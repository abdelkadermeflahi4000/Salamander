"""
وحدة التسجيل الجنائي (Forensic Audit Logging) لمشروع Salamander.

الميزات الأمنية:
1. تنسيق JSON صارم: لتسهيل البلع من قبل أنظمة SIEM (مثل ELK, Splunk).
2. منع حقن السجلات (Log Injection Sanitization): تنظيف الأحرف التحكمية.
3. تجزئة الحمولة (Payload Hashing): حفظ بصمة SHA-256 للنص الهجومي دون تخزين النص الكامل الخطير.
4. التدوير الآمن (Log Rotation): منع هجمات حجب الخدمة (DoS) عبر ملء قرص التخزين.
"""

import json
import logging
import os
import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """
    مُنسق مخصص لتحويل سجلات الأحداث إلى كائنات JSON صالحة.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "event_id": getattr(record, "event_id", str(uuid.uuid4())),
            "event_type": getattr(record, "event_type", "UNKNOWN"),
            "severity": getattr(record, "severity", "INFO"),
            "context": getattr(record, "context", "N/A"),
            "rhythm_state": getattr(record, "rhythm_state", "UNKNOWN"),
            "score": getattr(record, "score", 0.0),
            "threshold_triggered": getattr(record, "threshold_triggered", 0.0),
            "matched_categories": getattr(record, "matched_categories", []),
            "payload_snippet": getattr(record, "payload_snippet", ""),
            "payload_sha256": getattr(record, "payload_sha256", ""),
            "action_taken": getattr(record, "action_taken", "NONE"),
            "agent_version": getattr(record, "agent_version", "Salamander-v1.0")
        }
        # استخدام ensure_ascii=False لدعم اللغة العربية في السجلات بشكل صحيح
        return json.dumps(log_record, ensure_ascii=False)


class AuditLogger:
    """
    المحرك المركزي للتسجيل الجنائي لأحداث الأمان في Salamander.
    """
    
    def __init__(
        self, 
        log_dir: str = "logs", 
        filename: str = "salamander_audit.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB لكل ملف
        backup_count: int = 5               # الاحتفاظ بـ 5 ملفات احتياطية
    ):
        """
        تهيئة مسجل التدقيق مع تدوير تلقائي للملفات.
        """
        self.log_dir = log_dir
        self.filename = filename
        
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        os.makedirs(self.log_dir, exist_ok=True)
        log_path = os.path.join(self.log_dir, self.filename)
        
        # إعداد الـ Logger
        self.logger = logging.getLogger("SalamanderAudit")
        self.logger.setLevel(logging.INFO)
        
        # منع تكرار المعالجات إذا تم استدعاء __init__ عدة مرات
        if not self.logger.handlers:
            # استخدام RotatingFileHandler لمنع امتلاء القرص (دفاع ضد DoS)
            handler = RotatingFileHandler(
                log_path, 
                maxBytes=max_bytes, 
                backupCount=backup_count, 
                encoding="utf-8"
            )
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def _sanitize_and_truncate(self, text: str, max_length: int = 250) -> str:
        """
        تنظيف النص من أحرف التحكم (لمنع Log Injection) وتقصيره.
        """
        if not text:
            return ""
        
        # إزالة أحرف السطر الجديد والتبويب لمنع تزوير هيكل سجل JSON
        sanitized = text.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        
        # التقصير مع إضافة علامة الحذف
        if len(sanitized) > max_length:
            return sanitized[:max_length] + "..."
        return sanitized

    def _hash_payload(self, text: str) -> str:
        """
        إنشاء بصمة SHA-256 للحمولة الكاملة لأغراض الطب الشرعي الرقمي،
        دون الحاجة لتخزين النص الهجومي الكامل في السجل.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def log_threat(
        self,
        severity: str,
        payload: str,
        context: str,
        score: float,
        threshold: float,
        matched_categories: List[str],
        action_taken: str,
        rhythm_state: str = "UNKNOWN"
    ) -> None:
        """
        تسجيل حدث أمني عالي الخطورة.
        
        Args:
            severity: مستوى الخطورة (CRITICAL, HIGH, MEDIUM, LOW)
            payload: النص الأصلي الذي تم فحصه
            context: سياق العملية (مثال: DESTRUCTIVE_INFRASTRUCTURE_COMMAND)
            score: درجة الخطورة المحسوبة
            threshold: عتبة الحظر التي تم تجاوزها
            matched_categories: قائمة بأنماط الهجوم المكتشفة
            action_taken: الإجراء المتخذ (مثال: TOOL_EXECUTION_FROZEN)
            rhythm_state: حالة محرك الإيقاع وقت الحدث (مثال: GAMMA)
        """
        # 1. التحضير الآمن للبيانات
        snippet = self._sanitize_and_truncate(payload, max_length=200)
        payload_hash = self._hash_payload(payload)
        event_id = str(uuid.uuid4())
        
        # 2. إنشاء كائن سجل مخصص
        log_record = logging.LogRecord(
            name="SalamanderAudit",
            level=logging.WARNING if severity in ["MEDIUM", "HIGH"] else logging.CRITICAL,
            pathname="",
            lineno=0,
            msg=f"Security Threat Detected: {context}",
            args=(),
            exc_info=None
        )
        
        # 3. إرفاق البيانات الإضافية (Extra Fields)
        log_record.event_id = event_id
        log_record.event_type = "INJECTION_BLOCKED"
        log_record.severity = severity
        log_record.context = context
        log_record.rhythm_state = rhythm_state
        log_record.score = score
        log_record.threshold_triggered = threshold
        log_record.matched_categories = matched_categories
        log_record.payload_snippet = snippet
        log_record.payload_sha256 = payload_hash
        log_record.action_taken = action_taken
        
        # 4. الكتابة إلى ملف السجل بتنسيق JSON
        self.logger.handle(log_record)
        
        # طباعة تنبيه فوري في وحدة التحكم (للتنبيه السريع أثناء التطوير)
        print(f"🚨 [AUDIT ALERT] {severity} | Context: {context} | Action: {action_taken} | ID: {event_id[:8]}")

    def log_system_event(self, event_type: str, message: str, details: Dict[str, Any] = None) -> None:
        """
        تسجيل أحداث النظام العامة (مثل بدء التشغيل، تحديث الأنماط).
        """
        log_record = logging.LogRecord(
            name="SalamanderAudit",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        log_record.event_id = str(uuid.uuid4())
        log_record.event_type = event_type
        log_record.details = details or {}
        
        self.logger.handle(log_record)
