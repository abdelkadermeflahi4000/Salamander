import re
import unicodedata


_ZERO_WIDTH = re.compile(
    r"[\u200b\u200c\u200d\u2060\ufeff]"
)


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH.sub("", text)

    return text.casefold()
@dataclass(frozen=True)
class NormalizedText:
    original: str
    value: str
    changed: bool
    mixed_scripts: bool
