from test_helpers import IsolatedDatabaseTestCase

import os


class RouteTests(IsolatedDatabaseTestCase):

    def test_homepage_and_projects_page_load(self):

        from app import app

        client = app.test_client()

        login_page = client.get(
            "/",
            follow_redirects=True
        )

        self.assertIn(
            b"Sign in to TemplateForge",
            login_page.data
        )

        self.sign_in_default_user(
            client
        )

        home_response = client.get("/")
        projects_response = client.get("/projects")

        self.assertEqual(200, home_response.status_code)
        self.assertEqual(200, projects_response.status_code)

    def test_project_form_creates_project_and_page_form_creates_page(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        project_response = client.post(
            "/projects/new",
            data={
                "project_name": "Route Project",
                "project_description": "Created through route"
            },
            follow_redirects=True
        )

        self.assertEqual(200, project_response.status_code)
        self.assertIn(
            b"Route Project",
            project_response.data
        )

        page_response = client.post(
            "/projects/1/pages/new",
            data={
                "page_title": "Contact"
            },
            follow_redirects=True
        )

        self.assertEqual(200, page_response.status_code)
        self.assertIn(
            b"Contact",
            page_response.data
        )

    def test_new_editor_component_renders(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        client.post(
            "/projects/new",
            data={
                "project_name": "Editor Project",
                "project_description": "Component route"
            },
            follow_redirects=True
        )

        response = client.get(
            "/pages/1/add/features",
            follow_redirects=True
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(
            b"Feature Grid added.",
            response.data
        )
        self.assertIn(
            b"What you get",
            response.data
        )

    def test_editor_component_can_move_up_and_down(self):

        from app import app
        from modules.component_service import get_components_by_page

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        client.post(
            "/projects/new",
            data={
                "project_name": "Reorder Project",
                "project_description": "Component order"
            },
            follow_redirects=True
        )

        client.get(
            "/pages/1/add/hero",
            follow_redirects=True
        )
        response = client.get(
            "/pages/1/add/footer",
            follow_redirects=True
        )

        self.assertIn(
            b"Move Up",
            response.data
        )
        self.assertIn(
            b"Move Down",
            response.data
        )

        components = get_components_by_page(1)
        footer_id = components[1]["id"]

        client.post(
            f"/components/{footer_id}/move/up",
            follow_redirects=True
        )

        moved_components = get_components_by_page(1)
        self.assertEqual(
            "footer",
            moved_components[0]["component_type"]
        )

        client.post(
            f"/components/{footer_id}/move/down",
            follow_redirects=True
        )

        restored_components = get_components_by_page(1)
        self.assertEqual(
            "hero",
            restored_components[0]["component_type"]
        )

    def test_export_route_opens_generated_site_handoff(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        client.post(
            "/projects/new",
            data={
                "project_name": "Export Route Project",
                "project_description": "Route export"
            },
            follow_redirects=True
        )

        response = client.get(
            "/projects/1/export"
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(
            b"Opening exported site",
            response.data
        )
        self.assertIn(
            b"EXPORT WAS COMPLETED",
            response.data
        )
        self.assertIn(
            b"Exported project folder:",
            response.data
        )
        self.assertIn(
            os.path.abspath(
                os.path.join(
                    "exports",
                    "Export Route Project"
                )
            ).encode(),
            response.data
        )

        exported_response = client.get(
            "/exports/Export%20Route%20Project/index.html"
        )

        self.assertEqual(200, exported_response.status_code)
        exported_response.close()

    def test_theme_editor_exposes_expanded_font_list(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        client.post(
            "/projects/new",
            data={
                "project_name": "Theme Fonts Project",
                "project_description": "Theme fonts"
            },
            follow_redirects=True
        )

        response = client.get("/projects/1/theme")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Segoe UI", response.data)
        self.assertIn(b"Open Sans", response.data)
        self.assertIn(b"Lato", response.data)

    def test_project_page_can_delete_extra_page_but_not_last_page(self):

        from app import app

        client = app.test_client()
        self.sign_in_default_user(
            client
        )

        client.post(
            "/projects/new",
            data={
                "project_name": "Page Delete Project",
                "project_description": "Route page delete"
            },
            follow_redirects=True
        )

        client.post(
            "/projects/1/pages/new",
            data={
                "page_title": "Home"
            },
            follow_redirects=True
        )

        delete_response = client.post(
            "/projects/1/pages/2/delete",
            follow_redirects=True
        )

        self.assertEqual(200, delete_response.status_code)
        self.assertIn(
            b"Page &#39;Home&#39; deleted.",
            delete_response.data
        )
        self.assertNotIn(
            b"/home",
            delete_response.data
        )

        final_page_response = client.post(
            "/projects/1/pages/1/delete",
            follow_redirects=True
        )

        self.assertEqual(200, final_page_response.status_code)
        self.assertIn(
            b"A project needs at least one page.",
            final_page_response.data
        )
