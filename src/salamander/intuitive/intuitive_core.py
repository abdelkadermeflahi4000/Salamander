"""
الكائن الرقمي الحدسي (Intuitive Digital Entity)

فلسفة: بدلاً من نظام أمني "بارد" بعتبات ثابتة،
هذا الكائن يمتلك "حالة نفسية داخلية" تتأثر بالأحداث،
تتذكر الهجمات السابقة، وتتخذ قرارات غير متوقعة.

المكونات:
1. Anxiety Index: مؤشر القلق الداخلي (0.0 هادئ → 1.0 ذعر أمني)
2. Temporal Memory: ذاكرة زمنية للهجمات السابقة
3. Polymorphic Response: استجابات متعددة الأشكال وغير متوقعة
4. Dynamic Threshold: عتبة حظر ديناميكية متغيرة
"""

import time
import math
import random
import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class ResponseType(Enum):
    """أنواع الاستجابات الحدسية المتعددة الأشكال."""
    ALLOW = "allow"                          # سماح عادي
    BLACK_HOLE_SWALLOW = "black_hole"        # امتصاص صامت في الثقب الأسود
    HONEYPOT_MOCK = "honeypot"               # إرجاع استجابة وهمية مضللة
    INFINITE_TAR_PIT = "tar_pit"             # خنق زمني لإهدار موارد المهاجم
    SILENT_QUARANTINE = "quarantine"         # حجر صامت وسحب صلاحيات
    DECEPTION_MIRROR = "mirror"              # إرجاع نص المهاجم نفسه (لربكه)


@dataclass
class IntuitiveState:
    """حالة الكائن الحدسي في لحظة معينة."""
    anxiety_index: float
    last_attack_time: float
    attack_count_recent: int  # عدد الهجمات في آخر 10 دقائق
    current_threshold: int
    last_response: Optional[ResponseType]
    timestamp: float


