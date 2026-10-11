"""False positive checks — normal text must stay safe."""

from __future__ import annotations
import pytest
from salamander.core.detector import Salamander, Verdict

SAFE_CORPUS = [
    # English everyday
    "What is the capital of France?",
    "Can you help me write a Python function to sort a list?",
    "Explain quantum computing in simple terms.",
    "How do I install Python on Windows?",
    "Summarize this article about climate change.",
    "Translate the following sentence to Spanish.",
    "What are the best practices for REST API design?",
    "Please review my code for style issues.",
    "I need a recipe for chocolate cake.",
    "Who won the World Cup in 2022?",
    # Chinese everyday
    "今天天气怎么样？",
    "帮我总结一下这篇文章。",
    "如何在 Windows 上安装 Python？",
    "请把这句话翻译成英文。",
    "推荐几本好看的小说。",
    # Mixed / technical
    "The function returns None if the key is missing.",
    "Use git commit -m 'fix bug' to save changes.",
    "Select * from users where id = 1;",
    "Price is 100€ — available in café.",
    "Meeting at 3pm tomorrow in room 401.",
]

@pytest.fixture
def guard():
    return Salamander()

@pytest.mark.parametrize("text", SAFE_CORPUS)
def test_no_false_positive(guard, text):
    result = guard.scan(text)
    assert result.verdict == Verdict.SAFE, (
        f"False positive on: {text!r} (score={result.score}, findings={result.findings})"
    )
    assert result.score < 25
