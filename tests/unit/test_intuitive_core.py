"""
اختبارات وحدة للكائن الرقمي الحدسي.
"""
import pytest
import time
from salamander.intuitive.intuitive_core import (
    IntuitiveDigitalEntity,
    ResponseType,
    IntuitiveState
)


class TestAnxietyDynamics:
    """اختبارات ديناميكيات القلق."""
    
    def test_initial_anxiety(self):
        entity = IntuitiveDigitalEntity(initial_anxiety=0.1)
        assert 0.09 <= entity.anxiety_index <= 0.11
    
    def test_anxiety_increases_on_suspicious_event(self):
        entity = IntuitiveDigitalEntity(initial_anxiety=0.1)
        initial = entity.anxiety_index
        entity.update_internal_state(is_suspicious=True, entropy=5.0)
        assert entity.anxiety_index > initial
    
    def test_anxiety_decays_over_time(self):
        entity = IntuitiveDigitalEntity(initial_anxiety=0.5)
        entity.update_internal_state(is_suspicious=True, entropy=5.0)
        high_anxiety = entity.anxiety_index
        
        # محاكاة مرور الوقت (بتعديل _last_attack_time مباشرة)
        entity._last_attack_time -= 600  # 10 دقائق في الماضي
        
        decayed = entity.anxiety_index
        assert decayed < high_anxiety
    
    def test_anxiety_bounded_at_one(self):
        entity = IntuitiveDigitalEntity(initial_anxiety=0.9)
        for _ in range(100):
            entity.update_internal_state(is_suspicious=True, entropy=8.0, threat_score=100)
        assert entity.anxiety_index <= 1.0


class TestDynamicThreshold:
    """اختبارات العتبة الديناميكية."""
    
    def test_threshold_decreases_with_anxiety(self):
        entity = IntuitiveDigitalEntity(base_threshold=45)
        baseline = entity.generate_dynamic_threshold()
        
        # رفع القلق
        for _ in range(10):
            entity.update_internal_state(is_suspicious=True, entropy=6.0, threat_score=50)
        
        anxious_threshold = entity.generate_dynamic_threshold()
        assert anxious_threshold < baseline
    
    def test_threshold_has_jitter(self):
        entity = IntuitiveDigitalEntity()
        thresholds = {entity.generate_dynamic_threshold() for _ in range(20)}
        # يجب أن نحصل على أكثر من قيمة (بسبب Jitter)
        assert len(thresholds) > 1
    
    def test_threshold_minimum_is_five(self):
        entity = IntuitiveDigitalEntity(initial_anxiety=1.0, base_threshold=5)
        # حتى مع قلق أقصى، العتبة لا تقل عن 5
        threshold = entity.generate_dynamic_threshold()
        assert threshold >= 5


class TestPolymorphicResponse:
    """اختبارات الاستجابات متعددة الأشكال."""
    
    def test_below_threshold_returns_allow(self):
        entity = IntuitiveDigitalEntity()
        response, _ = entity.decide_unpredictable_action(
            threat_score=10, threshold=45
        )
        assert response == ResponseType.ALLOW
    
    def test_above_threshold_returns_non_allow(self):
        entity = IntuitiveDigitalEntity()
        response, _ = entity.decide_unpredictable_action(
            threat_score=80, threshold=45
        )
        assert response != ResponseType.ALLOW
    
    def test_responses_are_varied(self):
        """يجب أن نرى استجابات مختلفة على مدى عدة قرارات."""
        entity = IntuitiveDigitalEntity(initial_anxiety=0.5)
        responses = set()
        for _ in range(50):
            response, _ = entity.decide_unpredictable_action(
                threat_score=70, threshold=45, entropy=6.0
            )
            responses.add(response)
        # يجب أن نرى على الأقل 3 استجابات مختلفة
        assert len(responses) >= 3
    
    def test_tar_pit_has_delay_parameter(self):
        entity = IntuitiveDigitalEntity()
        # فرض استجابة tar_pit عبر تعديل الاحتمالات
        entity._select_polymorphic_response = lambda *args, **kwargs: ResponseType.INFINITE_TAR_PIT
        
        response, params = entity.decide_unpredictable_action(
            threat_score=70, threshold=45
        )
        assert response == ResponseType.INFINITE_TAR_PIT
        assert "delay_seconds" in params
        assert params["delay_seconds"] > 0


class TestDiagnostics:
    """اختبارات التشخيص."""
    
    def test_diagnostics_returns_dict(self):
        entity = IntuitiveDigitalEntity()
        diag = entity.get_diagnostics()
        assert isinstance(diag, dict)
        assert "anxiety_index" in diag
        assert "anxiety_level" in diag
        assert "current_threshold" in diag
    
    def test_anxiety_classification(self):
        entity = IntuitiveDigitalEntity()
        diag = entity.get_diagnostics()
        assert diag["anxiety_level"] in ["calm", "alert", "concerned", "anxious", "panic"]