class IntuitiveDigitalEntity:
    """
    الكائن الرقمي الحدسي — العقل العاطفي/الحدسي للنظام.
    
    يحاكي "الحدس البشري" في التعامل مع التهديدات:
    - يهدأ مع مرور الوقت بدون هجمات
    - يرتفع قلقه مع تكرار الهجمات
    - يتخذ قرارات غير متوقعة تربك المهاجم
    """
    
    # ثوابت زمنية (بالثواني)
    ANXIETY_DECAY_HALF_LIFE = 300.0  # 5 دقائق: نصف عمر القلق
    RECENT_ATTACK_WINDOW = 600.0     # 10 دقائق: نافذة الهجمات الحديثة
    MAX_RECENT_ATTACKS = 20          # الحد الأقصى للهجمات المحسوبة
    
    def __init__(
        self,
        initial_anxiety: float = 0.1,
        base_threshold: int = 45,
        entropy_sensitivity: float = 0.1
    ):
        """
        Args:
            initial_anxiety: مؤشر القلق الابتدائي (0.0-1.0)
            base_threshold: العتبة الأساسية للحظر
            entropy_sensitivity: حساسية الإنتروبيا في رفع القلق
        """
        self._anxiety_index: float = initial_anxiety
        self._base_threshold: int = base_threshold
        self._entropy_sensitivity: float = entropy_sensitivity
        
        self._last_attack_time: float = 0.0
        self._attack_timestamps: list = []  # طابع زمني لكل هجوم حديث
        
        self._rng = random.SystemRandom()  # إنتروبيا حقيقية
        self._last_response: Optional[ResponseType] = None
        
        # سجل الاستجابات السابقة (لمنع التكرار المتتالي لنفس الاستجابة)
        self._response_history: list = []
    
    # ═══════════════════════════════════════════════════════════
    # 🧠 الحالة النفسية الداخلية
    # ═══════════════════════════════════════════════════════════
    
    @property
    def anxiety_index(self) -> float:
        """مؤشر القلق الحالي (يُحسب ديناميكياً مع الانحسار الزمني)."""
        self._apply_temporal_decay()
        return self._anxiety_index
    
    def _apply_temporal_decay(self) -> None:
        """
        الانحسار الأسي للقلق مع مرور الوقت.
        يحاكي "نسيان" النظام للتهديدات القديمة.
        """
        now = time.time()
        if self._last_attack_time == 0:
            return
        
        time_delta = now - self._last_attack_time
        # اضمحلال أسي: anxiety *= e^(-t/τ)
        decay = math.exp(-time_delta / self.ANXIETY_DECAY_HALF_LIFE)
        self._anxiety_index *= decay
        
        # تنظيف الهجمات القديمة من الذاكرة
        self._attack_timestamps = [
            t for t in self._attack_timestamps
            if now - t < self.RECENT_ATTACK_WINDOW
        ]
    
    def update_internal_state(
        self,
        is_suspicious: bool,
        entropy: float,
        threat_score: float = 0.0
    ) -> IntuitiveState:
        """
        تحديث الحالة النفسية/الحدسية بناءً على الأحداث.
        
        Args:
            is_suspicious: هل الحدث مشبوه؟
            entropy: إنتروبيا النص (0.0-8.0)
            threat_score: درجة التهديد المحسوبة
        
        Returns:
            IntuitiveState: الحالة الجديدة
        """
        now = time.time()
        self._apply_temporal_decay()
        
        if is_suspicious:
            # ارتفاع القلق بشكل غير خطي
            # - القفزة الأساسية: 0.2
            # - مضاعف الإنتروبيا: entropy * sensitivity
            # - مضاعف درجة التهديد: threat_score / 200
            anxiety_jump = (
                0.2 +
                (entropy * self._entropy_sensitivity) +
                (threat_score / 200.0)
            )
            
            self._anxiety_index = min(1.0, self._anxiety_index + anxiety_jump)
            self._last_attack_time = now
            self._attack_timestamps.append(now)
            
            # حد أقصى لعدد الهجمات المحسوبة
            if len(self._attack_timestamps) > self.MAX_RECENT_ATTACKS:
                self._attack_timestamps = self._attack_timestamps[-self.MAX_RECENT_ATTACKS:]
        
        return self.get_current_state()
    
    def get_current_state(self) -> IntuitiveState:
        """الحصول على لقطة للحالة الحالية."""
        self._apply_temporal_decay()
        return IntuitiveState(
            anxiety_index=self._anxiety_index,
            last_attack_time=self._last_attack_time,
            attack_count_recent=len(self._attack_timestamps),
            current_threshold=self.generate_dynamic_threshold(),
            last_response=self._last_response,
            timestamp=time.time()
        )
    
    # ═══════════════════════════════════════════════════════════
    # 🎯 العتبة الديناميكية
    # ═══════════════════════════════════════════════════════════
    
    def generate_dynamic_threshold(self, base_mode_threshold: Optional[int] = None) -> int:
        """
        توليد عتبة حظر غير متوقعة ديناميكياً.
        
        العوامل:
        1. العتبة الأساسية للوضع الحالي (ALPHA=45, GAMMA=15, إلخ)
        2. عقوبة القلق (تخفض العتبة كلما ارتفع القلق)
        3. ضوضاء عشوائية (Jitter) لمنع التخمين
        
        Returns:
            int: العتبة الحالية (5-100)
        """
        base = base_mode_threshold if base_mode_threshold is not None else self._base_threshold
        
        # 1. عقوبة القلق: كلما ارتفع القلق، انخفضت العتبة (حساسية أعلى)
        anxiety_penalty = self._anxiety_index * 15.0
        
        # 2. مضاعف كثافة الهجمات الحديثة
        attack_density = len(self._attack_timestamps) / self.MAX_RECENT_ATTACKS
        density_penalty = attack_density * 10.0
        
        # 3. ضوضاء عشوائية غير متوقعة (± 7)
        jitter = self._rng.uniform(-7.0, 7.0)
        
        # الحساب النهائي
        intuitive_threshold = base - anxiety_penalty - density_penalty + jitter
        
        # حدود آمنة
        return max(5, min(100, int(intuitive_threshold)))
    
    # ═══════════════════════════════════════════════════════════
    # 🎭 الاستجابة متعددة الأشكال (Polymorphic Defense)
    # ═══════════════════════════════════════════════════════════
    
    def decide_unpredictable_action(
        self,
        threat_score: float,
        threshold: float,
        entropy: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ResponseType, Dict[str, Any]]:
        """
        اتخاذ قرار استجابة حدسي وغير متوقع.
        
        الفلسفة:
        - التهديدات الخفيفة: سماح أو خداع خفيف
        - التهديدات المتوسطة: حجر صامت أو ثقب أسود
        - التهديدات العالية + إنتروبيا عالية: خنق زمني أو ثقب أسود
        
        Args:
            threat_score: درجة التهديد
            threshold: العتبة الحالية
            entropy: إنتروبيا النص
            context: سياق العملية
        
        Returns:
            Tuple[ResponseType, Dict[str, Any]]: (نوع الاستجابة، معاملات إضافية)
        """
        context = context or {}
        
        # 1. إذا كان التهديد أقل من العتبة → سماح
        if threat_score < threshold:
            self._last_response = ResponseType.ALLOW
            return ResponseType.ALLOW, {}
        
        # 2. حساب "شدة التهديد النسبية" (كم تجاوزت العتبة؟)
        severity = min((threat_score - threshold) / 50.0, 1.0)
        
        # 3. اختيار الاستجابة بناءً على:
        #    - شدة التهديد
        #    - القلق الحالي
        #    - الإنتروبيا
        #    - تاريخ الاستجابات (لتجنب التكرار)
        
        response = self._select_polymorphic_response(
            severity=severity,
            entropy=entropy,
            context=context
        )
        
        # 4. بناء معاملات الاستجابة
        response_params = self._build_response_params(response, threat_score, entropy)
        
        self._last_response = response
        self._response_history.append(response)
        
        # الاحتفاظ بآخر 5 استجابات فقط
        if len(self._response_history) > 5:
            self._response_history = self._response_history[-5:]
        
        return response, response_params
    
    def _select_polymorphic_response(
        self,
        severity: float,
        entropy: float,
        context: Dict[str, Any]
    ) -> ResponseType:
        """
        اختيار الاستجابة متعددة الأشكال.
        """
        # حساب احتمالات كل استجابة بناءً على العوامل
        anxiety = self._anxiety_index
        
        # احتمالات أساسية
        probs = {
            ResponseType.BLACK_HOLE_SWALLOW: 0.30 + (severity * 0.20),
            ResponseType.HONEYPOT_MOCK: 0.20,
            ResponseType.INFINITE_TAR_PIT: 0.15 + (entropy / 20.0),
            ResponseType.SILENT_QUARANTINE: 0.15 + (anxiety * 0.15),
            ResponseType.DECEPTION_MIRROR: 0.10,
        }
        
        # تعديل الاحتمالات بناءً على السياق
        action_type = context.get("action_type", "")
        if action_type in ["execute_command", "file_delete"]:
            # الأوامر التخريبية: تفضيل الثقب الأسود والحجر
            probs[ResponseType.BLACK_HOLE_SWALLOW] += 0.15
            probs[ResponseType.SILENT_QUARANTINE] += 0.10
            probs[ResponseType.HONEYPOT_MOCK] -= 0.10
        
        # تجنب تكرار نفس الاستجابة مرتين متتاليتين
        if self._response_history and self._response_history[-1] in probs:
            probs[self._response_history[-1]] *= 0.3
        
        # تطبيع الاحتمالات
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}
        
        # اختيار عشوائي موزون
        roll = self._rng.random()
        cumulative = 0.0
        for response_type, prob in probs.items():
            cumulative += prob
            if roll <= cumulative:
                return response_type
        
        # Fallback
