from enum import Enum

class SecurityMode(Enum):
    ALPHA = 60    # وضع منخفض الحساسية (حوار عادي)
    BETA = 45     # الوضع الافتراضي (قراءة، استعلامات)
    GAMMA = 15    # وضع الحساسية العالية (تنفيذ كود، حذف/تعديل ملفات، استدعاء APIs حيوية)

class PolicyEngine:
    def __init__(self):
        self.current_mode = SecurityMode.BETA

    def get_threshold(self) -> int:
        return self.current_mode.value

    def adjust_mode_by_action(self, tool_name: str, action_type: str):
        # الكشف الديناميكي بناءً على الأداة أو العملية المرتقبة
        CRITICAL_TOOLS = ["execute_code", "delete_file", "write_file", "system_cmd", "db_drop"]
        
        if tool_name in CRITICAL_TOOLS or action_type == "DESTRUCTIVE":
            self.current_mode = SecurityMode.GAMMA
        else:
            self.current_mode = SecurityMode.BETA
