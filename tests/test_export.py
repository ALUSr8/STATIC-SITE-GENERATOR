from pathlib import Path

from test_helpers import IsolatedDatabaseTestCase

from modules.component_service import create_component
from modules.export_service import export_project
from modules.page_service import create_page_with_unique_slug, get_pages_by_project
from modules.project_service import create_project, get_project_by_id


class ExportTests(IsolatedDatabaseTestCase):

    def test_export_writes_html_css_and_assets(self):

        project_id = create_project(
            "Export Project",
            "Testing static export"
        )
        page = get_pages_by_project(project_id)[0]
        create_page_with_unique_slug(
            project_id,
            "About Us"
        )
        pages = get_pages_by_project(project_id)
        about_page = pages[1]

        upload_path = Path("user_uploads") / "photo.jpg"
        upload_path.write_bytes(b"fake image bytes")

        create_component(
            page_id=page["id"],
            component_type="hero",
            component_data={
                "title": "Hello <World>",
                "subtitle": "Static site",
                "alignment": "right"
            },
            display_order=1
        )
        create_component(
            page_id=page["id"],
            component_type="image",
            component_data={
                "image_path": "photo.jpg",
                "alt_text": "Profile <photo>",
                "alignment": "left"
            },
            display_order=2
        )
        create_component(
            page_id=about_page["id"],
            component_type="text",
            component_data={
                "content": "About content"
            },
            display_order=1
        )
        create_component(
            page_id=about_page["id"],
            component_type="cta",
            component_data={
                "headline": "Book <Now>",
                "button_text": "Start",
                "button_url": "#contact"
            },
            display_order=2
        )
        create_component(
            page_id=about_page["id"],
            component_type="features",
            component_data={
                "heading": "Services",
                "items": "Design\nBuild",
                "size": "large"
            },
            display_order=3
        )
        create_component(
            page_id=about_page["id"],
            component_type="product_demo",
            component_data={
                "title": "Demo",
                "description": "Watch it work",
                "button_text": "Watch",
                "button_url": "#",
                "video_url": "https://youtu.be/example123",
                "size": "small"
            },
            display_order=4
        )

        export_folder = Path(
            export_project(
                get_project_by_id(project_id)
            )
        )

        html = (export_folder / "index.html").read_text(
            encoding="utf-8"
        )

        self.assertTrue((export_folder / "style.css").exists())
        self.assertTrue((export_folder / "about-us.html").exists())
        self.assertTrue((export_folder / "assets" / "photo.jpg").exists())
        self.assertIn("assets/photo.jpg", html)
        self.assertIn("about-us.html", html)
        self.assertIn("Hello &lt;World&gt;", html)
        self.assertIn("Profile &lt;photo&gt;", html)
        self.assertIn("hero size-medium align-right", html)
        self.assertIn("image-section size-medium align-left", html)

        about_html = (export_folder / "about-us.html").read_text(
            encoding="utf-8"
        )

        css = (export_folder / "style.css").read_text(
            encoding="utf-8"
        )

        self.assertIn("Book &lt;Now&gt;", about_html)
        self.assertIn("feature-section size-large", about_html)
        self.assertIn("product-demo-section size-small", about_html)
        self.assertIn("youtube.com/embed/example123", about_html)
        self.assertIn("cta-section", css)
        self.assertIn("site-button", css)
        self.assertIn("image-section.align-left", css)
        self.assertIn("gallery-section.align-right", css)


if __name__ == "__main__":
    import unittest

    unittest.main()
