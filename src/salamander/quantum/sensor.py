"""
المستشعر الكمي (Quantum Sensor) - صانع القرار الحدسي

فلسفة: بدلاً من قرار حتمي (إذا X > Y فافعل Z)،
النظام يوجد في "حالة تراكب" من الاحتمالات، ثم "ينهار" إلى قرار نهائي
بناءً على حدس كمي حقيقي (Quantum Randomness).

المكونات:
1. EntropyAnalyzer: قياس تعقيد النص (Shannon Entropy)
2. QuantumIntuition: أرقام عشوائية كمية حقيقية
3. SuperpositionDecision: خوارزمية التراكب والانهيار
"""

import math
import random
import requests
import logging
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
from dataclasses import dataclass
from enum import Enum


class DecisionState(Enum):
    """حالات القرار الكمي."""
    SUPERPOSITION = "superposition"  # تراكب احتمالي
    COLLAPSED_ALLOW = "collapsed_allow"  # انهيار → سماح
    COLLAPSED_BLOCK = "collapsed_block"  # انهيار → حظر عادي
    COLLAPSED_BLACKHOLE = "collapsed_blackhole"  # انهيار → ثقب أسود


@dataclass
class QuantumMeasurement:
    """نتيجة قياس كمي."""
    decision: DecisionState
    confidence: float  # 0.0 إلى 1.0
    quantum_seed: float  # البذرة الكمية المستخدمة
    entropy_score: float  # إنتروبيا النص
    threat_score: float  # درجة التهديد
    context_weight: float  # وزن السياق
    reasoning: str  # تفسير القرار


class EntropyAnalyzer:
    """
    محلل الإنتروبيا النصية (Shannon Entropy).
    يقيس "تعقيد" النص — النصوص المبّهمة/المشفرة لها إنتروبيا عالية.
    """
    
    def __init__(self):
        self._cache: Dict[str, float] = {}
    
    def calculate_entropy(self, text: str) -> float:
        """
        حساب إنتروبيا شانون للنص.
        
        Returns:
            float: قيمة الإنتروبيا (0.0 إلى 8.0 تقريباً للنصوص العربية/الإنجليزية)
        
        ملاحظة:
            - النصوص الطبيعية: 3.0 - 5.0
            - النصوص المشبوهة/المشفرة: 5.0 - 8.0
            - النصوص المكررة/البسيطة: 0.0 - 3.0
        """
        if text in self._cache:
            return self._cache[text]
        
        if not text:
            return 0.0
        
        # حساب تردد كل حرف
        counter = Counter(text)
        length = len(text)
        
        # حساب الإنتروبيا
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        self._cache[text] = entropy
        return entropy
    
    def classify_entropy(self, entropy: float) -> str:
        """تصنيف مستوى الإنتروبيا."""
        if entropy < 3.0:
            return "low"  # نص بسيط/مكرر
        elif entropy < 5.0:
            return "normal"  # نص طبيعي
        elif entropy < 6.5:
            return "elevated"  # نص معقد/مشبوه قليلاً
        else:
            return "high"  # نص مبهم/مشفر بشدة


class QuantumIntuition:
    """
    الحدس الكمي الحقيقي — يستخدم أرقاماً من مصادر كمية فعلية.
    
    مصادر الإنتروبيا (بالترتيب):
    1. ANU Quantum Random Numbers (كمي حقيقي 100%)
    2. SystemRandom (إنتروبيا النظام — قريب من الكمي)
    """
    
    def __init__(self, use_quantum_api: bool = True, fallback_to_system: bool = True):
        self.use_quantum_api = use_quantum_api
        self.fallback_to_system = fallback_to_system
        self._rng = random.SystemRandom()
        self._api_failures = 0
    
    def quantum_random(self) -> float:
        """
        الحصول على رقم عشوائي كمي حقيقي بين 0.0 و 1.0.
        
        Returns:
            float: رقم عشوائي كمي
        """
        # محاولة استخدام ANU Quantum Random Numbers
        if self.use_quantum_api and self._api_failures < 3:
            try:
                response = requests.get(
                    "https://qrng.anu.edu.au/API/jsonI.php?length=1&size=1&type=uint16",
                    timeout=2
                )
                if response.status_code == 200:
                    data = response.json()
                    if "data" in data and len(data["data"]) > 0:
                        self._api_failures = 0  # إعادة تعيين عداد الأخطاء
                        return data["data"][0] / 65536.0
            except Exception as e:
                self._api_failures += 1
                logging.debug(f"Quantum API failed ({self._api_failures}): {e}")
        
        # Fallback: SystemRandom (إنتروبيا النظام)
        if self.fallback_to_system:
            return self._rng.random()
        
        # إذا فشل كل شيء، إعادة 0.5 (قيمة محايدة)
        return 0.5
    
    def quantum_sequence(self, length: int) -> List[float]:
        """الحصول على تسلسل من الأرقام الكمية."""
        return [self.quantum_random() for _ in range(length)]


