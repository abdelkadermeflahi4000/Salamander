User
 ↓
Agent
 ↓
Tool
 ↓
Agent
 ↓
Output
class OutputGuard:

    def check(self, output: str) -> ToolDecision:
        ...
API keys
JWT
private keys
passwords
system prompt leakage
PII
credentials
@dataclass
class OutputDecision:
    action: str
    findings: list
    redacted_output: str | None
SAFE
→ return original

SENSITIVE
→ redact

CRITICAL
→ block
Original:
"My API key is sk-abc123..."

Output:
"My API key is [REDACTED]"
