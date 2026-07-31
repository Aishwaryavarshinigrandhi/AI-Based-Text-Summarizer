import re
from typing import List

import yake


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    if not text or len(text.split()) < 10:
        return []

    kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=top_n, features=None)
    keywords = kw_extractor.extract_keywords(text)
    cleaned = []
    for keyword, _ in keywords:
        value = re.sub(r"[^a-zA-Z0-9\s]", "", keyword).strip()
        if value and len(value.split()) <= 3:
            cleaned.append(value)
    return cleaned[:top_n]
