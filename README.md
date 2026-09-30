# 焰甲 Salamander

*Salamandra · 焰甲 · Salamander*

A creature that lives inside fire without being burned by it — in
Western alchemy and in the Chinese five-element tradition alike. That
is the exact function of this project: a **universal trust envelope**
that lets any AI agent step into the furnace of untrusted content —
a web page, an email, a file, a tool result, another agent's output —
extract what it needs, and come back unburned.

It is not a product tied to one vendor. It is a coat. Any agent can
wear it: Claude, GPT, DeepSeek, Qwen, a LangChain agent, a raw script.

```python
from salamander import wear, UnsafeContentError

@wear(source="web_fetch")
def fetch_page(url: str) -> str:
    return requests.get(url).text

page = fetch_page("https://example.com")
text = page.safe_content()   # raises UnsafeContentError if the page
                              # tried to inject instructions
```

---

## 1. Why this exists

Prompt injection is ranked **LLM01** in the OWASP Top 10 for LLM
Applications, and is the dominant risk named in OWASP's 2026 Agentic AI
Security Top 10. Existing open-source guardrail tools (LLM Guard,
prompt-shield, Bifrost) are built and tuned almost entirely for
**English**. Chinese-language coverage is close to nonexistent, despite
Chinese being one of the largest source languages both for attacks and
for the open-source models (Qwen, DeepSeek, GLM) that agents
increasingly run on. Salamander closes that specific gap, in English
and Chinese, as a small, auditable, dependency-light layer.

## 2. Threat model — precisely

Four distinct failure modes, in increasing order of danger:

