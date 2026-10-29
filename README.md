# Ghost AI — Your Personal Haunted Assistant

A local AI web app for Hacktoberfest 2026 Week 4 ("Ghost in the Machine"). Flask + SQLite + vanilla JS, answering through `gemma4:e2b` on your own Ollama.

## Features
Chat with 3 personalities (Friendly, Mysterious, Nightmare) · coding assistant (explain, debug, error, optimize, learn; code is never executed) · horror story generator · summarizer · persistent memories you save yourself · conversation history (rename on double-click, delete with confirmation) · settings with a real Ollama status check.

## Architecture
`app.py` routes and validation · `ai_service.py` Ollama calls, personalities, status · `database.py` SQLite (parameterized queries) · `config.py` env settings · `static/` and `templates/` frontend. Memories you saved (max 20) are added to the system prompt; the last 10 turns of the conversation are sent as context.

## Windows setup
1. Install Ollama and confirm `ollama list` shows `gemma4:e2b`.
2. In the project folder:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```
3. Open http://127.0.0.1:5000
4. Tests (mocked Ollama, no model needed): `python -m unittest tests.test_app`

## Troubleshooting
- "Cannot reach Ollama": open the Ollama app or run `ollama serve`.
- "Model not found": run `ollama list`, then match `OLLAMA_MODEL` in `.env`.
- Slow replies on 8 GB RAM: close other apps, keep prompts short, raise `OLLAMA_TIMEOUT`.

## Privacy
Prompts go only to the Ollama service at `127.0.0.1` on your machine. The server binds to localhost, makes no third-party AI calls, and the browser never calls arbitrary URLs. Data lives in `instance/ghost.db` (git-ignored). The app is not a cloud service; if you deploy it, prompts would travel to wherever you host Ollama.

## Limitations
Replies are not streamed. Stop discards the reply in the browser; the model may still finish generating. Memory retrieval includes your newest 20 memories rather than semantic search. Single user, no login. Check the Gemma license terms yourself: open weights are not automatically fully open source.

## Future ideas
Token streaming, memory search, export/import, screenshots (`docs/screenshots/` placeholder), license (choose one before publishing).

---
# DEV draft
**Tags:** #devchallenge #hacktoberfest (confirm the exact challenge tags)
**What I built:** Ghost AI, a haunted assistant running Gemma through local Ollama.
**Demo:** [DEMO LINK]  **Code:** [GITHUB REPO]  **Screenshots:** [ADD]
**How I built it:** Flask, SQLite, vanilla JS; personalities swap the system prompt; memories are opt-in.
**Why open innovation matters:** I run, inspect and tune the model myself, with no paid API and prompts staying on my laptop.
**Spirit:** a ghost that lives in your machine and forgets nothing you didn't choose to keep.
