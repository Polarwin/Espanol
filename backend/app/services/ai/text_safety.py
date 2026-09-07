"""Conservative edit checks, not a guarantee of preserved meaning."""
import re
from difflib import SequenceMatcher


def acceptable_edit(original: str, suggested: str) -> bool:
    if SequenceMatcher(None, original, suggested).ratio() < 0.55:
        return False
    if re.findall(r'\d+', original) != re.findall(r'\d+', suggested):
        return False
    # Protect noninitial capitalized words (e.g. names). Sentence-initial verb
    # changes such as Soy -> Tengo remain possible. This is deliberately coarse.
    def capitals(text):
        return [m.group() for m in re.finditer(r'\b[A-ZÁÉÍÓÚÑÜ][a-záéíóúñü]+\b', text) if text[:m.start()].strip() and text[:m.start()].rstrip()[-1] not in '.!?']
    return capitals(original) == capitals(suggested)
