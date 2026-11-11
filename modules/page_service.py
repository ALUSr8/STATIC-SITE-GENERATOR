from database.db import get_connection
import re


def slugify(value):

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower()
    ).strip("-")

    return slug or "page"


def create_page(
    project_id,
    title,
    slug
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO pages
        (
            project_id,
            title,
            slug,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            project_id,
            title,
            slug,
            "{}"
        )
    )

    connection.commit()

    connection.close()

def create_page_with_unique_slug(
    project_id,
    title
):

    base_slug = slugify(title)
    slug = base_slug
    suffix = 2

    existing_slugs = {
        page["slug"]
        for page in get_pages_by_project(project_id)
    }

    while slug in existing_slugs:
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    create_page(
        project_id,
        title,
        slug
    )

    return slug

def get_pages_by_project(
    project_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM pages
        WHERE project_id = ?
        ORDER BY id
        """,
        (project_id,)
    )

    pages = cursor.fetchall()

    connection.close()

    return pages

def get_page_by_id(page_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM pages
        WHERE id = ?
        """,
        (page_id,)
    )

    page = cursor.fetchone()

    connection.close()

    return page


def delete_page(page_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM components
        WHERE page_id = ?
        """,
        (page_id,)
    )

    cursor.execute(
        """
        DELETE FROM pages
        WHERE id = ?
        """,
        (page_id,)
    )

    connection.commit()

    connection.close()
