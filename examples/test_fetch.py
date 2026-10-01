import pytest

from salamander.integrations.fetch import FetchError, check_url, fetch_and_gate

BAD_URLS = [
    "file:///etc/passwd",
    "ftp://example.com/x",
    "http://127.0.0.1/",
    "http://localhost/",
    "http://169.254.169.254/latest/meta-data/",
    "http://10.0.0.5/",
    "http://192.168.1.1/",
    "http://[::1]/",
    "http://[::ffff:127.0.0.1]/",
    "http:///nohost",
]


@pytest.mark.parametrize("url", BAD_URLS)
def test_non_public_or_non_http_urls_rejected(url: str) -> None:
    with pytest.raises(FetchError):
        check_url(url)


def test_fetch_and_gate_returns_refusal_not_exception() -> None:
    out = fetch_and_gate("http://127.0.0.1/")
    assert out["allowed"] is False
    assert out["verdict"] == "error"
    assert out["content"] is None
