"""@wear must preserve function metadata."""

from __future__ import annotations
from salamander import wear

@wear(source="meta-test")
def documented_function(x: str) -> str:
    """This is the original docstring."""
    return f"echo: {x}"

def test_name_preserved():
    assert documented_function.__name__ == "documented_function"

def test_doc_preserved():
    assert documented_function.__doc__ is not None
    assert "original docstring" in documented_function.__doc__

def test_still_returns_envelope():
    from salamander.envelope.envelope import Envelope
    result = documented_function("hello")
    assert isinstance(result, Envelope)
