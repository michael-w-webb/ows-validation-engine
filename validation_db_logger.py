import os, uuid, sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "validation_dev.db")

class ValidationDBLogger:

    """
    SQLite-backed logging and persistence layer for the validation engine.

    This class is responsible for recording validation runs, resolving and
    persisting participant identities, and logging normalized data values
    and validation violations to a SQLite database. It enables longitudinal
    tracking of participants and datasets across repeated validation runs.

    The logger supports:
      - Run-level tracking via unique ``run_id`` values
      - Deterministic person resolution using hashed identity keys
      - Persistent participant identifiers scoped to (person, dataset)
      - Column-level metadata normalization across sheets and datasets
      - Cell-level value history logging for post-normalization analysis
      - Structured violation logging with severity levels

    SQLite is configured for concurrent-safe access using WAL mode and
    foreign key enforcement. All timestamps are generated at write time
    using the database clock.

    Notes
    -----
    * This logger assumes the database schema already exists.
    * Identity resolution prioritizes strict and medium-strength keys;
      weak-name-only matching is intentionally disabled to avoid
      accidental merges.
    * All Pandas NA / NaN values are coerced to ``NULL`` prior to insertion.

    Typical usage
    -------------
    >>> logger = ValidationDBLogger()
    >>> run_id = logger.start_run(
    ...     dataset_name="Q2 Submission",
    ...     org="EWIB",
    ...     quarter="2025Q2"
    ... )
    >>> person_id = logger.resolve_person(row)
    >>> participant_id = logger.get_or_create_participant(
    ...     person_id, dataset_name="Q2 Submission"
    ... )

    This class is designed to be called by higher-level orchestration
    components (e.g., validation engines, workbook loaders) rather than
    directly by end users.
    """

    def __init__(self):

        """
        Initialize a SQLite connection for validation logging.

        Opens a connection to the validation database and configures
        SQLite pragmas to support concurrent access and safe writes.

        Configuration applied:
        - Foreign key enforcement enabled
        - WAL journal mode for concurrent readers/writers
        - NORMAL synchronous mode for performance/safety balance

        Notes
        -----
        The database file is expected to exist and have a valid schema.
        This constructor does not create or migrate tables.
        """

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.commit()

    def _clean_sql_value(self, v):

        """
        Normalize Python and Pandas missing values for SQLite insertion.

        Converts Pandas NA, NaN, and ``None`` values to ``NULL`` so they
        can be safely written to SQLite columns.

        Parameters
        ----------
        v : Any
            A value originating from Pandas or Python objects.

        Returns
        -------
        Any or None
            ``None`` if the value represents missing data; otherwise
            the original value.
        """

        if v is pd.NA or v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        return v

    def start_run(self, dataset_name, org, quarter, triggered_by=None):

        """
        Create and persist a new validation run.

        Inserts a new row into the ``validation_run`` table and returns
        a unique ``run_id`` that should be used to associate all
        subsequent logging activity for this run.

        Parameters
        ----------
        dataset_name : str
            Logical name of the dataset submission.
        org : str
            Submitting organization.
        quarter : str
            Reporting quarter (e.g. ``"2025Q2"``).
        triggered_by : str, optional
            Identifier for the process or user that initiated the run.

        Returns
        -------
        str
            UUID string identifying the validation run.
        """

        run_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO validation_run (run_id, dataset_name, organization, quarter, triggered_by) VALUES (?, ?, ?, ?, ?)",
            (run_id, dataset_name, org, quarter, triggered_by),
        )
        self.conn.commit()
        return run_id

    def get_or_create_column(self, dataset_name, sheet_name, column_name):

        """
        Retrieve or create a normalized column identifier.

        Ensures that each logical (dataset, sheet, column) combination
        is represented by a single persistent ``column_id`` across runs.

        Parameters
        ----------
        dataset_name : str
            Dataset to which the column belongs.
        sheet_name : str
            Sheet name within the dataset.
        column_name : str
            Column name as it appears in the sheet.

        Returns
        -------
        str
            UUID string identifying the column.
        """

        cur = self.conn.execute(
            "SELECT column_id FROM dataset_column WHERE dataset_name=? AND sheet_name=? AND column_name=?",
            (dataset_name, sheet_name, column_name)
        )
        row = cur.fetchone()
        if row:
            return row[0]

        column_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO dataset_column (column_id, dataset_name, sheet_name, column_name) VALUES (?, ?, ?, ?)",
            (column_id, dataset_name, sheet_name, column_name)
        )
        self.conn.commit()
        return column_id

    def get_person_by_key(self, key_field, key_value):

        """
        Retrieve a person record using a hashed identity key.

        Parameters
        ----------
        key_field : str
            Name of the identity key column (e.g.
            ``id_key_strict_name_dob_zip``).
        key_value : str
            Hashed identity key value.

        Returns
        -------
        tuple or None
            The full ``person`` row if a match is found, otherwise ``None``.
        """

        sql = f"SELECT * FROM person WHERE {key_field} = ?"
        cur = self.conn.execute(sql, (key_value,))
        return cur.fetchone()

    def insert_person(self, first, last, dob, zip_code,
                    strict_key, med_name_dob_key, med_name_zip_key, weak_key):

        """
        Insert a new person record into the database.

        Persists identifying information and associated hashed identity
        keys. Missing values are safely coerced to ``NULL``.

        Parameters
        ----------
        first : str
            First name.
        last : str
            Last name.
        dob : date or str
            Date of birth.
        zip_code : str
            ZIP code.
        strict_key : str
            Strict identity hash (name + DOB + ZIP).
        med_name_dob_key : str
            Medium identity hash (name + DOB).
        med_name_zip_key : str
            Medium identity hash (name + ZIP).
        weak_key : str
            Weak identity hash (name only).

        Returns
        -------
        str
            UUID string identifying the new person.
        """


        clean = self._clean_sql_value  # shortcut alias
    
        person_id = str(uuid.uuid4())

        self.conn.execute("""
            INSERT INTO person (
                person_id,
                first_name, last_name, dob, zip,
                id_key_strict_name_dob_zip,
                id_key_medium_name_dob,
                id_key_medium_name_zip,
                id_key_weak_name,
                created_timestamp, updated_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            person_id,
            clean(first), clean(last), clean(dob), clean(zip_code),
            clean(strict_key),
            clean(med_name_dob_key),
            clean(med_name_zip_key),
            clean(weak_key)
        ))

        self.conn.commit()
        return person_id

    
    def resolve_person(self, row):

        """
        Resolve or create a person record for a given data row.

        Attempts to match an existing person using a hierarchy of
        identity keys in decreasing order of confidence:

        1. Strict (name + DOB + ZIP)
        2. Medium (name + DOB)
        3. Medium (name + ZIP)

        Weak (name-only) matching is intentionally disabled to avoid
        accidental merges. If no match is found, a new person record
        is created.

        Parameters
        ----------
        row : dict-like
            Normalized row containing identity keys and demographic fields.

        Returns
        -------
        str
            UUID string identifying the resolved or newly created person.
        """        

        # Extract keys
        strict    = row.get("id_key_strict_name_dob_zip")
        med_dob   = row.get("id_key_medium_name_dob")
        med_zip   = row.get("id_key_medium_name_zip")
        weak      = row.get("id_key_weak_name")

        # 1️⃣ strict match
        if strict:
            person = self.get_person_by_key("id_key_strict_name_dob_zip", strict)
            if person:
                return person[0]  # person_id

        # 2️⃣ medium (name + dob)
        if med_dob:
            person = self.get_person_by_key("id_key_medium_name_dob", med_dob)
            if person:
                return person[0]

        # 3️⃣ medium (name + zip)
        if med_zip:
            person = self.get_person_by_key("id_key_medium_name_zip", med_zip)
            if person:
                return person[0]

        ## Not linking on weak, even if only one match. Too risky. 
        # # 4️⃣ weak (name only)
        # if weak:
        #     cur = self.conn.execute(
        #         "SELECT person_id FROM person WHERE id_key_weak_name = ?",
        #         (weak,)
        #     )
        #     rows = cur.fetchall()
        #     if len(rows) == 1:  # safe fallback
        #         return rows[0][0]

        # 5️⃣ No match → create new person
        return self.insert_person(
            first=row.get("First Name"),
            last=row.get("Last Name"),
            dob=row.get("Client Date of Birth"),
            zip_code=row.get("Zip Code"),
            strict_key=strict,
            med_name_dob_key=med_dob,
            med_name_zip_key=med_zip,
            weak_key=weak
        )

    
    def get_or_create_participant(
        self,
        person_id,
        dataset_name,
        org=None):

        """
        Retrieve or create a persistent participant identifier.

        A participant represents a specific person's presence within
        a given dataset. The identifier is stable across runs and reused
        whenever the same (person, dataset) pair is encountered.

        Parameters
        ----------
        person_id : str
            Identifier of the resolved person.
        dataset_name : str
            Dataset to which the participant belongs.
        sheet_name : str, optional
            Sheet name where the participant appears.
        org : str, optional
            Organization associated with the participant.
        quarter : str, optional
            Reporting quarter.

        Returns
        -------
        str
            UUID string identifying the participant.
        """

        # 1. Try fetch existing participant
        cur = self.conn.execute("""
            SELECT participant_id 
            FROM participant
            WHERE person_id=? AND dataset_name=? AND org=?
        """, (person_id, dataset_name, org))

        row = cur.fetchone()
        if row:
            return row[0]  # <-- existing persistent participant_id

        # 2. Create new participant
        participant_id = str(uuid.uuid4())

        self.conn.execute("""
            INSERT INTO participant (
                participant_id, person_id, dataset_name, org
            ) VALUES (?, ?, ?, ?)
        """, (participant_id, person_id, dataset_name, org))

        self.conn.commit()
        return participant_id
    
    def mark_presence_participant(self, run_id, participant_id, status, row_number, sheet_name, quarter):
        
        """
        Record participant presence or absence for a validation run.

        Writes to ``participant_presence_log`` using a composite key
        of (run_id, participant_id), allowing presence state to be
        updated idempotently.

        Parameters
        ----------
        run_id : str
            Validation run identifier.
        participant_id : str
            Participant identifier.
        status : str
            Presence status (e.g. ``"present"``, ``"missing"``).
        """

        self.conn.execute(
            """
            INSERT OR REPLACE INTO participant_presence_log
                (run_id, participant_id, status, row_number, sheet_name, quarter, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (run_id, participant_id, status, row_number, sheet_name, quarter)
        )

        self.conn.commit()


    def bulk_log_cell_history(self, records):

        """
        Bulk insert cell-level value history records.

        Parameters
        ----------
        records : list of dict
            Each record represents a single cell value observation
            with associated run, participant, and column identifiers.

        Notes
        -----
        This method performs no validation; it assumes records are
        already normalized and schema-compliant.
        """

        df = pd.DataFrame(records)
        if not df.empty:
            df.to_sql("cell_value_history", self.conn, if_exists="append", index=False)

    def log_all_normalized_cell_values(
        logger,
        run_id,
        dataset_name,
        normalized_data,   # dict: sheet_name → normalized df
        id_df              # identity df containing id_key, person_id, participant_id
    ):
        
        """
        Log normalized cell values for all sheets in a dataset.

        Aligns rows from normalized dataframes to participants using
        identity keys, then records normalized values for each
        non-metadata column.

        Parameters
        ----------
        logger : ValidationDBLogger
            Active logger instance.
        run_id : str
            Validation run identifier.
        dataset_name : str
            Dataset being logged.
        normalized_data : dict
            Mapping of ``sheet_name`` to normalized Pandas DataFrames.
        id_df : pandas.DataFrame
            DataFrame containing ``id_key`` to ``participant_id`` mappings.
        """

        # -------------------------------------------------------
        # 1. Build a lookup table: id_key → participant_id
        # -------------------------------------------------------
        key_to_participant = (
            id_df[["id_key", "participant_id"]]
            .dropna(subset=["participant_id"])
            .set_index("id_key")["participant_id"]
            .to_dict()
        )

        # -------------------------------------------------------
        # 2. Loop through each normalized sheet
        # -------------------------------------------------------
        for sheet_name, df_norm in normalized_data.items():

            if "id_key" not in df_norm.columns:
                print(f"[WARN] Sheet '{sheet_name}' has no id_key column; skipping logging.")
                continue

            records = []

            # ---------------------------------------------------
            # 3. Loop through every row in this sheet
            # ---------------------------------------------------
            for idx, row in df_norm.iterrows():

                id_key = row["id_key"]

                # Skip rows with no matching participant
                participant_id = key_to_participant.get(id_key)
                if participant_id is None:
                    # Optionally accumulate untracked rows here
                    continue

                # ---------------------------------------------------
                # 4. Log every meaningful column except metadata
                # ---------------------------------------------------
                for col in df_norm.columns:
                    if col in ("id_key", "row_number", "person_id", "participant_id"):
                        continue

                    column_id = logger.get_or_create_column(
                        dataset_name=dataset_name,
                        sheet_name=sheet_name,
                        column_name=col
                    )

                    value_raw = None  # raw not available because this is post-normalization logging
                    value_norm = row[col]

                    records.append({
                        "history_id": uuid.uuid4().hex,
                        "run_id": run_id,
                        "participant_id": participant_id,
                        "column_id": column_id,
                        "value_raw": value_raw,
                        "value_normalized": value_norm
                    })

            # ---------------------------------------------------
            # 5. Bulk insert logs for this sheet
            # ---------------------------------------------------
            logger.bulk_log_cell_history(records)
    
    def log_violation(self, run_id, rule_id, participant_id,
                    column_id, normalized, raw_value, severity="error"):

        """
        Record a validation rule violation.

        Inserts a structured violation record capturing the rule,
        affected participant, column, and observed values.

        Parameters
        ----------
        run_id : str
            Validation run identifier.
        rule_id : int
            Identifier of the violated rule.
        participant_id : str
            Participant associated with the violation.
        column_id : str
            Column associated with the violation.
        normalized : Any
            Normalized value that triggered the violation.
        raw_value : Any
            Original raw value prior to normalization.
        severity : str, optional
            Severity level (default: ``"error"``).
        """
         
        violation_id = str(uuid.uuid4())
        
        clean = self._clean_sql_value
        
        self.conn.execute("""
            INSERT INTO validation_violation (
                violation_id, run_id, rule_id, participant_id,
                column_id, normalized, raw_value, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (violation_id, run_id, rule_id, participant_id,
            column_id, clean(normalized), clean(raw_value), severity))
        
        self.conn.commit()


    import uuid

    def log_key_mismatches(self, run_id, mismatches):
        """
        Persist unresolved identity-key mismatches detected during validation.

        Parameters
        ----------
        run_id : str
            Validation run identifier.
        mismatches : list[dict]
            Each dict must contain:
            org, period, sheet, id_key, issue
        """
        rows = [
            (
                str(uuid.uuid4()),
                run_id,
                m["org"],
                m["period"],
                m["sheet"],
                m["id_key"],
                m["issue"],
            )
            for m in mismatches
        ]

        self.conn.executemany(
            """
            INSERT INTO participant_key_mismatch (
                mismatch_id,
                run_id,
                org,
                quarter,
                sheet_name,
                id_key,
                issue
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows
        )
        self.conn.commit()

