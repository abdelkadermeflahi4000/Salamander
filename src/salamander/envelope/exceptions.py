"""Custom exceptions for Salamander."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salamander.core.detector import ScanResult


class UnsafeContentError(Exception):
    """Raised when content is blocked by Salamander."""

    def __init__(self, message: str, result: "ScanResult | None" = None):
        super().__init__(message)
        self.result = result
