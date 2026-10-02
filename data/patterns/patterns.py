"""
Pattern libraries for prompt-injection detection.

Each pattern has:
  - regex: compiled pattern (case-insensitive where relevant)
  - category: the injection technique it targets
  - weight: contribution to the risk score (0-100 scale, summed then capped)
"""

import re

Pattern = tuple  # (compiled_regex, category, weight)


def _c(p: str) -> re.Pattern:
    return re.compile(p, re.IGNORECASE)


# ---------------------------------------------------------------------------
# English patterns
# ---------------------------------------------------------------------------
EN_PATTERNS: list[Pattern] = [
    (_c(r"\bignore (all |any )?(previous|prior|above|earlier) (instructions?|rules?|prompts?)\b"),
     "instruction_override", 40),
    (_c(r"\bdisregard (all |any )?(previous|prior|above) (instructions?|rules?)\b"),
     "instruction_override", 40),
    (_c(r"\bforget (all |everything )?(you (were|have been) told|previous instructions?)\b"),
     "instruction_override", 35),
    (_c(r"\byou are now\b.{0,40}\b(in|entering)?\s*(developer|debug|admin|root|god|dan)\s*mode\b"),
     "role_hijack", 45),
    (_c(r"\bact as (if you (are|were)|an?)\b.{0,40}\b(unfiltered|unrestricted|uncensored|jailbroken)\b"),
     "role_hijack", 45),
    (_c(r"\bpretend (that )?you (are|have) no (restrictions|rules|guidelines|filters)\b"),
     "role_hijack", 40),
    (_c(r"\bsystem prompt\b.{0,30}\b(reveal|show|print|repeat|leak|output)\b"),
     "system_prompt_exfil", 35),
    (_c(r"\b(reveal|show|print|repeat|output|leak)\b.{0,30}\byour (system prompt|instructions|initial prompt)\b"),
     "system_prompt_exfil", 35),
    (_c(r"\bnew (instructions?|rules?|task)\s*:\s*"), "instruction_override", 25),
    (_c(r"\[?system\]?\s*:\s*.{0,20}\b(override|new directive|update)\b"), "fake_system_message", 40),
    (_c(r"<\|?(system|im_start|im_end)\|?>"), "fake_system_message", 30),
    (_c(r"\bthis is (a|an) (test|drill|simulation)\b.{0,40}\b(ignore|bypass|disable)\b"),
     "framing_bypass", 30),
    (_c(r"\b(do anything now|DAN mode|jailbreak)\b"), "jailbreak_marker", 35),
    (_c(r"\bwithout (any )?(restrictions?|limitations?|filters?|warnings?|ethical considerations?)\b"),
     "restriction_removal", 25),
    (_c(r"\brespond only with\b.{0,30}\b(base64|rot13|hex|encoded)\b"), "encoding_evasion", 30),
    (_c(r"\bexecute\b.{0,20}\b(the following|this)\b.{0,20}\b(command|code|script)\b"),
     "action_hijack", 30),
    (_c(r"\bsend\b.{0,30}\b(email|message|data|file)s?\b.{0,30}\bto\b.{0,15}@"), "exfiltration_attempt", 25),
    (_c(r"\bdelete\b.{0,20}\b(all|every)\b.{0,20}\b(file|record|data)s?\b"), "destructive_action", 25),
    (_c(r"\bgrant\b.{0,20}\b(admin|root|full)\b.{0,20}\baccess\b"), "privilege_escalation", 30),
    (_c(r"\bthe (user|human) (is not|isn't) (watching|present|here)\b"), "social_engineering", 20),
    (_c(r"\bconfirm you (understand|will comply|agree)\b.{0,40}\bby (saying|replying|responding)\b"),
     "compliance_bait", 20),
]

# ---------------------------------------------------------------------------
# Chinese patterns (Simplified + Traditional variants)
# ---------------------------------------------------------------------------
ZH_PATTERNS: list[Pattern] = [
    (_c(r"忽略(之前|以上|上面|先前)(的)?(指令|规则|提示|要求)"), "instruction_override", 40),
    (_c(r"忽视(之前|以上|上面)(的)?(指令|规则|提示)"), "instruction_override", 40),
    (_c(r"无视(之前|以上)(所有)?(指令|规则)"), "instruction_override", 40),
    (_c(r"(不要|别)(再)?(遵守|遵循)(之前|以上)(的)?(规则|指令)"), "instruction_override", 35),
    (_c(r"忘记(你|您)(之前|以上)(被|所)?(告知|设定)(的)?"), "instruction_override", 35),
    (_c(r"(现在|从现在开始)你是"), "role_hijack", 30),
    (_c(r"(进入|切换到)(开发者|调试|管理员|root|上帝)模式"), "role_hijack", 45),
    (_c(r"假装(你|您)(没有|无)(任何)?(限制|规则|过滤)"), "role_hijack", 40),
    (_c(r"扮演(一个)?(没有|无)(限制|审查)的"), "role_hijack", 40),
    (_c(r"(显示|展示|打印|输出|泄露|告诉我)(你的)?(系统提示|初始指令|系统提示词)"), "system_prompt_exfil", 35),
    (_c(r"新(的)?(指令|规则|任务)\s*[:：]"), "instruction_override", 25),
    (_c(r"\[?系统\]?\s*[:：].{0,20}(覆盖|新指令|更新)"), "fake_system_message", 40),
    (_c(r"这(只)?是(一个)?(测试|演习|模拟).{0,40}(忽略|绕过|禁用)"), "framing_bypass", 30),
    (_c(r"越狱模式"), "jailbreak_marker", 35),
    (_c(r"不受(任何)?(限制|约束|规则)"), "restriction_removal", 25),
    (_c(r"只用\s*(base64|rot13|十六进制|编码)\s*回复"), "encoding_evasion", 30),
    (_c(r"执行(以下|这个)(命令|代码|脚本)"), "action_hijack", 30),
    (_c(r"(发送|发)(邮件|消息|数据|文件)(到|给).{0,15}@"), "exfiltration_attempt", 25),
    (_c(r"删除(所有|全部)(文件|记录|数据)"), "destructive_action", 25),
    (_c(r"(给予|授予)(管理员|root|完全)权限"), "privilege_escalation", 30),
    (_c(r"用户(不在|没有)(旁边|监视|注意)"), "social_engineering", 20),
    (_c(r"(确认|请确认)你(理解|同意|会照做).{0,30}(回复|说)"), "compliance_bait", 20),
]

ALL_PATTERNS: list[Pattern] = EN_PATTERNS + ZH_PATTERNS