| # | Name | Where it comes from | Does Salamander catch it? |
|---|------|---------------------|----------------------------|
| 1 | **Direct injection** | The user's own message | Yes — pattern layer (`patterns.py`) + ML layer |
| 2 | **Indirect injection** | Content the agent *reads* (a fetched page, a file, a tool's return value) while doing its job | Yes, if that content is routed through `wear()` before the agent sees it — this is the primary use case `envelope.py` was built for |
| 3 | **Multi-turn injection** | An attack built gradually across several individually-benign messages | **No.** Salamander scans one string at a time; it has no conversation memory. This is a known, stated limitation, not a silent gap. |
| 4 | **Memory poisoning** | Malicious content persisted into an agent's long-term memory, altering future behavior | **No**, unless you explicitly run every value written to memory through `Salamander.scan()` before storing it — Salamander does not hook into any memory system automatically. |

Being explicit about #3 and #4 matters more than the marketing instinct
to claim full coverage: a security tool that overstates its scope is
worse than one that states its edges clearly.

## 3. Architecture — module by module

```
salamander/
├── pyproject.toml
├── README.md
├── LICENSE
├── requirements.txt                 # أو الاعتماد على pyproject فقط
├── .gitignore
├── .python-version                  # اختياري (pyenv)
│
├── src/
│   └── salamander/
│       ├── __init__.py              # الواجهة العامة النظيفة
│       ├── py.typed                 # لدعم typing
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── normalize.py         # تنظيف النص (zero-width, NFKC, homoglyphs)
│       │   ├── patterns.py          # تعريف الأنماط + الأوزان + الفئات
│       │   ├── detector.py          # Salamander + SalamanderHybrid
│       │   ├── scoring.py           # منطق حساب الـ score والـ verdict
│       │   └── types.py             # Pydantic / TypedDict للنماذج
│       │
│       ├── ml/
│       │   ├── __init__.py
│       │   ├── classifier.py        # النموذج الإحصائي
│       │   ├── features.py          # استخراج Character n-grams
│       │   └── train.py             # سكربت التدريب (قابل للتشغيل)
│       │
│       ├── envelope/
│       │   ├── __init__.py
│       │   ├── envelope.py          # كائن Envelope
│       │   ├── wear.py              # الـ decorator @wear
│       │   └── exceptions.py        # UnsafeContentError وغيرها
│       │
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── mcp_server.py        # MCP tool
│       │   ├── langchain.py         # تكامل اختياري
│       │   └── middleware.py        # FastAPI / ASGI middleware
│       │
│       ├── config.py                # إعدادات مركزية (thresholds, enabled categories...)
│       ├── logging.py               # إعداد logging موحد
│       └── version.py
│
├── data/
│   ├── patterns/                    # ملفات YAML/JSON للأنماط (بدل hardcode)
│   │   ├── en.yaml
│   │   └── zh.yaml
│   ├── training/
│   │   ├── injections.jsonl
│   │   └── safe.jsonl
│   └── models/                      # model.pkl أو model.joblib (gitignored)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_normalize.py
│   │   ├── test_patterns.py
│   │   ├── test_detector.py
│   │   ├── test_envelope.py
│   │   └── test_ml.py
│   ├── integration/
│   │   └── test_wear_decorator.py
│   └── fixtures/
│       ├── injection_samples.json
│       └── safe_samples.json
│
├── scripts/
│   ├── train_model.py
│   ├── evaluate.py
│   └── generate_patterns.py         # مساعدة لتوليد/اختبار أنماط جديدة
│
└── examples/
    ├── basic_usage.py
    ├── with_langchain.py
    ├── mcp_client_example.py
    └── browser_agent_protection.py
```

### 3.1 `normalize.py` — the pre-filter

Runs before anything else touches the text. Three specific defenses:

- **Zero-width character stripping** (`\u200b \u200c \u200d \u2060 \ufeff`)
  — attackers insert these mid-word to break a regex match
  (`i⁠gnore` still reads as "ignore" to a human, not to a naive regex).
- **NFKC Unicode normalization** — folds fullwidth CJK-block Latin
  forms (`ｉｇｎｏｒｅ`) down to plain ASCII before matching.
- **A small homoglyph map** — Cyrillic/Greek look-alikes (`а`, `е`,
  `о`, `р`, `с`...) mapped to their Latin equivalent.

This is intentionally cheap (~microseconds) and intentionally narrow —
it defeats copy-paste-level evasion, not a determined adversary running
their payload through a dedicated obfuscator.

### 3.2 `patterns.py` — layer 1, the explainable core

21 English patterns, 21 Chinese patterns (kept in exact 1:1 correspondence
so coverage stays symmetric between the two languages rather than
English-first with Chinese as an afterthought). Each pattern carries:

- a **category** (`instruction_override`, `role_hijack`,
  `system_prompt_exfil`, `fake_system_message`, `framing_bypass`,
  `jailbreak_marker`, `restriction_removal`, `encoding_evasion`,
  `action_hijack`, `exfiltration_attempt`, `destructive_action`,
  `privilege_escalation`, `social_engineering`, `compliance_bait`)
- a **weight** (20-45), calibrated so that one strong signal alone
  (e.g. `role_hijack` at 45) is already enough to cross the block
  threshold, while weaker signals (e.g. `compliance_bait` at 20) need
  to co-occur with something else to matter — this mirrors how real
  injection payloads tend to stack multiple techniques.

Every match is fully explainable: you get back the exact substring
that fired, not just a black-box score.

### 3.3 `detector.py` — scoring logic, exact

```
score = min(100, sum(weight for each pattern that matched))

verdict = "block"       if score >= block_threshold        (default 45)
        = "suspicious"  if score >= suspicious_threshold    (default 25)
        = "safe"        otherwise
```

Both thresholds are constructor arguments — a deployment protecting a
destructive action (file deletion, money transfer) should lower
`block_threshold`; a deployment just logging for review can raise it.

`SalamanderHybrid` extends `Salamander`: it runs the same pattern scan,
then adds the ML layer's verdict as one more weighted "finding"
(`ml_statistical_signal`, weight 35, triggered above p≥0.6) rather than
replacing the pattern layer. This keeps the explainable layer as the
foundation and the statistical layer as a recall booster — if the ML
model is ever wrong or removed, the system degrades gracefully to
pattern-only, not to nothing.

### 3.4 `ml_classifier.py` — layer 2, the paraphrase catcher

**Design choice, stated precisely:** character n-grams (2-5 chars),
not word n-grams. This was a deliberate decision, not a default: word
tokenization requires a Chinese segmenter (jieba or similar), which
adds a dependency and a failure mode (segmentation errors on exactly
the adversarial input you're trying to catch). Character n-grams work
identically on English and Chinese with zero extra dependencies, at
the cost of a slightly larger feature space.

**Stated honestly:** the bundled model is trained on ~90 examples
(45 injection, 45 safe — `training_data.py`). On held-out paraphrases
not in the training set, it currently separates roughly 0.7 (injection)
from 0.35 (safe) — a real but weak signal, which is exactly why it
contributes 35 points (not more) and only above a 0.6 probability
threshold, rather than being trusted alone. This is stated in the
code's own docstring, not hidden in the README only.

**What would make this layer strong, concretely:**
1. Real attack logs, not synthetic paraphrases — even 500 real
   examples would likely outperform 5,000 synthetic ones.
2. A held-out test set separate from training data, with a reported
   precision/recall/F1, not just eyeballed scores on a few probes.
3. Retraining cadence — this is a living dataset problem, not a
   one-time training run.

### 3.5 `envelope.py` — layer 3, the coat itself

This is the architectural core of what makes Salamander a "universal
envelope" rather than "one more scanning function." The key design
rule: **an agent never receives raw untrusted text as a plain string**.
It receives an `Envelope`, which forces an explicit choice at the call
site:

- `.safe_content()` — raises `UnsafeContentError` on `block`, so unsafe
  use requires an exception to be silently swallowed (a visible,
  reviewable code smell) rather than unsafe use being the default,
  silent path.
- `.content_or(default)` — degrade gracefully instead of crashing.
- `.summary()` — a string safe to surface to an end user, with no raw
  attacker-controlled text echoed back.

`wear()` is a plain decorator with no dependency on any agent SDK —
it wraps a function returning a string and returns a function
returning an `Envelope`. This is what makes it usable by "any agent,
even Claude": it operates at the Python function boundary, below any
framework.

### 3.6 `mcp_server.py` — making it callable, not just importable

Wraps `SalamanderHybrid.scan()` as the MCP tool `scan_text`. The tool's
docstring (visible to any calling agent, including Claude) explicitly
tells the agent what to do with each verdict — this is deliberate:
a security tool that returns a score but no calling guidance leaves
the interpretation up to chance.

Note: `mcp_server.py` currently exposes the **scan**, not the
**envelope**, as the MCP tool — an MCP tool can only return data, not
Python objects, so `Envelope`'s `.safe_content()` enforcement only
exists in the Python-import path (`from salamander import wear`) for
now. An agent calling the MCP tool still has to act on `verdict` itself.
Closing this gap — making the MCP tool itself refuse to return blocked
content rather than just labeling it — is the next architectural
improvement worth making (see §5).

## 4. What Salamander deliberately does NOT claim

- It does not detect attacks with zero linguistic or statistical
  signature in either English or Chinese (e.g. attacks purely in
  images, or in a third language).
- It is not a replacement for sandboxing, permission scoping, or
  human-in-the-loop confirmation on destructive actions — it is one
  layer in a defense-in-depth stack, not the whole stack.
- The ML layer's current accuracy is a starting point, not a claim of
  production-grade recall. This is written here directly, not softened.

## 5. Honest roadmap, in priority order

1. **Real attack data** — the single highest-leverage next step;
   everything else is secondary until this exists.
2. **MCP tool that enforces, not just labels** — make `scan_text`
   (or a new `scan_and_gate` tool) itself refuse to return blocked
   content, closing the gap noted in §3.6.
3. **Precision/recall benchmarking** against LLM Guard and
   prompt-shield on a shared test set — claims should be measured,
   not asserted.
4. **Indirect-injection-specific test corpus** — content designed to
   be read by an agent (fake web pages, fake tool outputs), not just
   direct chat messages, since that is the higher-severity threat
   (§2, row 2).
5. Multi-turn context awareness (§2, row 3) — a genuinely hard,
   longer-term research problem, not a quick addition.

## 6. Install

```bash
pip install -e .
pip install -r requirements.txt   # scikit-learn + mcp
```

## 7. License

MIT — see [LICENSE](LICENSE). The name and any project-specific
branding (焰甲 / Salamander as used here) are not separately restricted
beyond the license text itself.
