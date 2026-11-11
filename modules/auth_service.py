from datetime import datetime

from flask import has_request_context, session
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import DEFAULT_USERNAME, get_connection


def create_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                has_seen_tutorial,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash(password),
                0,
                datetime.now().isoformat()
            )
        )
        user_id = cursor.lastrowid
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return user_id


def get_user_by_username(username):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()
    connection.close()

    return user


def get_user_by_id(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()
    connection.close()

    return user


def authenticate_user(username, password):

    user = get_user_by_username(username)

    if user is None:
        return None

    if not check_password_hash(
        user["password_hash"],
        password
    ):
        return None

    return user


def mark_tutorial_seen(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET has_seen_tutorial = 1
        WHERE id = ?
        """,
        (user_id,)
    )

    connection.commit()
    connection.close()


def get_default_user_id():

    user = get_user_by_username(DEFAULT_USERNAME)

    if user is None:
        return None

    return user["id"]


def get_current_user_id():

    if has_request_context():
        user_id = session.get("user_id")

        if user_id is not None:
            return user_id

    return get_default_user_id()
