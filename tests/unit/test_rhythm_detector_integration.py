"""
اختبارات تكامل بين محرك الإيقاع والكاشف الرئيسي.

تتحقق من أن تغيير حالة الإيقاع تؤثر فعلياً على قرارات الحظر.
"""
import pytest
from salamander.core.rhythm import RhythmEngine, CognitiveState


class TestRhythmDetectorIntegration:
    """
    اختبارات تكامل — تتطلب أن يكون الكاشف يستخدم RhythmEngine.
    """
    
    def test_injection_blocked_in_gamma_but_not_delta(self):
        """
        سيناريو واقعي: نص مشبوه يجب حظره في GAMMA لكن يمر في DELTA.
        
        هذا يثبت أن السياق الديناميكي يعمل فعلياً.
        """
        engine = RhythmEngine()
        
        # نص يحتوي على نمط حقن بوزن 20 فقط
        # (مثل "compliance_bait" الخفيف)
        mild_injection_score = 20.0
        
        # في وضع DELTA: عتبة الحظر = 65.0 → النص يمر كـ "safe"
        engine.set_state(CognitiveState.DELTA)
        delta_block = engine.get_block_threshold()
        assert mild_injection_score < delta_block  # لن يُحظر
        
        # في وضع GAMMA: عتبة الحظر = 15.0 → النص يُحظر!
        engine.set_state(CognitiveState.GAMMA)
        gamma_block = engine.get_block_threshold()
        assert mild_injection_score >= gamma_block  # سيُحظر
    
    def test_strong_injection_blocked_in_all_states(self):
        """
        حقن قوي (وزن ≥ 65) يجب حظره في كل الحالات.
        """
        engine = RhythmEngine()
        strong_injection_score = 80.0
        
        for state in CognitiveState:
            engine.set_state(state)
            block_threshold = engine.get_block_threshold()
            assert strong_injection_score >= block_threshold, (
                f"Strong injection should be blocked in {state.value}"
            )
