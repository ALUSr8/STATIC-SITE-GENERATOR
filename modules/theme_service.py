from database.db import get_connection
from modules.security import safe_theme_values

DEFAULT_THEME = {
    "font_family": "Arial",
    "primary_color": "#2563eb",
    "secondary_color": "#1e40af",
    "background_color": "#ffffff",
    "text_color": "#111111"
}


def create_default_theme(project_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO project_themes
        (
            project_id,
            font_family,
            primary_color,
            secondary_color,
            background_color,
            text_color
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            DEFAULT_THEME["font_family"],
            DEFAULT_THEME["primary_color"],
            DEFAULT_THEME["secondary_color"],
            DEFAULT_THEME["background_color"],
            DEFAULT_THEME["text_color"]
        )
    )

    connection.commit()
    connection.close()

    return get_theme(project_id)

def get_theme(project_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM project_themes
        WHERE project_id = ?
        """,
        (project_id,)
    )

    theme = cursor.fetchone()

    connection.close()

    if theme:
       theme = dict(theme)
       theme.update(
           safe_theme_values(
               theme["font_family"],
               theme["primary_color"],
               theme["secondary_color"],
               theme["background_color"],
               theme["text_color"]
           )
       )
       return theme

    return None

def ensure_theme(project_id):

    theme = get_theme(project_id)

    if theme is not None:
       return theme

    return create_default_theme(project_id)

def update_theme(
    project_id,
    font_family,
    primary_color,
    secondary_color,
    background_color,
    text_color
):

    theme = safe_theme_values(
        font_family,
        primary_color,
        secondary_color,
        background_color,
        text_color
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE project_themes
        SET
            font_family = ?,
            primary_color = ?,
            secondary_color = ?,
            background_color = ?,
            text_color = ?
        WHERE project_id = ?
        """,
        (
            theme["font_family"],
            theme["primary_color"],
            theme["secondary_color"],
            theme["background_color"],
            theme["text_color"],
            project_id
        )
    )

    connection.commit()
    connection.close()
