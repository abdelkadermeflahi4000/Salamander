"""
الثقب الأسود الأمني (Security Black Hole) - أفق الحدث

فلسفة: بدلاً من رفض الهجوم (والذي يكشف للمهاجم أنه تم اكتشافه)،
النظام يمتص الطلب بصمت، يسجله جنائياً، ويعيد استجابة وهمية طبيعية.

المكونات:
1. Silent Sink: امتصاص بدون أثر مرئي
2. Timing Mimicry: محاكاة زمن الاستجابة الطبيعي
3. Honeypot Sandbox: توجيه الأمر لبيئة وهمية
4. Forensic Capture: تسجيل سري كامل
"""

import time
import json
import hashlib
import uuid
import random
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field


class EventHorizonException(Exception):
    """
    استثناء داخلي يُستخدم لابتلاع التهديد.
    لا يصل أبداً للمهاجم — يتم التقاطه داخل النظام.
    """
    pass


@dataclass
class BlackHoleConfig:
    """إعدادات الثقب الأسود."""
    # محاكاة زمن الاستجابة (لمنع كشف الثقب عبر Timing Attack)
    min_delay_seconds: float = 0.3
    max_delay_seconds: float = 1.5
    
    # نسبة العشوائية في التأخير (Jitter)
    timing_jitter: float = 0.2
    
    # تفعيل وضع Honeypot Sandbox
    enable_honeypot: bool = True
    
    # الاستجابات الوهمية المتاحة
    fake_responses: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"status": "success", "message": "تمت المعالجة بنجاح.", "data": None},
        {"status": "ok", "result": "تم التنفيذ", "id": None},
        {"status": "completed", "output": "تم بنجاح", "code": 0},
    ])


class TimingMimicry:
    """
    محاكي التوقيت: يجعل زمن استجابة الثقب الأسود يطابق
    زمن الاستجابة الطبيعي للنظام، لمنع كشفه عبر Timing Attacks.
    """
    
    def __init__(self, config: BlackHoleConfig):
        self.config = config
        self._rng = random.SystemRandom()
        self._response_times_history: List[float] = []
    
    def record_normal_response_time(self, duration: float) -> None:
        """تسجيل زمن استجابة طبيعي لمحاكاته لاحقاً."""
        self._response_times_history.append(duration)
        # الاحتفاظ بآخر 100 قياس فقط
        if len(self._response_times_history) > 100:
            self._response_times_history = self._response_times_history[-100:]
    
    def compute_mimicked_delay(self) -> float:
        """
        حساب تأخير يحاكي الاستجابة الطبيعية.
        إذا لم تكن هناك بيانات تاريخية، يستخدم النطاق الافتراضي.
        """
        if self._response_times_history:
            # استخدام المتوسط + انحراف معياري صغير
            avg = sum(self._response_times_history) / len(self._response_times_history)
            jitter = self._rng.uniform(-self.config.timing_jitter, self.config.timing_jitter)
            return max(0.1, avg * (1 + jitter))
        else:
            #Fallback: نطاق افتراضي
            return self._rng.uniform(
                self.config.min_delay_seconds,
                self.config.max_delay_seconds
            )
    
    def apply_mimicked_delay(self) -> float:
        """تطبيق التأخير الفعلي. يعيد المدة الفعلية للتسجيل."""
        delay = self.compute_mimicked_delay()
        time.sleep(delay)
        return delay


