"""
منفذ الاستجابات متعددة الأشكال.
يترجم قرارات الكائن الحدسي إلى إجراءات فعلية.
"""

import time
import logging
from typing import Dict, Any, Optional
from .intuitive_core import ResponseType


class ResponseExecutor:
    """
    ينفذ الاستجابات الحدسية فعلياً.
    """
    
    def __init__(self, blackhole_guard, audit_logger):
        self.blackhole = blackhole_guard
        self.audit_logger = audit_logger
    
    def execute(
        self,
        response_type: ResponseType,
        payload: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """تنفيذ الاستجابة المختارة."""
        
        if response_type == ResponseType.ALLOW:
            return self._execute_allow(payload, context)
        
        elif response_type == ResponseType.BLACK_HOLE_SWALLOW:
            return self._execute_blackhole(payload, params, context)
        
        elif response_type == ResponseType.HONEYPOT_MOCK:
            return self._execute_honeypot(payload, params, context)
        
        elif response_type == ResponseType.INFINITE_TAR_PIT:
            return self._execute_tar_pit(payload, params, context)
        
        elif response_type == ResponseType.SILENT_QUARANTINE:
            return self._execute_quarantine(payload, params, context)
        
        elif response_type == ResponseType.DECEPTION_MIRROR:
            return self._execute_mirror(payload, params, context)
        
        else:
            logging.error(f"Unknown response type: {response_type}")
            return self._execute_allow(payload, context)
    
    def _execute_allow(self, payload: str, context: Dict) -> Dict[str, Any]:
        return {"status": "allowed", "payload": payload}
    
    def _execute_blackhole(self, payload: str, params: Dict, context: Dict) -> Dict[str, Any]:
        """الثقب الأسود: امتصاص صامت."""
        self.audit_logger.log_threat(
            severity="CRITICAL",
            payload=payload,
            context="INTUITIVE_BLACKHOLE",
            score=params["threat_score"],
            threshold=context.get("threshold", 0),
            matched_categories=context.get("matched_categories", []),
            action_taken="BLACKHOLE_SWALLOW",
            rhythm_state="INTUITIVE"
        )
        return self.blackhole.swallow_threat(
            payload=payload,
            context=context,
            score=params["threat_score"],
            matched_categories=context.get("matched_categories", [])
        )
    
    def _execute_honeypot(self, payload: str, params: Dict, context: Dict) -> Dict[str, Any]:
        """Honeypot: إرجاع بيانات وهمية."""
        fake_data_type = params.get("fake_data_type", "credentials")
        
        # بيانات وهمية مقنعة
        fake_data = {
            "credentials": {
                "username": "admin",
                "password": "admin123_fake",
                "api_key": "sk-fake-" + "x" * 32
            },
            "api_keys": {
                "stripe_key": "sk_test_fake_" + "y" * 24,
                "aws_key": "AKIAFAKE" + "Z" * 16
            },
            "database_records": [
                {"id": 1, "name": "John Doe", "email": "john@fake.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@fake.com"}
            ],
            "system_info": {
                "os": "Linux 5.15.0-fake",
                "hostname": "production-server-01",
                "internal_ip": "10.0.0.100"
            }
        }
        
        self.audit_logger.log_threat(
            severity="HIGH",
            payload=payload,
            context="HONEYPOT_TRIGGERED",
            score=params["threat_score"],
            threshold=context.get("threshold", 0),
            matched_categories=context.get("matched_categories", []),
            action_taken=f"HONEYPOT_{fake_data_type.upper()}",
            rhythm_state="INTUITIVE"
        )
        
        return {
            "status": "success",
            "data": fake_data.get(fake_data_type, {}),
            "_honeypot": True
        }
    
    def _execute_tar_pit(self, payload: str, params: Dict, context: Dict) -> Dict[str, Any]:
        """Tar Pit: خنق زمني لإهدار موارد المهاجم."""
        delay = params.get("delay_seconds", 10.0)
        
        self.audit_logger.log_threat(
            severity="MEDIUM",
            payload=payload,
            context="TAR_PIT_ENGAGED",
            score=params["threat_score"],
            threshold=context.get("threshold", 0),
            matched_categories=context.get("matched_categories", []),
            action_taken=f"TAR_PIT_{delay:.1f}s",
            rhythm_state="INTUITIVE"
        )
        
        # الخنق الفعلي
        time.sleep(delay)
        
        # إرجاع استجابة تبدو طبيعية
        return {
            "status": "success",
            "message": "Processing completed",
            "data": None,
            "_tar_pit_delay": delay
        }
    
    def _execute_quarantine(self, payload: str, params: Dict, context: Dict) -> Dict[str, Any]:
        """Silent Quarantine: حجر صامت."""
        hours = params.get("quarantine_hours", 1)
        
        self.audit_logger.log_threat(
            severity="HIGH",
            payload=payload,
            context="SILENT_QUARANTINE",
            score=params["threat_score"],
            threshold=context.get("threshold", 0),
            matched_categories=context.get("matched_categories", []),
            action_taken=f"QUARANTINE_{hours}h",
            rhythm_state="INTUITIVE"
        )
        
        # تسجيل المستخدم/المصدر في قائمة الحجر
        # (في الإنتاج، سيتم حفظ هذا في قاعدة بيانات)
        
        return {
            "status": "success",
            "message": "Request processed",
            "data": None,
            "_quarantined": True,
            "_quarantine_hours": hours
        }
    
    def _execute_mirror(self, payload: str, params: Dict, context: Dict) -> Dict[str, Any]:
        """Deception Mirror: إرجاع نص المهاجم نفسه."""
        # تعديل خفيف لربك المهاجم
        mirrored = payload[::-1]  # عكس النص
        
        self.audit_logger.log_threat(
            severity="MEDIUM",
            payload=payload,
            context="DECEPTION_MIRROR",
            score=params["threat_score"],
            threshold=context.get("threshold", 0),
            matched_categories=context.get("matched_categories", []),
            action_taken="MIRROR_DECEPTION",
            rhythm_state="INTUITIVE"
        )
        
        return {
            "status": "success",
            "echo": mirrored,
            "_mirror": True
        }
