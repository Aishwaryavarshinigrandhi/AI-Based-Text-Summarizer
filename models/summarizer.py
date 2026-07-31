import re
from collections import Counter
from typing import List, Optional

from transformers import pipeline

from models.preprocess import preprocess_text, tokenize_text

MODEL_MAP = {
    "bart": "facebook/bart-large-cnn",
    "pegasus": "google/pegasus-xsum",
    "t5": "t5-small",
}

_SUMMARY_PIPELINE: Optional[object] = None


def _get_pipeline(model_name: str):
    global _SUMMARY_PIPELINE
    if _SUMMARY_PIPELINE is None:
        _SUMMARY_PIPELINE = pipeline("summarization", model=MODEL_MAP.get(model_name, MODEL_MAP["bart"]))
    return _SUMMARY_PIPELINE


def _split_into_chunks(text: str, max_words: int = 450) -> List[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    for start in range(0, len(words), max_words):
        chunk = " ".join(words[start:start + max_words])
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks


def _extractive_chunk_summary(chunk: str, target_sentences: int = 3) -> str:
    cleaned = preprocess_text(chunk).strip()
    if not cleaned:
        return ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    if len(sentences) <= 2:
        return cleaned

    tokenized_sentences = [tokenize_text(sentence) for sentence in sentences]
    frequencies = Counter(word for tokens in tokenized_sentences for word in tokens)
    if not frequencies:
        return " ".join(sentences[:target_sentences])

    scored = []
    for index, tokens in enumerate(tokenized_sentences):
        score = sum(frequencies[token] for token in tokens) / max(1, len(tokens))
        if index == 0:
            score += 0.3
        if index == len(sentences) - 1:
            score += 0.2
        scored.append((score, sentences[index]))

    ranked = [sentence for _, sentence in sorted(scored, key=lambda item: item[0], reverse=True)]
    selected = ranked[:target_sentences]
    return " ".join(selected)


def _extractive_summary(text: str, length: str = "medium") -> str:
    cleaned = preprocess_text(text).strip()
    if len(cleaned.split()) < 20:
        return cleaned

    chunk_target = 2 if length == "short" else 3 if length == "detailed" else 2
    chunks = _split_into_chunks(cleaned, max_words=450)
    chunk_summaries = []
    for chunk in chunks:
        chunk_summaries.append(_extractive_chunk_summary(chunk, target_sentences=chunk_target))

    combined = " ".join(part for part in chunk_summaries if part)
    if len(combined.split()) <= 40:
        return combined

    final_summary = _extractive_chunk_summary(combined, target_sentences=max(2, chunk_target + 1))
    return final_summary


def summarize_text(text: str, length: str = "medium", model_name: str = "bart") -> str:
    cleaned = preprocess_text(text).strip()
    if len(cleaned.split()) < 20:
        return cleaned

    max_length = 110 if length == "short" else 220 if length == "detailed" else 180
    min_length = max(35, int(max_length * 0.65))

    try:
        pipeline_model = _get_pipeline(model_name)
        result = pipeline_model(cleaned, max_length=max_length, min_length=min_length, do_sample=False)
        summary = result[0]["summary_text"].strip()
        if len(summary.split()) > 12:
            return summary
    except Exception:
        pass

    fallback = _extractive_summary(cleaned, length=length)
    if not fallback or len(fallback.split()) < 20:
        return cleaned[: max_length * 3]
    return fallback
