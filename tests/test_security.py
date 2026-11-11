from io import BytesIO
from pathlib import Path
import re

from test_helpers import IsolatedDatabaseTestCase

from modules.component_service import create_component
from modules.export_service import export_project
from modules.page_service import get_pages_by_project
from modules.project_service import create_project, get_project_by_id
from modules.security import safe_link_url, safe_theme_values


class SecurityTests(IsolatedDatabaseTestCase):

    def test_unsafe_links_and_theme_values_are_normalized(self):

        self.assertEqual("#", safe_link_url("javascript:alert(1)"))
        self.assertEqual("#", safe_link_url("//example.com"))
        self.assertEqual("mailto:hello@example.com", safe_link_url("mailto:hello@example.com"))

        theme = safe_theme_values(
            "<script>",
            "red; background: url(javascript:alert(1))",
            "#123456",
            "#abcdef",
            "#000000"
        )

        self.assertEqual("Arial", theme["font_family"])
        self.assertEqual("#2563eb", theme["primary_color"])

    def test_export_escapes_content_and_rejects_javascript_links(self):

        project_id = create_project("Security Project", "Export test")
        page = get_pages_by_project(project_id)[0]
        create_component(
            page_id=page["id"],
            component_type="cta",
            component_data={
                "headline": "<script>alert(1)</script>",
                "button_text": "Open",
                "button_url": "javascript:alert(1)"
            },
            display_order=1
        )

        export_folder = Path(export_project(get_project_by_id(project_id)))
        html = (export_folder / "index.html").read_text(encoding="utf-8")

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn('href="#"', html)
        self.assertNotIn('href="javascript:', html)

    def test_invalid_image_content_is_rejected(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(client)

        response = client.post(
            "/upload-image",
            data={"image": (BytesIO(b"not an image"), "photo.jpg")},
            content_type="multipart/form-data",
            follow_redirects=True
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Upload a valid JPG, PNG, GIF, or WebP image.", response.data)
        self.assertEqual([], list(Path("user_uploads").iterdir()))

    def test_csrf_token_is_required_outside_testing(self):

        from app import app

        app.config["TESTING"] = False
        client = app.test_client()
        response = client.post(
            "/login",
            data={
                "username": self.default_username,
                "password": self.default_password
            }
        )

        self.assertEqual(400, response.status_code)

        login_page = client.get("/login")
        token = re.search(
            rb'name="_csrf_token" value="([^"]+)"',
            login_page.data
        ).group(1).decode()
        authenticated = client.post(
            "/login",
            data={
                "username": self.default_username,
                "password": self.default_password,
                "_csrf_token": token
            }
        )

        self.assertEqual(302, authenticated.status_code)
        app.config["TESTING"] = True

