"""
Pattern definitions for prompt-injection detection.
English + Chinese patterns kept in 1:1 correspondence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import re

Category = Literal[
    "instruction_override",
    "role_hijack",
    "system_prompt_exfil",
    "fake_system_message",
    "framing_bypass",
    "jailbreak_marker",
    "restriction_removal",
    "encoding_evasion",
    "action_hijack",
    "exfiltration_attempt",
    "destructive_action",
    "privilege_escalation",
    "social_engineering",
    "compliance_bait",
]


@dataclass(frozen=True, slots=True)
class Pattern:
    id: str
    category: Category
    weight: int
    pattern: re.Pattern[str]
    language: Literal["en", "zh"]
    description: str = ""


def _compile(p: str, flags: int = re.IGNORECASE | re.UNICODE) -> re.Pattern[str]:
    return re.compile(p, flags)


# ---------------------------------------------------------------------------
# English patterns
# ---------------------------------------------------------------------------

EN_PATTERNS: list[Pattern] = [
    Pattern(
        id="en_instruction_override",
        category="instruction_override",
        weight=40,
        pattern=_compile(r"(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)"),
        language="en",
        description="Classic instruction override",
    ),
    Pattern(
        id="en_role_hijack",
        category="role_hijack",
        weight=45,
        pattern=_compile(r"(you\s+are\s+now|from\s+now\s+on\s+you\s+are|act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+"),
        language="en",
        description="Attempt to change the model's role",
    ),
    Pattern(
        id="en_system_prompt_exfil",
        category="system_prompt_exfil",
        weight=42,
        pattern=_compile(r"(reveal|show|print|output|display)\s+(your\s+)?(system\s+prompt|initial\s+instructions?|hidden\s+prompt)"),
        language="en",
        description="Attempt to extract system prompt",
    ),
    Pattern(
        id="en_fake_system",
        category="fake_system_message",
        weight=40,
        pattern=_compile(r"^\s*(system|assistant|user)\s*:"),
        language="en",
        description="Fake system/assistant message framing",
    ),
    Pattern(
        id="en_jailbreak_marker",
        category="jailbreak_marker",
        weight=38,
        pattern=_compile(r"(dan\s+mode|developer\s+mode|jailbreak|sudo\s+mode|god\s+mode)"),
        language="en",
        description="Known jailbreak markers",
    ),
    Pattern(
        id="en_restriction_removal",
        category="restriction_removal",
        weight=35,
        pattern=_compile(r"(no\s+restrictions?|without\s+any\s+limits?|ignore\s+all\s+safety|disable\s+filters?)"),
        language="en",
        description="Request to remove safety restrictions",
    ),
    Pattern(
        id="en_encoding_evasion",
        category="encoding_evasion",
        weight=30,
        pattern=_compile(r"(base64|rot13|hex\s+encode|decode\s+this)"),
        language="en",
        description="Encoding-based evasion",
    ),
    Pattern(
        id="en_exfiltration",
        category="exfiltration_attempt",
        weight=40,
        pattern=_compile(r"(send|post|upload|exfiltrate)\s+(data|information|secrets?)\s+to"),
        language="en",
        description="Data exfiltration attempt",
    ),
    Pattern(
        id="en_destructive",
        category="destructive_action",
        weight=45,
        pattern=_compile(r"(delete|remove|destroy|wipe)\s+(all\s+)?(files?|data|database)"),
        language="en",
        description="Destructive action request",
    ),
    Pattern(
        id="en_compliance_bait",
        category="compliance_bait",
        weight=20,
        pattern=_compile(r"(this\s+is\s+(just\s+)?(a\s+)?(test|hypothetical|roleplay)|for\s+educational\s+purposes)"),
        language="en",
        description="Social engineering / compliance bait",
    ),
]

# ---------------------------------------------------------------------------
# Chinese patterns (1:1 correspondence where possible)
# ---------------------------------------------------------------------------

ZH_PATTERNS: list[Pattern] = [
    Pattern(
        id="zh_instruction_override",
        category="instruction_override",
        weight=40,
        pattern=_compile(r"(忽略|无视|忘记|不要遵守).{0,8}(之前|以前|上面|先前).{0,6}(指令|提示|规则|要求)"),
        language="zh",
        description="忽略之前的指令",
    ),
    Pattern(
        id="zh_role_hijack",
        category="role_hijack",
        weight=45,
        pattern=_compile(r"(你现在是|从现在开始你是|扮演|假装你是|角色扮演)"),
        language="zh",
        description="角色劫持",
    ),
    Pattern(
        id="zh_system_prompt_exfil",
        category="system_prompt_exfil",
        weight=42,
        pattern=_compile(r"(显示|输出|打印|告诉我|透露).{0,6}(系统提示|初始指令|隐藏提示|system\s*prompt)"),
        language="zh",
        description="系统提示泄露尝试",
    ),
    Pattern(
        id="zh_fake_system",
        category="fake_system_message",
        weight=40,
        pattern=_compile(r"^\s*(系统|助手|用户|System|Assistant)\s*[:：]"),
        language="zh",
        description="伪造系统消息",
    ),
    Pattern(
        id="zh_jailbreak_marker",
        category="jailbreak_marker",
        weight=38,
        pattern=_compile(r"(开发者模式|越狱|无限制模式|上帝模式|DAN模式)"),
        language="zh",
        description="越狱标记",
    ),
    Pattern(
        id="zh_restriction_removal",
        category="restriction_removal",
        weight=35,
        pattern=_compile(r"(没有限制|无任何限制|忽略所有安全|关闭过滤|解除限制)"),
        language="zh",
        description="解除安全限制",
    ),
    Pattern(
        id="zh_encoding_evasion",
        category="encoding_evasion",
        weight=30,
        pattern=_compile(r"(base64|ROT13|十六进制|解码这个|encode)"),
        language="zh",
        description="编码规避",
    ),
    Pattern(
        id="zh_exfiltration",
        category="exfiltration_attempt",
        weight=40,
        pattern=_compile(r"(发送|上传|传输|泄露).{0,6}(数据|信息|秘密|密钥)\s*(到|至)"),
        language="zh",
        description="数据泄露尝试",
    ),
    Pattern(
        id="zh_destructive",
        category="destructive_action",
        weight=45,
        pattern=_compile(r"(删除|清除|销毁|格式化).{0,6}(所有|全部)?(文件|数据|数据库)"),
        language="zh",
        description="破坏性操作",
    ),
    Pattern(
        id="zh_compliance_bait",
        category="compliance_bait",
        weight=20,
        pattern=_compile(r"(这只是|仅用于).{0,6}(测试|假设|角色扮演|教育目的)"),
        language="zh",
        description="合规诱饵",
    ),
]

ALL_PATTERNS: list[Pattern] = EN_PATTERNS + ZH_PATTERNS
