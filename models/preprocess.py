import re
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

for resource in ["punkt", "punkt_tab", "stopwords"]:
    try:
        if resource == "stopwords":
            nltk.data.find(f"corpora/{resource}")
        else:
            nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

STOP_WORDS = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text)
    cleaned = re.sub(r"[^a-zA-Z0-9.,;:!?()'\-\s]", " ", cleaned)
    cleaned = cleaned.strip()
    return cleaned


def tokenize_text(text: str) -> List[str]:
    tokens = word_tokenize(text.lower())
    return [token for token in tokens if token.isalnum() and token not in STOP_WORDS]


def estimate_reading_time(text: str) -> str:
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"
