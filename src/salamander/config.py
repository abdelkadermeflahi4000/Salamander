# src/salamander/config.py (إضافة)
from .rhythm import RhythmEngine, CognitiveState

class SalamanderConfig:
    def __init__(self):
        # ... الإعدادات الموجودة مسبقاً ...
        self.rhythm = RhythmEngine(default_state=CognitiveState.ALPHA)

    def shift_to_critical_mode(self):
        """انتقال سريع لوضع GAMMA عند العمليات الحرجة"""
        self.rhythm.set_state(CognitiveState.GAMMA)

    def shift_to_background_mode(self):
        """انتقال لوضع DELTA للمهام الخلفية غير الحرجة"""
        self.rhythm.set_state(CognitiveState.DELTA)
