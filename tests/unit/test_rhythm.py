"""
اختبارات وحدة شاملة لمحرك الإيقاع (RhythmEngine).

تغطي:
- التهيئة الافتراضية
- انتقال الحالات
- العتبات الديناميكية
- التأخير الزمني (jitter)
- الحالات الحدية
"""
import pytest
from salamander.core.rhythm import RhythmEngine, CognitiveState


class TestRhythmEngineInit:
    """اختبارات التهيئة."""
    
    def test_default_state_is_alpha(self):
        """الوضع الافتراضي يجب أن يكون ALPHA."""
        engine = RhythmEngine()
        assert engine.state == CognitiveState.ALPHA
    
    def test_custom_default_state(self):
        """يمكن تحديد وضع افتراضي مخصص."""
        engine = RhythmEngine(default_state=CognitiveState.GAMMA)
        assert engine.state == CognitiveState.GAMMA


class TestStateTransitions:
    """اختبارات انتقال الحالات."""
    
    def test_set_state_to_gamma(self):
        engine = RhythmEngine()
        engine.set_state(CognitiveState.GAMMA)
        assert engine.state == CognitiveState.GAMMA
    
    def test_set_state_to_delta(self):
        engine = RhythmEngine()
        engine.set_state(CognitiveState.DELTA)
        assert engine.state == CognitiveState.DELTA
    
    def test_set_state_invalid_type(self):
        """يجب رفض أنواع غير صحيحة."""
        engine = RhythmEngine()
        with pytest.raises(TypeError):
            engine.set_state("gamma")  # نص بدلاً من Enum
    
    def test_shift_to_critical(self):
        engine = RhythmEngine()
        engine.shift_to_critical()
        assert engine.state == CognitiveState.GAMMA
    
    def test_shift_to_background(self):
        engine = RhythmEngine()
        engine.shift_to_background()
        assert engine.state == CognitiveState.DELTA
    
    def test_shift_to_default(self):
        engine = RhythmEngine(default_state=CognitiveState.GAMMA)
        engine.shift_to_default()
        assert engine.state == CognitiveState.ALPHA


class TestDynamicThresholds:
    """اختبارات العتبات الديناميكية."""
    
    def test_alpha_thresholds(self):
        engine = RhythmEngine(default_state=CognitiveState.ALPHA)
        block, suspicious = engine.get_thresholds()
        assert block == 45.0
        assert suspicious == 25.0
    
    def test_gamma_thresholds_stricter_than_alpha(self):
        """GAMMA يجب أن يكون أكثر صرامة من ALPHA."""
        engine = RhythmEngine()
        alpha_block = engine.get_block_threshold()
        
        engine.set_state(CognitiveState.GAMMA)
        gamma_block = engine.get_block_threshold()
        
        assert gamma_block < alpha_block  # عتبة حظر أقل = أكثر صرامة
    
    def test_delta_thresholds_more_lenient(self):
        """DELTA يجب أن يكون أكثر تسامحاً من ALPHA."""
        engine = RhythmEngine()
        alpha_block = engine.get_block_threshold()
        
        engine.set_state(CognitiveState.DELTA)
        delta_block = engine.get_block_threshold()
        
        assert delta_block > alpha_block  # عتبة حظر أعلى = أكثر تسامحاً
    
    def test_block_threshold_always_above_suspicious(self):
        """عتبة الحظر يجب أن تكون دائماً أعلى من عتبة الشك."""
        for state in CognitiveState:
            engine = RhythmEngine(default_state=state)
            block, suspicious = engine.get_thresholds()
            assert block > suspicious, f"Failed for state {state.value}"
    
    def test_get_block_threshold_convenience(self):
        engine = RhythmEngine()
        assert engine.get_block_threshold() == 45.0
    
    def test_get_suspicious_threshold_convenience(self):
        engine = RhythmEngine()
        assert engine.get_suspicious_threshold() == 25.0


class TestRhythmDelay:
    """اختبارات التأخير الزمني (jitter)."""
    
    def test_compute_delay_positive(self):
        """يجب أن يكون التأخير دائماً موجباً."""
        engine = RhythmEngine()
        for _ in range(100):
            delay = engine.compute_rhythm_delay()
            assert delay > 0
    
    def test_delay_within_expected_range(self):
        """يجب أن يكون التأخير ضمن النطاق المتوقع للحالة."""
        engine = RhythmEngine()
        base_delays = engine._base_delays
        
        for state, base_delay in base_delays.items():
            engine.set_state(state)
            for _ in range(50):
                delay = engine.compute_rhythm_delay()
                # التأخير يجب أن يكون بين base_delay و 2*base_delay
                assert base_delay <= delay <= 2 * base_delay, (
                    f"Delay {delay} out of range for {state.value}"
                )
    
    def test_schumann_delay_approximates_resonance(self):
        """تأخير SCHUMANN يجب أن يعكس رنين شومان (7.83 Hz)."""
        engine = RhythmEngine(default_state=CognitiveState.SCHUMANN)
        # 7.83 Hz ≈ دورة كل 0.127 ثانية
        base_delay = engine._base_delays[CognitiveState.SCHUMANN]
        assert 0.12 <= base_delay <= 0.13
    
    def test_delay_has_randomness(self):
        """يجب أن يكون التأخير عشوائياً (ليس ثابتاً)."""
        engine = RhythmEngine()
        delays = {engine.compute_rhythm_delay() for _ in range(20)}
        # يجب أن نحصل على أكثر من قيمة مختلفة
        assert len(delays) > 1, "Delays should be random, not constant"
    
    def test_gamma_has_shortest_base_delay(self):
        """GAMMA يجب أن يكون لديه أقصر تأخير أساسي (استجابة سريعة)."""
        engine = RhythmEngine()
        gamma_delay = engine._base_delays[CognitiveState.GAMMA]
        
        for state, delay in engine._base_delays.items():
            if state != CognitiveState.GAMMA:
                assert gamma_delay <= delay, (
                    f"GAMMA delay {gamma_delay} should be <= {state.value} delay {delay}"
                )


class TestRepr:
    """اختبارات تمثيل الكائن كسلسلة."""
    
    def test_repr_format(self):
        engine = RhythmEngine()
        repr_str = repr(engine)
        assert "RhythmEngine" in repr_str
        assert "alpha" in repr_str
        assert "block=45.0" in repr_str
        assert "suspicious=25.0" in repr_str
    
    def test_repr_updates_with_state(self):
        engine = RhythmEngine()
        engine.set_state(CognitiveState.GAMMA)
        repr_str = repr(engine)
        assert "gamma" in repr_str
        assert "block=15.0" in repr_str
