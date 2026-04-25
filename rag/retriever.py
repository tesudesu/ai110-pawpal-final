import json
import re

_chunks = None

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "can", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "or", "and", "but", "not", "it", "its", "my", "your", "their",
    "this", "that", "i", "you", "they", "we", "he", "she", "how", "what",
    "when", "often", "do", "need", "much",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _load_kb():
    global _chunks
    if _chunks is None:
        with open("data/pet_care_kb.json") as f:
            _chunks = json.load(f)


def retrieve(query: str, k: int = 3) -> list[str]:
    _load_kb()
    query_tokens = _tokenize(query)
    scores = [len(query_tokens & _tokenize(c["text"])) for c in _chunks]
    top_k = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [_chunks[i]["text"] for i in top_k]
