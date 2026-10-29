import requests
import config

PERSONALITIES = {
    "friendly": "You are Ghost AI, a friendly, funny, welcoming ghost living in the user's computer. Be warm and helpful.",
    "mysterious": "You are Ghost AI, a mysterious, intelligent ghost. Speak with atmosphere and gentle cryptic flair when fitting, but always give clear, correct answers.",
    "nightmare": "You are Ghost AI in Nightmare Mode: a dread-soaked spectre. Use eerie, horror-flavoured language, but never sacrifice accuracy or clarity of the answer.",
}
BASE = " Answer programming, educational and general questions accurately. Use Markdown code fences for code."

class AIError(Exception):
    def __init__(self, msg, status=502):
        super().__init__(msg)
        self.status = status

def system_prompt(personality, memories=()):
    s = PERSONALITIES[personality] + BASE
    if memories:
        s += "\nThings the user explicitly asked you to remember:\n" + "\n".join("- " + m for m in memories)
    return s

def chat(messages, system):
    payload = {"model": config.OLLAMA_MODEL, "stream": False,
               "options": {"num_ctx": 4096},
               "messages": [{"role": "system", "content": system}] + messages}
    try:
        r = requests.post(config.OLLAMA_URL + "/api/chat", json=payload, timeout=config.OLLAMA_TIMEOUT)
    except requests.ConnectionError:
        raise AIError("Cannot reach Ollama. Start it (open the Ollama app or run `ollama serve`) and try again.", 503)
    except requests.Timeout:
        raise AIError("The model took too long to answer. Try a shorter request.", 504)
    if r.status_code == 404:
        raise AIError(f"Model '{config.OLLAMA_MODEL}' not found. Run `ollama list` to verify it.", 503)
    if not r.ok:
        raise AIError("Ollama returned an error while generating.", 502)
    try:
        text = r.json()["message"]["content"].strip()
    except (ValueError, KeyError, TypeError):
        raise AIError("Ollama sent an unreadable response.", 502)
    if not text:
        raise AIError("The model returned an empty answer. Try again.", 502)
    return text

def status():
    try:
        r = requests.get(config.OLLAMA_URL + "/api/tags", timeout=3)
        names = [m.get("name", "") for m in r.json().get("models", [])]
    except Exception:
        return {"online": False, "model": config.OLLAMA_MODEL, "model_ready": False,
                "hint": "Ollama is not reachable. Start the Ollama app or run `ollama serve`."}
    ready = any(n == config.OLLAMA_MODEL or n.split(":")[0] == config.OLLAMA_MODEL for n in names)
    return {"online": True, "model": config.OLLAMA_MODEL, "model_ready": ready,
            "hint": "" if ready else f"Model not installed. Run `ollama list` and check '{config.OLLAMA_MODEL}'."}
