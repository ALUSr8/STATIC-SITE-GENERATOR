from test_helpers import IsolatedDatabaseTestCase

from modules.component_service import create_component, delete_component, get_components_by_page
from modules.page_service import get_pages_by_project
from modules.project_service import create_project


class ComponentInsertTests(IsolatedDatabaseTestCase):

    def test_create_component_persists_json_data(self):

        project_id = create_project(
            "Component Project",
            "Testing component storage"
        )
        page = get_pages_by_project(project_id)[0]

        create_component(
            page_id=page["id"],
            component_type="hero",
            component_data={
                "title": "Welcome",
                "subtitle": "My First Website"
            },
            display_order=1
        )

        components = get_components_by_page(page["id"])

        self.assertEqual(1, len(components))
        self.assertEqual("hero", components[0]["component_type"])
        self.assertEqual("Welcome", components[0]["component_data"]["title"])

    def test_delete_component_removes_it_from_page(self):

        project_id = create_project(
            "Delete Component Project",
            "Testing component deletion"
        )
        page = get_pages_by_project(project_id)[0]

        create_component(
            page_id=page["id"],
            component_type="text",
            component_data={
                "content": "Remove me"
            },
            display_order=1
        )

        component = get_components_by_page(page["id"])[0]

        delete_component(
            component["id"]
        )

        self.assertEqual(
            0,
            len(get_components_by_page(page["id"]))
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
