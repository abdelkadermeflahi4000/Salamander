# src/salamander/rhythm.py
import time
import random
from enum import Enum
from typing import Tuple

class CognitiveState(Enum):
    """حالات الوعي التشغيلي للسمندل، مستوحاة من الترددات البيولوجية والفيزيائية"""
    DELTA = "delta"       # (0.5-4 Hz): صيانة خلفية، عتبة حظر عالية (متسامح مع الضوضاء)
    ALPHA = "alpha"       # (8-13 Hz): وضع المراقبة الطبيعي والافتراضي
    BETA = "beta"         # (13-30 Hz): معالجة نشطة، عتبة حظر متوسطة (حذر)
    GAMMA = "gamma"       # (30-100 Hz): عملية حرجة (مثل تنفيذ أداة)، عتبة حظر منخفضة جداً (صارم)
    SCHUMANN = "schumann" # (7.83 Hz): نبض المزامنة الأساسي بين الوكلاء

class RhythmEngine:
    """
    محرك يضبط إيقاع وحساسية نظام Salamander ديناميكياً.
    يضيف طبقة من "الوعي السياقي" للأمان.
    """
    def __init__(self, default_state: CognitiveState = CognitiveState.ALPHA):
        self.state = default_state
        
        # العتبات: (block_threshold, suspicious_threshold)
        self._thresholds = {
            CognitiveState.DELTA: (65.0, 45.0),    # متسامح
            CognitiveState.ALPHA: (45.0, 25.0),    # افتراضي (كما في config.py الأصلي)
            CognitiveState.BETA: (35.0, 20.0),     # حذر
            CognitiveState.GAMMA: (15.0, 10.0),    # صارم جداً (Paranoid)
            CognitiveState.SCHUMANN: (45.0, 25.0)  # متزامن
        }
        
        # التأخيرات الزمنية بالثواني (لمنع هجمات قياس التوقيت Side-Channel Timing Attacks)
        self._base_delays = {
            CognitiveState.DELTA: 0.100,
            CognitiveState.ALPHA: 0.050,
            CognitiveState.BETA: 0.020,
            CognitiveState.GAMMA: 0.010,
            CognitiveState.SCHUMANN: 0.127  # ~7.83 Hz
        }

    def set_state(self, state: CognitiveState):
        """تغيير حالة الوعي التشغيلي"""
        self.state = state

    def get_thresholds(self) -> Tuple[float, float]:
        """إرجاع عتبات الحظر والشك الحالية بناءً على الحالة"""
        return self._thresholds[self.state]

    def apply_rhythm_delay(self):
        """
        تطبيق تأخير زمني عشوائي (Jitter).
        هذا يمنع المهاجمين من استخدام 'هجمات القناة الجانبية' لاستنتاج 
        أي الأنماط تم تفعيلها بناءً على سرعة استجابة النظام.
        """
        base_delay = self._base_delays[self.state]
        # إضافة عشوائية حقيقية (Quantum-inspired jitter)
        jitter = random.SystemRandom().uniform(0, base_delay)
        time.sleep(base_delay + jitter)
