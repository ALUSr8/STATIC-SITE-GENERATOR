import os
import secrets
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import db


class IsolatedDatabaseTestCase(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.previous_database = db.DATABASE_NAME
        self.previous_cwd = os.getcwd()
        self.default_username = f"test-{secrets.token_hex(8)}"
        self.default_password = secrets.token_urlsafe(16)

        db.DATABASE_NAME = str(
            self.temp_path / "sitegen.db"
        )

        os.chdir(
            self.temp_path
        )

        (self.temp_path / "user_uploads").mkdir()

        db.DEFAULT_USERNAME = None
        db.DEFAULT_PASSWORD = None
        db.initialize_database()

        import modules.auth_service as auth_service
        create_user = auth_service.create_user
        create_user(self.default_username, self.default_password)
        db.DEFAULT_USERNAME = self.default_username
        db.DEFAULT_PASSWORD = self.default_password
        auth_service.DEFAULT_USERNAME = self.default_username

        from app import app
        app.config["TESTING"] = True

    def tearDown(self):

        os.chdir(
            self.previous_cwd
        )

        db.DATABASE_NAME = self.previous_database
        self.temp_dir.cleanup()

    def sign_in_default_user(self, client):

        return client.post(
            "/login",
            data={
                "username": self.default_username,
                "password": self.default_password
            },
            follow_redirects=True
        )
