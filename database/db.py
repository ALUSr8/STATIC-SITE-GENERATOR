import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

DATABASE_NAME = "database/sitegen.db"
DEFAULT_USERNAME = os.environ.get("TEMPLATEFORGE_DEFAULT_USERNAME")
DEFAULT_PASSWORD = os.environ.get("TEMPLATEFORGE_DEFAULT_PASSWORD")


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            has_seen_tutorial INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("PRAGMA table_info(projects)")
    project_columns = {
        column["name"]
        for column in cursor.fetchall()
    }

    if "user_id" not in project_columns:
        cursor.execute("""
            ALTER TABLE projects
            ADD COLUMN user_id INTEGER
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT NOT NULL,
            slug TEXT NOT NULL,
            content TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS components (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER,
        component_type TEXT NOT NULL,
        component_data TEXT NOT NULL,
        display_order INTEGER,
        FOREIGN KEY(page_id)
        REFERENCES pages(id)
    )
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER UNIQUE,
        font_family TEXT,
        primary_color TEXT,
        secondary_color TEXT,
        background_color TEXT,
        text_color TEXT,
        FOREIGN KEY(project_id)
        REFERENCES projects(id)
    )
""")

    default_user = None

    if DEFAULT_USERNAME and DEFAULT_PASSWORD:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (
                username,
                password_hash,
                has_seen_tutorial,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                DEFAULT_USERNAME,
                generate_password_hash(DEFAULT_PASSWORD),
                0,
                datetime.now().isoformat()
            )
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (DEFAULT_USERNAME,)
        )
        default_user = cursor.fetchone()

    if default_user is not None:
        cursor.execute(
            """
            UPDATE projects
            SET user_id = ?
            WHERE user_id IS NULL
            """,
            (default_user["id"],)
        )

    connection.commit()
    connection.close()
