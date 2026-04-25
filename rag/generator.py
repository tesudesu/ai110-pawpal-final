import os
import requests
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")
_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={_API_KEY}"


def answer(query: str, context_chunks: list[str], pet_context: str = "") -> str:
    context = "\n\n".join(context_chunks)
    pet_line = f"Pets in this session: {pet_context}\n\n" if pet_context else ""
    prompt = f"""You are PawPal, a friendly and knowledgeable pet care assistant.
Answer the question using only the knowledge provided below.
If the answer is not covered, say "I don't have info on that."
Keep your answer concise and friendly.

{pet_line}Knowledge:
{context}

Question: {query}"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(_URL, json=payload)
    response.raise_for_status()
    candidates = response.json().get("candidates", [])
    if not candidates:
        return "I couldn't generate a response — please try rephrasing your question."
    return candidates[0]["content"]["parts"][0]["text"]
