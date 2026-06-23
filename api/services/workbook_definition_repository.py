import json
import sqlite3
import logging

from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkbookDefinitionRepository:

    """
    Repository layer responsible for
    persisting and retrieving workbook
    definition artifacts.
    """

    def __init__(
        self,
        db_path
    ):

        self.db_path = db_path

        logger.info(
            (
                "Initializing workbook "
                "definition repository "
                "at %s"
            ),
            self.db_path
        )

        self._initialize_table()

    # ========================================
    # Table Initialization
    # ========================================

    def _initialize_table(
        self
    ):

        logger.info(
            (
                "Initializing workbook "
                "definition table"
            )
        )

        try:

            conn = sqlite3.connect(
                str(self.db_path)
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                workbook_definition (

                    workbook_definition_id TEXT
                        PRIMARY KEY,

                    workbook_name TEXT
                        NOT NULL,

                    format_name TEXT
                        NOT NULL,

                    version INTEGER
                        NOT NULL,

                    created_at TEXT
                        NOT NULL,

                    is_active INTEGER
                        DEFAULT 1,

                    definition_json TEXT
                        NOT NULL
                )
                """
            )

            conn.commit()

            conn.close()

            logger.info(
                (
                    "Workbook definition "
                    "table initialized "
                    "successfully"
                )
            )

        except Exception:

            logger.exception(
                (
                    "Failed initializing "
                    "workbook definition "
                    "table"
                )
            )

            raise

    # ========================================
    # Save Workbook Definition
    # ========================================

    def save_definition(
        self,
        workbook_name,
        format_name,
        workbook_definition
    ):

        logger.info(
            (
                "Saving workbook definition "
                "for workbook %s format %s"
            ),
            workbook_name,
            format_name
        )

        try:

            version = self.get_next_version(
                workbook_name=workbook_name,
                format_name=format_name
            )

            workbook_definition_id = str(
                uuid4()
            )

            created_at = (
                datetime.utcnow().isoformat()
            )

            definition_json = json.dumps(
                workbook_definition,
                indent=4
            )

            conn = sqlite3.connect(
                str(self.db_path)
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO workbook_definition (

                    workbook_definition_id,
                    workbook_name,
                    format_name,
                    version,
                    created_at,
                    is_active,
                    definition_json

                )

                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workbook_definition_id,
                    workbook_name,
                    format_name,
                    version,
                    created_at,
                    1,
                    definition_json
                )
            )

            conn.commit()

            conn.close()

            logger.info(
                (
                    "Workbook definition "
                    "saved successfully "
                    "with ID %s version %s"
                ),
                workbook_definition_id,
                version
            )

            return workbook_definition_id

        except Exception:

            logger.exception(
                (
                    "Failed saving workbook "
                    "definition for workbook "
                    "%s format %s"
                ),
                workbook_name,
                format_name
            )

            raise

    # ========================================
    # Load Workbook Definition
    # ========================================

    def load_definition(
        self,
        workbook_definition_id
    ):

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                workbook_definition_id,
                workbook_name,
                format_name,
                version,
                created_at,
                is_active,
                definition_json

            FROM workbook_definition

            WHERE workbook_definition_id = ?
            """,
            (
                workbook_definition_id,
            )
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:

            raise ValueError(
                (
                    "Workbook definition "
                    "not found"
                )
            )

        return {

            "workbook_definition_id":
                row[0],

            "workbook_name":
                row[1],

            "format_name":
                row[2],

            "version":
                row[3],

            "created_at":
                row[4],

            "is_active":
                bool(row[5]),

            "workbook_definition":
                json.loads(row[6])
        }

    # ========================================
    # List Workbook Definitions
    # ========================================

    def list_definitions(
        self
    ):

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                workbook_definition_id,
                workbook_name,
                format_name,
                version,
                created_at,
                is_active

            FROM workbook_definition

            ORDER BY
                workbook_name,
                format_name,
                version DESC
            """
        )

        rows = cursor.fetchall()

        conn.close()

        definitions = []

        for row in rows:

            definitions.append({

                "workbook_definition_id":
                    row[0],

                "workbook_name":
                    row[1],

                "format_name":
                    row[2],

                "version":
                    row[3],

                "created_at":
                    row[4],

                "is_active":
                    bool(row[5])
            })

        return definitions

    # ========================================
    # Version Management
    # ========================================

    def get_next_version(
        self,
        workbook_name,
        format_name
    ):

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT MAX(version)

            FROM workbook_definition

            WHERE workbook_name = ?
                AND format_name = ?
            """,
            (
                workbook_name,
                format_name
            )
        )

        row = cursor.fetchone()

        conn.close()

        max_version = row[0]

        if max_version is None:

            return 1

        return max_version + 1