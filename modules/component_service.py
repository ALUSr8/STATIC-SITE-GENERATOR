from database.db import get_connection

import json


def create_component(
    page_id,
    component_type,
    component_data,
    display_order
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO components
        (
            page_id,
            component_type,
            component_data,
            display_order
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            page_id,
            component_type,
            json.dumps(component_data),
            display_order
        )
    )

    connection.commit()

    connection.close()

def get_components_by_page(
    page_id
):
    import json
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM components
        WHERE page_id = ?
        ORDER BY display_order
        """,
        (page_id,)
    )
    
    components = cursor.fetchall()

    component_list = []

    for component in components:

        component_dict = dict(component)

        component_dict["component_data"] = json.loads(
            component["component_data"]
        )

        component_list.append(
             component_dict
        )
  
    connection.close()

    return component_list

def get_component_by_id(component_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM components
        WHERE id = ?
        """,
        (component_id,)
    )

    component = cursor.fetchone()

    connection.close()

    if component is None:
        return None

    component_dict = dict(component)

    component_dict["component_data"] = json.loads(
        component["component_data"]
    )

    return component_dict
   
def update_component_data(
    component_id,
    component_data
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE components
        SET component_data = ?
        WHERE id = ?
        """,
        (
            json.dumps(component_data),
            component_id
        )
    )

    connection.commit()

    connection.close()


def update_component_order(
    component_id,
    display_order
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE components
        SET display_order = ?
        WHERE id = ?
        """,
        (
            display_order,
            component_id
        )
    )

    connection.commit()

    connection.close()


def delete_component(component_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM components
        WHERE id = ?
        """,
        (component_id,)
    )

    connection.commit()

    connection.close()
