from test_helpers import IsolatedDatabaseTestCase

from database.db import get_connection
from modules.project_service import create_project
from modules.theme_service import ensure_theme, get_theme, update_theme


class ThemeTests(IsolatedDatabaseTestCase):

    def test_update_theme_changes_project_theme(self):

        project_id = create_project(
            "Theme Project",
            "Testing themes"
        )

        update_theme(
            project_id,
            "Georgia",
            "#111111",
            "#222222",
            "#333333",
            "#444444"
        )

        theme = get_theme(project_id)

        self.assertEqual("Georgia", theme["font_family"])
        self.assertEqual("#333333", theme["background_color"])

    def test_ensure_theme_creates_default_for_legacy_project(self):

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO projects
            (
                name,
                description,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "Legacy Project",
                "No theme row",
                "2026-01-01T00:00:00",
                "2026-01-01T00:00:00"
            )
        )
        project_id = cursor.lastrowid
        connection.commit()
        connection.close()

        theme = ensure_theme(project_id)

        self.assertEqual("Arial", theme["font_family"])
        self.assertEqual("#ffffff", theme["background_color"])


if __name__ == "__main__":
    import unittest

    unittest.main()
