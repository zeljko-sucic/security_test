from pathlib import Path
import re
import tempfile
import unittest

from helpdesk import create_app


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-only-key",
                               "DATABASE": str(Path(self.folder.name) / "test.sqlite3"),
                               "ATTACHMENT_DIR": str(Path(self.folder.name) / "attachments")})
        self.client = self.app.test_client()

    def token(self, page):
        return re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)

    def test_login_ticket_and_comment_flow(self):
        login = self.client.get("/login")
        response = self.client.post("/login", data={"email": "alice@northstar.example", "password": "ReviewLab-2026!",
                                                    "csrf_token": self.token(login)}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invoice export formatting", response.data)
        ticket = self.client.get("/tickets/1")
        response = self.client.post("/tickets/1/comments", data={"body": "Checked the sample.", "csrf_token": self.token(ticket)}, follow_redirects=True)
        self.assertIn(b"Checked the sample.", response.data)
        download = self.client.get("/attachments/1")
        self.addCleanup(download.close)
        self.assertEqual(download.status_code, 200)

    def test_login_required_and_form_token_required(self):
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/tickets/1").status_code, 302)
        self.assertEqual(self.client.post("/login", data={"email": "alice@northstar.example", "password": "ReviewLab-2026!"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
