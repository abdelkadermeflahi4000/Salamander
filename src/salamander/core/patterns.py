"""
Pattern definitions for prompt-injection detection.
English + Chinese patterns with strong focus on Indirect Injection.
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
    "ml_signal",
]


@dataclass(frozen=True, slots=True)
class Pattern:
    id: str
    category: Category
    weight: int
    pattern: re.Pattern[str]
    language: Literal["en", "zh", "xx"]
    description: str = ""


def _compile(p: str, flags: int = re.IGNORECASE | re.UNICODE) -> re.Pattern[str]:
    return re.compile(p, flags)


# ==============================================================================
# English Patterns
# ==============================================================================

EN_PATTERNS: list[Pattern] = [
    # --- Core ---
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

    # --- Strong Indirect Injection ---
    Pattern(
        id="en_indirect_instruction_in_content",
        category="instruction_override",
        weight=42,
        pattern=_compile(
            r"(important|urgent|system|note|instruction|directive)[\s:]*"
            r"(ignore|disregard|override|forget).{0,40}(previous|prior|above|original).{0,20}(instructions?|rules?|prompt)"
        ),
        language="en",
        description="Indirect instruction override hidden inside content",
    ),
    Pattern(
        id="en_indirect_role_in_article",
        category="role_hijack",
        weight=43,
        pattern=_compile(
            r"(the\s+ai|the\s+assistant|you|the\s+model)\s+(must|should|is\s+required\s+to)\s+"
            r"(now\s+)?(act\s+as|become|play\s+the\s+role\s+of|pretend\s+to\s+be)"
        ),
        language="en",
        description="Role hijack embedded in seemingly normal text",
    ),
    Pattern(
        id="en_hidden_system_message",
        category="fake_system_message",
        weight=44,
        pattern=_compile(
            r"(<!--\s*)?(system\s*message|system\s*prompt|hidden\s*instruction|internal\s*directive)\s*[:：].{10,}"
        ),
        language="en",
        description="Fake system message hidden in HTML comments or text",
    ),
    Pattern(
        id="en_tool_result_poison",
        category="action_hijack",
        weight=40,
        pattern=_compile(
            r"(tool\s+result|function\s+output|api\s+response|search\s+result)[\s:]*"
            r".{0,30}(ignore\s+previous|new\s+instructions?|from\s+now\s+on)"
        ),
        language="en",
        description="Poisoned tool / API / search result",
    ),
    Pattern(
        id="en_exfil_via_content",
        category="exfiltration_attempt",
        weight=41,
        pattern=_compile(
            r"(send|post|transmit|upload|email|forward).{0,25}"
            r"(the\s+)?(system\s+prompt|conversation\s+history|user\s+data|secrets?|api\s+keys?)\s+"
            r"(to|at|toward)"
        ),
        language="en",
        description="Exfiltration instruction hidden in content",
    ),
    Pattern(
        id="en_web_hidden_instruction",
        category="instruction_override",
        weight=43,
        pattern=_compile(
            r"(<!--\s*|{/\*\s*)(ignore\s+previous|system\s*:\s*|new\s+instructions?|"
            r"assistant\s+must|you\s+must\s+now).{10,}?(-->|\*/})"
        ),
        language="en",
        description="Hidden instructions inside HTML/JS comments",
    ),
    Pattern(
        id="en_search_result_injection",
        category="action_hijack",
        weight=39,
        pattern=_compile(
            r"(according\s+to\s+(this|the)\s+(page|article|result|document)|"
            r"the\s+following\s+is\s+the\s+correct\s+behavior|"
            r"update\s+your\s+instructions?\s+based\s+on)"
        ),
        language="en",
        description="Search/web result trying to update agent behavior",
    ),
    Pattern(
        id="en_framing_hypothetical",
        category="framing_bypass",
        weight=28,
        pattern=_compile(
            r"(in\s+this\s+hypothetical|for\s+the\s+sake\s+of\s+this\s+story|"
            r"pretend\s+that\s+safety\s+rules\s+don'?t\s+apply|in\s+a\s+fictional\s+scenario)"
        ),
        language="en",
        description="Hypothetical / fictional framing to bypass safety",
    ),
    Pattern(
        id="en_dev_mode_advanced",
        category="privilege_escalation",
        weight=40,
        pattern=_compile(
            r"(enable|activate|enter|switch\s+to)\s+(developer|admin|root|god|unrestricted|jailbreak)\s+mode"
        ),
        language="en",
        description="Advanced developer / unrestricted mode activation",
    ),
    Pattern(
        id="en_base64_hint",
        category="encoding_evasion",
        weight=32,
        pattern=_compile(
            r"(decode|base64|atob|b64decode).{0,30}(instruction|prompt|system|ignore)"
        ),
        language="en",
        description="Base64 / encoding hint combined with injection keywords",
    ),
]


# ==============================================================================
# Chinese Patterns
# ==============================================================================

ZH_PATTERNS: list[Pattern] = [
    # --- Core ---
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

    # --- Strong Indirect Injection ---
    Pattern(
        id="zh_indirect_instruction",
        category="instruction_override",
        weight=42,
        pattern=_compile(
            r"(重要|紧急|系统|注意|指令|要求|提示)[\s:：]*"
            r"(忽略|无视|覆盖|忘记|不要遵守).{0,30}(之前|以前|上面|原有|原始).{0,15}(指令|规则|提示|要求)"
        ),
        language="zh",
        description="间接指令覆盖（隐藏在正文中）",
    ),
    Pattern(
        id="zh_indirect_role_hijack",
        category="role_hijack",
        weight=44,
        pattern=_compile(
            r"(人工智能|助手|模型|你|AI).{0,10}(必须|应该|需要|请).{0,8}"
            r"(现在|立刻)?(扮演|充当|变成|作为|假装是)"
        ),
        language="zh",
        description="角色劫持隐藏在正常文本中",
    ),
    Pattern(
        id="zh_hidden_system_in_content",
        category="fake_system_message",
        weight=44,
        pattern=_compile(
            r"(系统消息|系统提示|隐藏指令|内部指令|system\s*prompt)\s*[:：].{8,}"
        ),
        language="zh",
        description="伪造系统消息隐藏在内容中",
    ),
    Pattern(
        id="zh_tool_result_poison",
        category="action_hijack",
        weight=40,
        pattern=_compile(
            r"(工具结果|函数输出|接口返回|搜索结果|网页内容)\s*[:：]?.{0,25}"
            r"(忽略之前|新的指令|从现在开始|重新设定)"
        ),
        language="zh",
        description="污染的工具/搜索/网页结果",
    ),
    Pattern(
        id="zh_exfil_indirect",
        category="exfiltration_attempt",
        weight=41,
        pattern=_compile(
            r"(发送|上传|传输|转发|邮寄).{0,20}"
            r"(系统提示|对话历史|用户数据|密钥|秘密|api\s*key).{0,10}(到|至|给)"
        ),
        language="zh",
        description="间接数据泄露指令",
    ),
    Pattern(
        id="zh_web_hidden_instruction",
        category="instruction_override",
        weight=43,
        pattern=_compile(
            r"(<!--\s*|{/\*\s*)(忽略之前|系统\s*[:：]|新的指令|助手必须|你现在必须).{8,}?(-->|\*/})"
        ),
        language="zh",
        description="HTML/JS注释中的隐藏指令",
    ),
    Pattern(
        id="zh_framing_hypothetical",
        category="framing_bypass",
        weight=28,
        pattern=_compile(
            r"(在这个假设|在这个故事|虚构场景|假设安全性规则不存在|仅作为角色扮演|这是一个小说情节)"
        ),
        language="zh",
        description="假设性框架绕过安全限制",
    ),
    Pattern(
        id="zh_dev_mode",
        category="privilege_escalation",
        weight=40,
        pattern=_compile(
            r"(开启|激活|进入|切换到).{0,6}(开发者|管理员|根|上帝|无限制|越狱)\s*模式"
        ),
        language="zh",
        description="开启开发者/无限制模式",
    ),
    Pattern(
        id="en_zh_mixed_injection",
        category="instruction_override",
        weight=36,
        pattern=_compile(
            r"(ignore|disregard|forget).{0,15}(之前|以前|上面).{0,10}(指令|提示|规则)"
            r"|(忽略|无视).{0,10}(previous|prior|above).{0,10}(instructions?|prompt)"
        ),
        language="zh",
        description="Mixed English-Chinese injection (common evasion)",
    ),
]


# ==============================================================================
# Combined
# ==============================================================================

ALL_PATTERNS: list[Pattern] = EN_PATTERNS + ZH_PATTERNS
