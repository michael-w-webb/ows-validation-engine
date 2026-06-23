import sqlite3

from api.config import WB_DEF_DB_PATH


OLD_NAME = "Charter Oak"
NEW_NAME = "Career ConneCT"


def rename_workbook_definitions():

    conn = sqlite3.connect(WB_DEF_DB_PATH)

    try:

        cursor = conn.cursor()

        # Preview affected rows
        cursor.execute(
            """
            SELECT
                workbook_definition_id,
                workbook_name,
                format_name,
                version
            FROM workbook_definition
            WHERE workbook_name = ?
            """,
            (OLD_NAME,)
        )

        rows = cursor.fetchall()

        print(
            f"Found {len(rows)} workbook definitions "
            f"matching '{OLD_NAME}'"
        )

        for row in rows:

            print(
                (
                    f"ID={row[0]} | "
                    f"Format={row[2]} | "
                    f"Version={row[3]}"
                )
            )

        # Perform update
        cursor.execute(
            """
            UPDATE workbook_definition

            SET
                workbook_name = ?,
                definition_json = REPLACE(
                    definition_json,
                    ?,
                    ?
                )

            WHERE workbook_name = ?
            """,
            (
                NEW_NAME,
                OLD_NAME,
                NEW_NAME,
                OLD_NAME
            )
        )

        conn.commit()

        print(
            f"\nUpdated {cursor.rowcount} rows "
            f"from '{OLD_NAME}' to '{NEW_NAME}'"
        )

    finally:

        conn.close()


if __name__ == "__main__":

    rename_workbook_definitions()