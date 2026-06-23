import sqlite3
import uuid
import logging

from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class ValidationRunRepository:

    """
    Repository responsible for
    persisting validation run state
    and runtime metadata.
    """

    def __init__(
        self,
        db_path
    ):

        self.db_path = Path(
            db_path
        )

        logger.info(
            (
                "Initializing validation "
                "run repository at %s"
            ),
            self.db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
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
                "Initializing validation "
                "run table"
            )
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            CREATE TABLE IF NOT EXISTS validation_run (

                validation_run_id TEXT
                    PRIMARY KEY,

                workbook_definition_id TEXT
                    NOT NULL,

                workbook_name TEXT,

                format_name TEXT,

                org TEXT,

                target_period TEXT,

                status TEXT
                    NOT NULL,

                uploaded_file_path TEXT,

                output_file_path TEXT,

                runtime_seconds REAL,

                sheet_count INTEGER,

                normalized_row_count INTEGER,

                error_count INTEGER,

                mismatch_count INTEGER,

                failure_message TEXT,

                created_at TEXT
                    NOT NULL,

                completed_at TEXT
            )

            """
        )

        conn.commit()

        conn.close()

        logger.info(
            (
                "Validation run table "
                "initialized successfully"
            )
        )

    # ========================================
    # Create Validation Run
    # ========================================

    def create_run(
        self,
        workbook_definition_id,
        workbook_name,
        format_name,
        org,
        target_period,
        uploaded_file_path
    ):

        validation_run_id = str(
            uuid.uuid4()
        )

        created_at = (
            datetime.utcnow()
            .isoformat()
        )

        logger.info(
            (
                "Creating validation "
                "run %s"
            ),
            validation_run_id
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            INSERT INTO validation_run (

                validation_run_id,

                workbook_definition_id,

                workbook_name,

                format_name,

                org,

                target_period,

                status,

                uploaded_file_path,

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            """,

            (

                validation_run_id,

                workbook_definition_id,

                workbook_name,

                format_name,

                org,

                target_period,

                "queued",

                str(uploaded_file_path),

                created_at
            )
        )

        conn.commit()

        conn.close()

        logger.info(
            (
                "Validation run %s "
                "created successfully"
            ),
            validation_run_id
        )

        return validation_run_id

    # ========================================
    # Update Status
    # ========================================

    def update_status(
        self,
        validation_run_id,
        status
    ):

        logger.info(
            (
                "Updating validation "
                "run %s status to %s"
            ),
            validation_run_id,
            status
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            UPDATE validation_run

            SET status = ?

            WHERE validation_run_id = ?

            """,

            (
                status,
                validation_run_id
            )
        )

        conn.commit()

        conn.close()

    # ========================================
    # Complete Validation Run
    # ========================================

    def complete_run(
        self,
        validation_run_id,
        output_file_path,
        runtime_seconds,
        sheet_count,
        normalized_row_count,
        error_count,
        mismatch_count
    ):

        completed_at = (
            datetime.utcnow()
            .isoformat()
        )

        logger.info(
            (
                "Completing validation "
                "run %s"
            ),
            validation_run_id
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            UPDATE validation_run

            SET

                status = ?,

                output_file_path = ?,

                runtime_seconds = ?,

                sheet_count = ?,

                normalized_row_count = ?,

                error_count = ?,

                mismatch_count = ?,

                completed_at = ?

            WHERE validation_run_id = ?

            """,

            (

                "completed",

                str(output_file_path),

                runtime_seconds,

                sheet_count,

                normalized_row_count,

                error_count,

                mismatch_count,

                completed_at,

                validation_run_id
            )
        )

        conn.commit()

        conn.close()

        logger.info(
            (
                "Validation run %s "
                "completed successfully"
            ),
            validation_run_id
        )

    # ========================================
    # Fail Validation Run
    # ========================================

    def fail_run(
        self,
        validation_run_id,
        failure_message
    ):

        logger.exception(
            (
                "Validation run %s "
                "failed"
            ),
            validation_run_id
        )

        completed_at = (
            datetime.utcnow()
            .isoformat()
        )

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            UPDATE validation_run

            SET

                status = ?,

                failure_message = ?,

                completed_at = ?

            WHERE validation_run_id = ?

            """,

            (

                "failed",

                failure_message,

                completed_at,

                validation_run_id
            )
        )

        conn.commit()

        conn.close()

    # ========================================
    # Retrieve Single Run
    # ========================================

    def get_run(
        self,
        validation_run_id
    ):

        logger.info(
            (
                "Loading validation "
                "run %s"
            ),
            validation_run_id
        )

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = (
            sqlite3.Row
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            SELECT *

            FROM validation_run

            WHERE validation_run_id = ?

            """,

            (
                validation_run_id,
            )
        )

        row = cursor.fetchone()

        conn.close()

        if row is None:

            logger.warning(
                (
                    "Validation run %s "
                    "not found"
                ),
                validation_run_id
            )

            return None

        return dict(row)

    # ========================================
    # List Active Runs
    # ========================================

    def list_active_runs(
        self
    ):

        logger.info(
            "Loading active validation runs"
        )

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = (
            sqlite3.Row
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            SELECT *

            FROM validation_run

            WHERE status IN (
                'queued',
                'running'
            )

            ORDER BY created_at DESC

            """
        )

        rows = cursor.fetchall()

        conn.close()

        return [

            dict(row)

            for row in rows
        ]

    # ========================================
    # List Completed Runs
    # ========================================

    def list_completed_runs(
        self,
        limit=50
    ):

        logger.info(
            (
                "Loading completed "
                "validation runs"
            )
        )

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = (
            sqlite3.Row
        )

        cursor = conn.cursor()

        cursor.execute(
            """

            SELECT *

            FROM validation_run

            WHERE status IN (
                'completed',
                'failed'
            )

            ORDER BY completed_at DESC

            LIMIT ?

            """,

            (
                limit,
            )
        )

        rows = cursor.fetchall()

        conn.close()

        return [

            dict(row)

            for row in rows
        ]