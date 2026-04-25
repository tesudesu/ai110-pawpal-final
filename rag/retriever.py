import json
import os
import math
import requests
from dotenv import load_dotenv

load_dotenv()

_chunks = None
_embeddings = None

_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pet_care_kb.json")
_API_KEY = os.getenv("GEMINI_API_KEY")
_EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-embedding-001:embedContent?key={_API_KEY}"
)


def _embed(text: str) -> list[float]:
    payload = {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": text}]}}
    response = requests.post(_EMBED_URL, json=payload)
    response.raise_for_status()
    return response.json()["embedding"]["values"]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _load_kb():
    global _chunks, _embeddings
    if _chunks is None:
        with open(_KB_PATH) as f:
            _chunks = json.load(f)
        _embeddings = [_embed(c["text"]) for c in _chunks]


def retrieve(query: str, k: int = 3) -> list[str]:
    _load_kb()
    query_vec = _embed(query)
    scores = [_cosine(query_vec, emb) for emb in _embeddings]
    top_k = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [_chunks[i]["text"] for i in top_k]