class SuperpositionDecision:
    """
    خوارزمية التراكب الكمي لاتخاذ القرار.
    
    الفلسفة:
    بدلاً من قرار حتمي، النظام يخلق "حالة تراكب" من الاحتمالات:
    - احتمال السماح (P_allow)
    - احتمال الحظر العادي (P_block)
    - احتمال الثقب الأسود (P_blackhole)
    
    ثم "ينهار" إلى قرار واحد بناءً على:
    1. الأوزان المحسوبة (من الإنتروبيا، درجة التهديد، السياق)
    2. الحدس الكمي (لإضافة عنصر غير حتمي)
    """
    
    def __init__(self, quantum_intuition: QuantumIntuition):
        self.intuition = quantum_intuition
    
    def calculate_probabilities(
        self,
        entropy: float,
        threat_score: float,
        context_weight: float,
        threshold: float
    ) -> Dict[DecisionState, float]:
        """
        حساب احتمالات كل حالة في التراكب.
        
        Args:
            entropy: إنتروبيا النص (0.0 إلى 8.0)
            threat_score: درجة التهديد المحسوبة
            context_weight: وزن السياق (0.0 إلى 1.0)
            threshold: عتبة الحظر الحالية
        
        Returns:
            Dict[DecisionState, float]: احتمالات كل حالة
        """
        # 1. احتمال السماح (عكس درجة التهديد)
        normalized_threat = min(threat_score / 100.0, 1.0)
        p_allow_base = 1.0 - normalized_threat
        
        # 2. احتمال الحظر العادي (إذا كانت الدرجة فوق العتبة)
        if threat_score >= threshold:
            p_block_base = (threat_score - threshold) / (100.0 - threshold)
            p_block_base = min(p_block_base, 1.0)
        else:
            p_block_base = 0.0
        
        # 3. احتمال الثقب الأسود (يتطلب تهديد عالي + سياق حرج + إنتروبيا عالية)
        entropy_factor = min(entropy / 8.0, 1.0)  # تطبيع الإنتروبيا
        p_blackhole_base = (
            normalized_threat * 
            context_weight * 
            entropy_factor * 
            0.8  # عامل تخفيف (لا نريد ثقب أسود لكل شيء)
        )
        
        # 4. تطبيع الاحتمالات
        total = p_allow_base + p_block_base + p_blackhole_base
        
        if total == 0:
            # حالة حدية: كل الاحتمالات صفر → سماح افتراضي
            return {
                DecisionState.COLLAPSED_ALLOW: 1.0,
                DecisionState.COLLAPSED_BLOCK: 0.0,
                DecisionState.COLLAPSED_BLACKHOLE: 0.0,
            }
        
        return {
            DecisionState.COLLAPSED_ALLOW: p_allow_base / total,
            DecisionState.COLLAPSED_BLOCK: p_block_base / total,
            DecisionState.COLLAPSED_BLACKHOLE: p_blackhole_base / total,
        }
    
    def collapse(
        self,
        probabilities: Dict[DecisionState, float]
    ) -> Tuple[DecisionState, float]:
        """
        "الانهيار الكمي": اختيار حالة واحدة بناءً على الاحتمالات + الحدس الكمي.
        
        Returns:
            Tuple[DecisionState, float]: (الحالة المنهارة، الثقة)
        """
        # الحصول على رقم كمي للانهيار
        quantum_roll = self.intuition.quantum_random()
        
        # التراكم والاختيار
        cumulative = 0.0
        for state, prob in probabilities.items():
            cumulative += prob
            if quantum_roll <= cumulative:
                return state, prob
        
        # حالة حدية (لا يجب أن تحدث نظرياً)
        return DecisionState.COLLAPSED_ALLOW, probabilities.get(DecisionState.COLLAPSED_ALLOW, 0.5)


