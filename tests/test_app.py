import os, sys, tempfile, unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config, requests
config.DB_PATH = os.path.join(tempfile.mkdtemp(), "t.db")
from app import create_app

class T(unittest.TestCase):
    def setUp(self):
        if os.path.exists(config.DB_PATH): os.remove(config.DB_PATH)
        self.c = create_app().test_client()
    def test_home(self): self.assertEqual(self.c.get("/").status_code, 200)
    def test_empty_message(self): self.assertEqual(self.c.post("/api/chat", json={"message": "  "}).status_code, 400)
    def test_bad_json(self): self.assertEqual(self.c.post("/api/chat", data="x").status_code, 400)
    def test_bad_personality(self): self.assertEqual(self.c.post("/api/chat", json={"message": "hi", "personality": "x"}).status_code, 400)
    @patch("ai_service.requests.post", side_effect=requests.ConnectionError)
    def test_ollama_down(self, _): self.assertEqual(self.c.post("/api/chat", json={"message": "hi"}).status_code, 503)
    @patch("ai_service.requests.post")
    def test_chat_stores(self, post):
        post.return_value.ok = True; post.return_value.status_code = 200
        post.return_value.json.return_value = {"message": {"content": "Boo"}}
        r = self.c.post("/api/chat", json={"message": "hi"}).get_json()
        self.assertEqual(r["reply"], "Boo")
        conv = self.c.get(f"/api/conversations/{r['conversation_id']}").get_json()
        self.assertEqual(len(conv["messages"]), 2)
        self.c.delete(f"/api/conversations/{r['conversation_id']}")
        self.assertEqual(self.c.get("/api/conversations").get_json(), [])
    def test_memory(self):
        mid = self.c.post("/api/memories", json={"content": "Prefers Python"}).get_json()["id"]
        self.assertEqual(len(self.c.get("/api/memories").get_json()), 1)
        self.assertEqual(self.c.post("/api/memories", json={"content": "my password is abc"}).status_code, 400)
        self.c.delete(f"/api/memories/{mid}")
        self.assertEqual(self.c.get("/api/memories").get_json(), [])
    @patch("ai_service.requests.get", side_effect=requests.ConnectionError)
    def test_status_offline(self, _): self.assertFalse(self.c.get("/api/status").get_json()["online"])
    def test_story_validation(self): self.assertEqual(self.c.post("/api/story", json={"setting": "x", "type": "bad"}).status_code, 400)

if __name__ == "__main__": unittest.main()
