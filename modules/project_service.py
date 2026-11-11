from database.db import get_connection
from datetime import datetime
from modules.auth_service import get_current_user_id
from modules.page_service import create_page
from modules.theme_service import (
    create_default_theme
)

def create_project(name, description):

    connection = get_connection()

    cursor = connection.cursor()

    current_time = datetime.now().isoformat()
    user_id = get_current_user_id()

    cursor.execute(
        """
        INSERT INTO projects
        (
            user_id,
            name,
            description,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            name,
            description,
            current_time,
            current_time
        )
    )
    project_id = cursor.lastrowid

    connection.commit()
    connection.close()

    create_page(
        project_id,
        "Home",
        "index"
    )

    create_default_theme(
        project_id
    )

    return project_id

def get_all_projects():

    connection = get_connection()

    cursor = connection.cursor()
    user_id = get_current_user_id()

    cursor.execute(
        """
        SELECT *
        FROM projects
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """,
        (user_id,)
    )

    projects = cursor.fetchall()

    connection.close()

    return projects

def get_project_by_id(project_id):

    connection = get_connection()

    cursor = connection.cursor()
    user_id = get_current_user_id()

    cursor.execute(
        """
        SELECT *
        FROM projects
        WHERE id = ?
        AND user_id = ?
        """,
        (
            project_id,
            user_id
        )
    )

    project = cursor.fetchone()

    connection.close()

    return project

def delete_project(project_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM components
        WHERE page_id IN (
            SELECT id
            FROM pages
            WHERE project_id = ?
        )
        """,
        (project_id,)
    )

    cursor.execute(
        """
        DELETE FROM pages
        WHERE project_id = ?
        """,
        (project_id,)
    )

    cursor.execute(
        """
        DELETE FROM project_themes
        WHERE project_id = ?
        """,
        (project_id,)
    )

    cursor.execute(
        """
        DELETE FROM projects
        WHERE id = ?
        """,
        (project_id,)
    )

    connection.commit()
    connection.close()