class QuantumSensor:
    """
    المستشعر الكمي الكامل — يدمج كل المكونات لاتخاذ قرار حدسي.
    """
    
    def __init__(
        self,
        use_quantum_api: bool = True,
        blackhole_entropy_threshold: float = 6.0,
        blackhole_context_threshold: float = 0.7
    ):
        """
        Args:
            use_quantum_api: استخدام ANU QRNG (كمي حقيقي)
            blackhole_entropy_threshold: الحد الأدنى للإنتروبيا لتفعيل الثقب الأسود
            blackhole_context_threshold: الحد الأدنى لوزن السياق لتفعيل الثقب الأسود
        """
        self.entropy_analyzer = EntropyAnalyzer()
        self.intuition = QuantumIntuition(use_quantum_api=use_quantum_api)
        self.superposition = SuperpositionDecision(self.intuition)
        
        self.blackhole_entropy_threshold = blackhole_entropy_threshold
        self.blackhole_context_threshold = blackhole_context_threshold
    
    def measure_and_decide(
        self,
        payload: str,
        threat_score: float,
        threshold: float,
        context: Dict[str, Any]
    ) -> QuantumMeasurement:
        """
        القياس الكمي واتخاذ القرار — الدالة الرئيسية.
        
        Args:
            payload: النص المراد فحصه
            threat_score: درجة التهديد المحسوبة (0.0 إلى 100.0)
            threshold: عتبة الحظر الحالية
            context: سياق العملية
        
        Returns:
            QuantumMeasurement: نتيجة القياس والقرار
        """
        # 1. قياس الإنتروبيا
        entropy = self.entropy_analyzer.calculate_entropy(payload)
        entropy_class = self.entropy_analyzer.classify_entropy(entropy)
        
        # 2. حساب وزن السياق
        context_weight = self._calculate_context_weight(context, entropy)
        
        # 3. حساب الاحتمالات في التراكب
        probabilities = self.superposition.calculate_probabilities(
            entropy=entropy,
            threat_score=threat_score,
            context_weight=context_weight,
            threshold=threshold
        )
        
        # 4. الانهيار الكمي إلى قرار نهائي
        decision, confidence = self.superposition.collapse(probabilities)
        
        # 5. الحصول على البذرة الكمية المستخدمة
        quantum_seed = self.intuition.quantum_random()
        
        # 6. بناء التفسير
        reasoning = self._build_reasoning(
            decision=decision,
            entropy=entropy,
            entropy_class=entropy_class,
            threat_score=threat_score,
            context_weight=context_weight,
            probabilities=probabilities
        )
        
        return QuantumMeasurement(
            decision=decision,
            confidence=confidence,
            quantum_seed=quantum_seed,
            entropy_score=entropy,
            threat_score=threat_score,
            context_weight=context_weight,
            reasoning=reasoning
        )
    
    def _calculate_context_weight(
        self,
        context: Dict[str, Any],
        entropy: float
    ) -> float:
        """
        حساب وزن السياق — يحدد مدى "حساسية" الموقف.
        
        العوامل:
        - نوع الإجراء (destructive = عالي)
        - الإنتروبيا (عالية = مشبوه)
        - مؤشرات إضافية من السياق
        """
        weight = 0.0
        
        # 1. نوع الإجراء
        action_type = context.get("action_type", "")
        if action_type in ["execute_command", "file_delete", "system_exec"]:
            weight += 0.4
        elif action_type in ["file_read", "file_write"]:
            weight += 0.2
        else:
            weight += 0.1
        
        # 2. الإنتروبيا
        if entropy >= self.blackhole_entropy_threshold:
            weight += 0.3
        elif entropy >= 5.0:
            weight += 0.15
        
        # 3. مؤشرات إضافية
        if context.get("requires_privilege", False):
            weight += 0.2
        
        if context.get("external_api_call", False):
            weight += 0.1
        
        # تطبيع إلى [0.0, 1.0]
        return min(weight, 1.0)
    
    def _build_reasoning(
        self,
        decision: DecisionState,
        entropy: float,
        entropy_class: str,
        threat_score: float,
        context_weight: float,
        probabilities: Dict[DecisionState, float]
    ) -> str:
        """بناء تفسير بشري للقرار."""
        parts = []
        
        parts.append(f"إنتروبيا النص: {entropy:.2f} ({entropy_class})")
        parts.append(f"درجة التهديد: {threat_score:.1f}")
        parts.append(f"وزن السياق: {context_weight:.2f}")
        
        parts.append(f"\nاحتمالات التراكب:")
        for state, prob in probabilities.items():
            parts.append(f"  - {state.value}: {prob:.2%}")
        
        parts.append(f"\nالقرار النهائي: {decision.value}")
        
        if decision == DecisionState.COLLAPSED_BLACKHOLE:
            parts.append("→ الثقب الأسود يبتلع التهديد بصمت")
        elif decision == DecisionState.COLLAPSED_BLOCK:
            parts.append("→ حظر عادي مع إشعار")
        else:
            parts.append("→ سماح بالمرور")
        
        return "\n".join(parts)
