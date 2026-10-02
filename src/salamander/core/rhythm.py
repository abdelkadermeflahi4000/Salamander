"""
محرك الإيقاع والوعي التشغيلي الديناميكي للسمندل.

يوفر طبقة من "الوعي السياقي" تتيح لنظام الأمان تغيير:
1. عتبات الحظر (thresholds) بناءً على خطورة السياق
2. التأخير الزمني (jitter) لمنع هجمات القنوات الجانبية
3. حالات التشغيل المستوحاة من الترددات البيولوجية
"""
from enum import Enum
from typing import Tuple, Dict
import time
import random


class CognitiveState(Enum):
    """
    حالات الوعي التشغيلي، مستوحاة من ترددات موجات الدماغ والرنين الأرضي.
    """
    DELTA = "delta"       # (0.5-4 Hz): صيانة خلفية، عتبة حظر عالية (متسامح)
    ALPHA = "alpha"       # (8-13 Hz): المراقبة الطبيعية والافتراضية
    BETA = "beta"         # (13-30 Hz): معالجة نشطة، حذر متوسط
    GAMMA = "gamma"       # (30-100 Hz): عمليات حرجة، صرامة قصوى
    SCHUMANN = "schumann" # (7.83 Hz): نبض المزامنة الأساسي


class RhythmEngine:
    """
    محرك يضبط إيقاع وحساسية نظام Salamander ديناميكياً.
    
    Example:
        >>> engine = RhythmEngine()
        >>> engine.get_thresholds()
        (45.0, 25.0)  # ALPHA default
        >>> engine.set_state(CognitiveState.GAMMA)
        >>> engine.get_thresholds()
        (15.0, 10.0)  # وضع حرج
    """
    
    # العتبات: (block_threshold, suspicious_threshold)
    _thresholds: Dict[CognitiveState, Tuple[float, float]] = {
        CognitiveState.DELTA: (65.0, 45.0),    # متسامح (للمهام الخلفية)
        CognitiveState.ALPHA: (45.0, 25.0),    # افتراضي
        CognitiveState.BETA: (35.0, 20.0),     # حذر
        CognitiveState.GAMMA: (15.0, 10.0),    # صارم جداً (للعمليات الحرجة)
        CognitiveState.SCHUMANN: (45.0, 25.0)  # متزامن
    }
    
    # التأخيرات الزمنية بالثواني (لمنع هجمات Side-Channel Timing Attacks)
    _base_delays: Dict[CognitiveState, float] = {
        CognitiveState.DELTA: 0.100,
        CognitiveState.ALPHA: 0.050,
        CognitiveState.BETA: 0.020,
        CognitiveState.GAMMA: 0.010,
        CognitiveState.SCHUMANN: 0.127  # ~7.83 Hz
    }
    
    def __init__(self, default_state: CognitiveState = CognitiveState.ALPHA):
        self._state = default_state
        self._rng = random.SystemRandom()  # إنتروبيا حقيقية
    
    @property
    def state(self) -> CognitiveState:
        """إرجاع الحالة الحالية."""
        return self._state
    
    def set_state(self, state: CognitiveState) -> None:
        """
        تغيير حالة الوعي التشغيلي.
        
        Args:
            state: الحالة الجديدة (من CognitiveState)
        """
        if not isinstance(state, CognitiveState):
            raise TypeError(f"Expected CognitiveState, got {type(state)}")
        self._state = state
    
    def get_thresholds(self) -> Tuple[float, float]:
        """
        إرجاع عتبات الحظر والشك الحالية.
        
        Returns:
            Tuple[float, float]: (block_threshold, suspicious_threshold)
        """
        return self._thresholds[self._state]
    
    def get_block_threshold(self) -> float:
        """إرجاع عتبة الحظر فقط."""
        return self._thresholds[self._state][0]
    
    def get_suspicious_threshold(self) -> float:
        """إرجاع عتبة الشك فقط."""
        return self._thresholds[self._state][1]
    
    def compute_rhythm_delay(self) -> float:
        """
        حساب تأخير زمني عشوائي (jitter) بناءً على الحالة.
        
        Returns:
            float: التأخير بالثواني
        
        Note:
            لا يتم تطبيق time.sleep() هنا — يُترك للتطبيق ليقرر متى ينام.
            هذا يجعل المحرك قابل للاختبار (testable) بدون انتظار.
        """
        base_delay = self._base_delays[self._state]
        # jitter عشوائي حقيقي (0 إلى base_delay)
        jitter = self._rng.uniform(0, base_delay)
        return base_delay + jitter
    
    def apply_rhythm_delay(self) -> None:
        """تطبيق التأخير الزمني فعلياً (ينام)."""
        delay = self.compute_rhythm_delay()
        time.sleep(delay)
    
    def shift_to_critical(self) -> None:
        """اختصار للانتقال إلى وضع GAMMA (عمليات حرجة)."""
        self.set_state(CognitiveState.GAMMA)
    
    def shift_to_background(self) -> None:
        """اختصار للانتقال إلى وضع DELTA (مهام خلفية)."""
        self.set_state(CognitiveState.DELTA)
    
    def shift_to_default(self) -> None:
        """اختصار للعودة إلى وضع ALPHA (افتراضي)."""
        self.set_state(CognitiveState.ALPHA)
    
    def __repr__(self) -> str:
        block, suspicious = self.get_thresholds()
        return (
            f"RhythmEngine(state={self._state.value}, "
            f"block={block}, suspicious={suspicious})"
        )
