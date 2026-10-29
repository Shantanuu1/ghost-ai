from flask import Flask, jsonify, render_template, request
import config, database as db, ai_service as ai

STORY_TYPES = ["ghost story", "psychological", "found footage", "folk horror"]
CODE_MODES = {"explain": "Explain what this code does, step by step.",
              "debug": "Find bugs in this code, explain them, and give a corrected version.",
              "error": "Explain this error message, its likely cause and how to fix it.",
              "optimize": "Suggest an optimized or cleaner version and explain why.",
              "learn": "Teach this programming concept clearly with a short example."}
LANGS = ["Python", "Java", "C++", "JavaScript", "SQL", "Other"]

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
    db.init_db()

    def body():
        d = request.get_json(silent=True)
        if not isinstance(d, dict):
            raise ValueError("Request body must be a JSON object.")
        return d

    def text(d, key, required=True, maxlen=config.MAX_INPUT):
        v = d.get(key, "")
        if not isinstance(v, str):
            raise ValueError(f"'{key}' must be text.")
        v = v.strip()
        if required and not v:
            raise ValueError(f"'{key}' must not be empty.")
        if len(v) > maxlen:
            raise ValueError(f"'{key}' is too long (max {maxlen} characters).")
        return v

    def persona(d):
        p = d.get("personality", "friendly")
        if p not in ai.PERSONALITIES:
            raise ValueError("Unknown personality.")
        return p

    def mems():
        return [m["content"] for m in db.list_memories()[:20]]

    @app.errorhandler(ValueError)
    def bad(e):
        return jsonify(error=str(e)), 400
    @app.errorhandler(ai.AIError)
    def aierr(e):
        return jsonify(error=str(e)), e.status
    @app.errorhandler(404)
    def nf(e):
        return jsonify(error="Not found."), 404
    @app.errorhandler(Exception)
    def boom(e):
        app.logger.exception("Unhandled error")
        return jsonify(error="Something went wrong inside the machine."), 500

    @app.get("/")
    def index():
        return render_template("index.html", model=config.OLLAMA_MODEL)

    @app.get("/api/status")
    def status():
        return jsonify(ai.status())

    @app.get("/api/conversations")
    def convs():
        return jsonify(db.list_conversations())
    @app.post("/api/conversations")
    def new_conv():
        return jsonify(id=db.create_conversation()), 201
    @app.delete("/api/conversations")
    def clear_convs():
        db.clear_conversations()
        return jsonify(ok=True)
    @app.get("/api/conversations/<int:cid>")
    def get_conv(cid):
        c = db.get_conversation(cid)
        return (jsonify(c) if c else (jsonify(error="Conversation not found."), 404))
    @app.patch("/api/conversations/<int:cid>")
    def rename(cid):
        if not db.get_conversation(cid):
            return jsonify(error="Conversation not found."), 404
        db.rename_conversation(cid, text(body(), "title", maxlen=80))
        return jsonify(ok=True)
    @app.delete("/api/conversations/<int:cid>")
    def del_conv(cid):
        db.delete_conversation(cid)
        return jsonify(ok=True)

    @app.post("/api/chat")
    def chat():
        d = body()
        msg, p = text(d, "message"), persona(d)
        cid = d.get("conversation_id")
        if cid is None:
            cid = db.create_conversation(msg[:40])
        elif not isinstance(cid, int) or not db.get_conversation(cid):
            return jsonify(error="Conversation not found."), 404
        history = db.recent_messages(cid, config.HISTORY_TURNS)
        reply = ai.chat(history + [{"role": "user", "content": msg}], ai.system_prompt(p, mems()))
        db.add_message(cid, "user", msg)
        db.add_message(cid, "assistant", reply)
        return jsonify(conversation_id=cid, reply=reply)

    def one_shot(prompt, p, use_mem=False):
        return ai.chat([{"role": "user", "content": prompt}], ai.system_prompt(p, mems() if use_mem else ()))

    @app.post("/api/code")
    def code():
        d = body()
        mode, lang = d.get("mode"), d.get("language", "Python")
        if mode not in CODE_MODES or lang not in LANGS:
            raise ValueError("Invalid mode or language.")
        p = one_shot(f"Language: {lang}\nTask: {CODE_MODES[mode]}\n\n{text(d, 'code')}", persona(d))
        return jsonify(reply=p)

    @app.post("/api/story")
    def story():
        d = body()
        stype, intensity, length = d.get("type", "ghost story"), d.get("intensity", "medium"), d.get("length", "short")
        if stype not in STORY_TYPES or intensity not in ("mild", "medium", "intense") or length not in ("short", "medium", "long"):
            raise ValueError("Invalid story options.")
        words = {"short": 250, "medium": 500, "long": 800}[length]
        setting = text(d, "setting", maxlen=120)
        prompt = (f"Write an original {stype} of about {words} words set in: {setting}. Horror intensity: {intensity} "
                  "(atmospheric suspense; no gore for gore's sake). Give it a title and a satisfying ending.")
        return jsonify(reply=one_shot(prompt, "mysterious"))

    @app.post("/api/summarize")
    def summarize():
        d = body()
        return jsonify(reply=one_shot("Summarize the following text concisely with key points:\n\n" + text(d, "text"), persona(d)))

    @app.get("/api/memories")
    def memories():
        return jsonify(db.list_memories())
    @app.post("/api/memories")
    def add_mem():
        mid = db.add_memory(text(body(), "content", maxlen=300))
        return jsonify(id=mid), 201
    @app.delete("/api/memories/<int:mid>")
    def del_mem(mid):
        db.delete_memory(mid)
        return jsonify(ok=True)
    @app.delete("/api/memories")
    def clear_mem():
        db.clear_memories()
        return jsonify(ok=True)
    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
