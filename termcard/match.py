import re
import unicodedata
from difflib import SequenceMatcher

_PERSIAN_MAP = str.maketrans({
    "ي": "ی", "ك": "ک", "ة": "ه", "ۀ": "ه", "ؤ": "و",
    "إ": "ا", "أ": "ا", "آ": "ا", "ٱ": "ا",
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
})


def normalize(s: str) -> str:
    # 1. compat forms (ﬁ→fi, ①→1, etc.)
    s = unicodedata.normalize("NFKC", s)
    # 2. Persian/Arabic char map (yeh, kaf, alef, digits)
    s = s.translate(_PERSIAN_MAP)
    # 3. decompose precomposed accents: ó → o + U+0301
    s = unicodedata.normalize("NFD", s)
    # 4. drop combining marks (accents, harakat)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # 5. lowercase
    s = s.lower()
    # 6. strip punctuation → space
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    # 7. collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def match_answer(user: str, expected: str) -> tuple[str, float]:
    """Returns (result, ratio). result ∈ {reveal, correct, close, wrong}."""
    u, e = normalize(user), normalize(expected)
    if not u:
        return "reveal", 0.0
    if u == e:
        return "correct", 1.0
    ratio = SequenceMatcher(None, u, e).ratio()
    if ratio >= 0.8:
        return "close", ratio
    return "wrong", ratio
