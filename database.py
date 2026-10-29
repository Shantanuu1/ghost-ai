import os, re, sqlite3
import config

SECRET = re.compile(r"(password|passwd|api[_ -]?key|token|secret|bearer|sk-[a-z0-9]{10,})", re.I)

def conn():
    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY, title TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)

def q(sql, args=(), one=False, commit=False):
    c = conn()
    try:
        cur = c.execute(sql, args)
        if commit:
            c.commit()
            return cur.lastrowid
        rows = [dict(r) for r in cur.fetchall()]
        return (rows[0] if rows else None) if one else rows
    finally:
        c.close()

def create_conversation(title="New haunting"):
    return q("INSERT INTO conversations(title) VALUES(?)", (title[:80],), commit=True)
def list_conversations():
    return q("SELECT * FROM conversations ORDER BY id DESC")
def get_conversation(cid):
    conv = q("SELECT * FROM conversations WHERE id=?", (cid,), one=True)
    if conv:
        conv["messages"] = q("SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id", (cid,))
    return conv
def rename_conversation(cid, title):
    q("UPDATE conversations SET title=? WHERE id=?", (title[:80], cid), commit=True)
def delete_conversation(cid):
    q("DELETE FROM conversations WHERE id=?", (cid,), commit=True)
def clear_conversations():
    q("DELETE FROM conversations", commit=True)
def add_message(cid, role, content):
    q("INSERT INTO messages(conversation_id, role, content) VALUES(?,?,?)", (cid, role, content), commit=True)
def recent_messages(cid, n):
    rows = q("SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT ?", (cid, n * 2))
    return rows[::-1]

def add_memory(text):
    if SECRET.search(text):
        raise ValueError("That looks like a secret (password, key or token). Ghost AI will not store it.")
    return q("INSERT INTO memories(content) VALUES(?)", (text,), commit=True)
def list_memories():
    return q("SELECT * FROM memories ORDER BY id DESC")
def delete_memory(mid):
    q("DELETE FROM memories WHERE id=?", (mid,), commit=True)
def clear_memories():
    q("DELETE FROM memories", commit=True)