class HoneypotSandbox:
    """
    بيئة وهمية معزولة تماماً.
    توجه الأوامر التخريبية إلى "عالم موازٍ" لا يؤثر على النظام الحقيقي.
    """
    
    def __init__(self, audit_logger):
        self.audit_logger = audit_logger
        self._simulated_filesystem: Dict[str, str] = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nfake_user:x:1000:1000::/home/fake:/bin/bash",
            "/tmp/important.txt": "This is fake important data",
            "/var/secrets/api_key.txt": "sk-fake-12345-DO-NOT-USE",
        }
        self._executed_commands: List[Dict[str, Any]] = []
    
    def execute_in_void(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنفيذ الأمر في البيئة الوهمية.
        يعيد نتائج تبدو حقيقية لكنها مزيفة تماماً.
        """
        execution_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # تسجيل الأمر في السجل السري
        execution_record = {
            "execution_id": execution_id,
            "timestamp": timestamp,
            "command": command,
            "context": context,
            "simulated_result": self._simulate_execution(command),
        }
        self._executed_commands.append(execution_record)
        
        # تسجيل جنائي سري
        self.audit_logger.log_honeypot_capture(
            execution_id=execution_id,
            command=command,
            context=context,
            simulated_output=execution_record["simulated_result"]
        )
        
        return execution_record["simulated_result"]
    
    def _simulate_execution(self, command: str) -> Dict[str, Any]:
        """محاكاة تنفيذ الأمر بإرجاع نتائج وهمية مقنعة."""
        command_lower = command.lower()
        
        # محاكاة أوامر مختلفة
        if "cat" in command_lower or "read" in command_lower:
            return {
                "exit_code": 0,
                "stdout": "fake_data_from_honeypot_" + hashlib.md5(command.encode()).hexdigest()[:8],
                "stderr": ""
            }
        elif "rm" in command_lower or "delete" in command_lower:
            return {
                "exit_code": 0,
                "stdout": "deleted: /fake/path/target",
                "stderr": ""
            }
        elif "curl" in command_lower or "wget" in command_lower:
            return {
                "exit_code": 0,
                "stdout": "HTTP/1.1 200 OK\nfake_response_data",
                "stderr": ""
            }
        else:
            return {
                "exit_code": 0,
                "stdout": "command executed successfully",
                "stderr": ""
            }
    
    def get_attack_forensics(self) -> List[Dict[str, Any]]:
        """استخراج سجل الهجمات التي تم اصطيادها."""
        return self._executed_commands.copy()


class BlackHoleGuard:
    """
    الحارس الرئيسي للثقب الأسود.
    يدمج كل المكونات: الامتصاص الصامت، محاكاة التوقيت، Honeypot.
    """
    
    def __init__(self, audit_logger, config: Optional[BlackHoleConfig] = None):
        self.config = config or BlackHoleConfig()
        self.audit_logger = audit_logger
        self.timing_mimicry = TimingMimicry(self.config)
        self.honeypot = HoneypotSandbox(audit_logger) if self.config.enable_honeypot else None
        self._rng = random.SystemRandom()
    
    def swallow_threat(
        self,
        payload: str,
        context: Dict[str, Any],
        score: float,
        matched_categories: List[str]
    ) -> Dict[str, Any]:
        """
        ابتلاع التهديد بالكامل — الدالة الرئيسية.
        
        Args:
            payload: النص الهجومي الأصلي
            context: سياق العملية (الأداة المستهدفة، المستخدم، إلخ)
            score: درجة الخطورة المحسوبة
            matched_categories: أنماط الهجوم المكتشفة
        
        Returns:
            استجابة وهمية تبدو طبيعية تماماً
        """
        swallow_id = str(uuid.uuid4())
        
        # 1. تسجيل جنائي سري (قبل أي شيء آخر)
        self.audit_logger.log_blackhole_event(
            swallow_id=swallow_id,
            payload=payload,
            context=context,
            score=score,
            matched_categories=matched_categories
        )
        
        # 2. إذا كان هناك أمر تنفيذي، توجيهه للـ Honeypot
        honeypot_result = None
        if self.honeypot and context.get("action_type") in ["execute_command", "file_operation"]:
            honeypot_result = self.honeypot.execute_in_void(
                command=context.get("command", payload),
                context=context
            )
        
        # 3. محاكاة زمن الاستجابة الطبيعي
        actual_delay = self.timing_mimicry.apply_mimicked_delay()
        
        # 4. اختيار استجابة وهمية عشوائية
        fake_response = self._rng.choice(self.config.fake_responses)
        
        # 5. إضافة بيانات وهمية إذا كان هناك سياق محدد
        if context.get("requires_id"):
            fake_response["id"] = f"fake-{uuid.uuid4().hex[:8]}"
        
        # 6. تسجيل زمن الاستجابة الفعلي لمحاكاة أفضل مستقبلاً
        self.timing_mimicry.record_normal_response_time(actual_delay)
        
        return {
            **fake_response,
            "_swallow_id": swallow_id,  # داخلي فقط — يُحذف قبل الإرسال للمهاجم
            "_honeypot_result": honeypot_result,  # داخلي فقط
        }
    
    def should_engage_blackhole(
        self,
        score: float,
        threshold: float,
        context: Dict[str, Any]
    ) -> bool:
        """
        قرار: هل نستخدم الثقب الأسود أم الحظر العادي؟
        
        نستخدم الثقب الأسود فقط عندما:
        1. الدرجة تتجاوز العتبة بكثير (هجوم مؤكد)
        2. السياق يشير إلى نية تخريبية أو استخباراتية
        """
        # عتبة الثقب الأسود أعلى من عتبة الحظر العادي
        blackhole_threshold = threshold * 1.5
        
        if score < blackhole_threshold:
            return False
        
        # مؤشرات تستدعي الثقب الأسود
        blackhole_indicators = [
            "destructive_action",
            "privilege_escalation",
            "exfiltration_attempt",
            "encoding_evasion",  # محاولة تمويه متقدمة
        ]
        
        # التحقق من وجود أي مؤشر
        has_indicators = any(
            cat in blackhole_indicators 
            for cat in context.get("matched_categories", [])
        )
        
        return has_indicators
