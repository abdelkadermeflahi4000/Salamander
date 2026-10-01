from dataclasses import dataclass


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str
    requires_approval: bool = False
class ToolGuard:

    HIGH_RISK_TOOLS = {
        "send_email",
        "delete_file",
        "execute_shell",
        "transfer_money",
    }

    def check(self, call: ToolCall) -> ToolDecision:
        if call.name in self.HIGH_RISK_TOOLS:
            return ToolDecision(
                allowed=False,
                requires_approval=True,
                reason=f"High-risk tool: {call.name}",
            )

        return ToolDecision(
            allowed=True,
            reason="Tool allowed by policy",
        )
