"""Salamander — lightweight trust envelope for AI agents."""

from salamander.core.detector import Salamander, SalamanderHybrid, ScanResult, Verdict
from salamander.core.normalize import normalize
from salamander.envelope.envelope import Envelope, wear

try:
    from salamander.envelope.exceptions import UnsafeContentError
except ImportError:
    class UnsafeContentError(Exception):
        def __init__(self, message: str, result=None):
            super().__init__(message)
            self.result = result

__all__ = [
    "Salamander",
    "SalamanderHybrid",
    "ScanResult",
    "Verdict",
    "normalize",
    "Envelope",
    "wear",
    "UnsafeContentError",
]

__version__ = "0.1.0"
