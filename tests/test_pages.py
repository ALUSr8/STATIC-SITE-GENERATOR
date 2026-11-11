from test_helpers import IsolatedDatabaseTestCase

from modules.component_service import create_component, get_components_by_page
from modules.page_service import (
    create_page,
    create_page_with_unique_slug,
    delete_page,
    get_pages_by_project
)
from modules.project_service import create_project


class PageTests(IsolatedDatabaseTestCase):

    def test_create_page_adds_page_to_project(self):

        project_id = create_project(
            "Page Project",
            "Testing pages"
        )

        create_page(
            project_id,
            "About",
            "about"
        )

        pages = get_pages_by_project(project_id)
        slugs = [
            page["slug"]
            for page in pages
        ]

        self.assertEqual(["index", "about"], slugs)

    def test_create_page_with_unique_slug_deduplicates_slugs(self):

        project_id = create_project(
            "Slug Project",
            "Testing unique slugs"
        )

        first_slug = create_page_with_unique_slug(
            project_id,
            "About Us"
        )
        second_slug = create_page_with_unique_slug(
            project_id,
            "About Us"
        )

        self.assertEqual("about-us", first_slug)
        self.assertEqual("about-us-2", second_slug)

    def test_delete_page_removes_page_and_components(self):

        project_id = create_project(
            "Delete Page Project",
            "Testing page deletion"
        )

        create_page(
            project_id,
            "About",
            "about"
        )

        pages = get_pages_by_project(project_id)
        about_page = pages[1]

        create_component(
            page_id=about_page["id"],
            component_type="text",
            component_data={
                "content": "Remove me"
            },
            display_order=1
        )

        delete_page(
            about_page["id"]
        )

        remaining_slugs = [
            page["slug"]
            for page in get_pages_by_project(project_id)
        ]

        self.assertEqual(["index"], remaining_slugs)
        self.assertEqual(
            0,
            len(get_components_by_page(about_page["id"]))
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
