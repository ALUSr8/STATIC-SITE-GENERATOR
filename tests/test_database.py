from test_helpers import IsolatedDatabaseTestCase

from modules.component_service import create_component, get_components_by_page
from modules.page_service import get_pages_by_project
from modules.project_service import create_project, delete_project, get_all_projects
from modules.theme_service import get_theme


class DatabaseTests(IsolatedDatabaseTestCase):

    def test_create_project_seeds_home_page_and_theme(self):

        project_id = create_project(
            "Test Project",
            "Testing database layer"
        )

        projects = get_all_projects()
        pages = get_pages_by_project(project_id)
        theme = get_theme(project_id)

        self.assertEqual(1, len(projects))
        self.assertEqual("Test Project", projects[0]["name"])
        self.assertEqual("index", pages[0]["slug"])
        self.assertEqual("#2563eb", theme["primary_color"])

    def test_delete_project_removes_pages_theme_and_components(self):

        project_id = create_project(
            "Delete Project",
            "Testing project deletion"
        )
        page = get_pages_by_project(project_id)[0]

        create_component(
            page_id=page["id"],
            component_type="hero",
            component_data={
                "title": "Delete",
                "subtitle": "Me"
            },
            display_order=1
        )

        delete_project(
            project_id
        )

        self.assertEqual(0, len(get_all_projects()))
        self.assertEqual(0, len(get_pages_by_project(project_id)))
        self.assertEqual(0, len(get_components_by_page(page["id"])))
        self.assertIsNone(get_theme(project_id))


if __name__ == "__main__":
    import unittest

    unittest.main()
