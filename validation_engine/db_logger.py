import os, uuid, sqlite3
from datetime import datetime
import pandas as pd
import datetime as dt
from config import DB_PATH
from validation_engine.column_names import (
    get_required_value,
    get_value,
    is_normalized,
    remove_normalized_suffix,
    sheet_name,
    base_name
)
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

    Persistence Model
    -----------------
    Some logging operations are buffered in memory and persisted in batches
    for performance reasons. Methods such as:

    - ``mark_presence_participant``
    - ``log_violation``
    - ``resolve_person`` (new people)
    - ``get_or_create_participant`` (new participants)

    defer database writes until their corresponding ``flush_*`` methods are
    called.

    This design reduces transaction overhead during large validation runs.

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
    def __init__(self, db_path = None):

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
        self._violation_buffer = []
        self._participant_presence_buffer = []
        self._column_cache = {}
        self._participant_cache = {}

        self._participant_map = {}
        self._new_participants_buffer = []

        self._person_by_strict = {}
        self._person_by_med_dob = {}
        self._person_by_med_zip = {}

        self._new_people_buffer = []

        self.keycreators = None

        self.raw_data_points = {}
        self.db_path = db_path or DB_PATH

        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.commit()

    #### some functions for mapping values: 

    def load_participant_map(
    self,
    dataset_name: str,
    org: str | None = None,
    ):
        """
        Preload participant identifiers into an in-memory lookup map.

        Loads existing participant records from the database into
        ``self._participant_map`` for O(1) participant resolution during
        validation.

        Keys are stored as:

            (person_id, dataset_name, org) -> participant_id

        Parameters
        ----------
        dataset_name : str
            Dataset scope to preload.
        org : str, optional
            If provided, restricts loading to a single organization.
            Otherwise all organizations for the dataset are loaded.

        Notes
        -----
        This method clears any previously loaded participant map state before
        loading new records.

        Typically called once at the beginning of a validation run to avoid
        repeated database lookups during participant resolution.
        """

        self._participant_map.clear()

        if org is None:
            sql = """
                SELECT participant_id, person_id, dataset_name, org
                FROM participant
                WHERE dataset_name = ?
            """
            params = (dataset_name,)
        else:
            sql = """
                SELECT participant_id, person_id, dataset_name, org
                FROM participant
                WHERE dataset_name = ? AND org = ?
            """
            params = (dataset_name, org)

        cur = self.conn.execute(sql, params)

        for participant_id, person_id, dataset_name, org in cur.fetchall():
            key = (person_id, dataset_name, org)
            self._participant_map[key] = participant_id

    def load_person_maps(self):

        """
        Preload deterministic identity-key maps into memory.

        Loads strict and medium-strength identity hashes from the ``person``
        table into in-memory dictionaries used during participant resolution.

        Loaded maps include:

        - strict: name + DOB + ZIP
        - medium: name + DOB
        - medium: name + ZIP

        Weak-name-only matching is intentionally excluded to reduce the risk
        of false-positive merges.

        Notes
        -----
        This method should typically be called once before processing rows in
        a validation run.
        """

        self._person_by_strict.clear()
        self._person_by_med_dob.clear()
        self._person_by_med_zip.clear()

        cur = self.conn.execute("""
            SELECT
                person_id,
                id_key_strict_name_dob_zip,
                id_key_medium_name_dob,
                id_key_medium_name_zip
            FROM person
        """)

        for pid, strict, med_dob, med_zip in cur.fetchall():
            if strict:
                self._person_by_strict[strict] = pid
            if med_dob:
                self._person_by_med_dob[med_dob] = pid
            if med_zip:
                self._person_by_med_zip[med_zip] = pid
 
    def get_primary_identity_creator(self):
        if not self.keycreators:
            raise ValueError("ValidationDBLogger.keycreators must be set before resolving people.")

        return max(
            self.keycreators,
            key=lambda item: len(item[0].key_fields)
        )[0]
    
    def _extract_primary_identity_values(self, row):
        kc = self.get_primary_identity_creator()

        return [
            kc._resolve_field(row, field)
            for field in kc.key_fields
        ]

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
        if isinstance(v, (pd.Timestamp, dt.datetime, dt.date, dt.time)):
            return v.isoformat()
        return v

    def start_run(self, dataset_name, org, quarter, triggered_by=None, run_description=None):

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
        run_description : str, optional
            Free-text description of the run.

        Returns
        -------
        str
            UUID string identifying the validation run.
        """

        run_id = str(uuid.uuid4())

        self.conn.execute(
            """
            INSERT INTO validation_run (
                run_id, dataset_name, organization, quarter, triggered_by, completed, run_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, dataset_name, org, quarter, triggered_by, 0, run_description),
        )

        self.conn.commit()
        return run_id
        
    def complete_run(self, run_id):
        """
        Mark a validation run as completed.

        Parameters
        ----------
        run_id : str
            UUID of the validation run to update.
        """

        cursor = self.conn.execute(
            """
            UPDATE validation_run
            SET completed = 1
            WHERE run_id = ?
            """,
            (run_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"No validation_run found for run_id={run_id}")

        self.conn.commit()

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
        key = (dataset_name, sheet_name, column_name)

        cached = self._column_cache.get(key)

        if cached:
            return cached

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
        self._column_cache[key] = column_id
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
        Resolve or logically create a person identifier using deterministic
        identity keys.

        Matching priority:
        1. strict key (name + DOB + ZIP)
        2. medium key (name + DOB)
        3. medium key (name + ZIP)

        If no match is found, a new ``person_id`` is generated and staged in
        ``self._new_people_buffer`` for later persistence.

        Parameters
        ----------
        row : pandas.Series or dict-like
            Row containing identity-key fields and participant attributes.

        Returns
        -------
        str
            Resolved or newly generated ``person_id``.

        Notes
        -----
        New people are not immediately written to the database. Persistence
        occurs when ``flush_new_people_buffer`` is called.

        Weak-name-only matching is intentionally disabled to reduce false
        positive merges.
        """

        strict = row.get("id_key_strict_name_dob_zip")
        med_dob = row.get("id_key_medium_name_dob")
        med_zip = row.get("id_key_medium_name_zip")
        weak = row.get("id_key_weak_name")

        # --------------------------------------------------
        # Existing person lookup
        # --------------------------------------------------

        if strict and strict in self._person_by_strict:
            return self._person_by_strict[strict]

        if med_dob and med_dob in self._person_by_med_dob:
            return self._person_by_med_dob[med_dob]

        if med_zip and med_zip in self._person_by_med_zip:
            return self._person_by_med_zip[med_zip]

        # --------------------------------------------------
        # New person creation
        # --------------------------------------------------

        person_id = str(uuid.uuid4())

        kc = self.get_primary_identity_creator()

        identity_fields = [
            field.replace("_normalized", "", 1)
            for field in kc.key_fields
        ]

        first_name = (
            get_value(row, identity_fields[0], normalized=True)
            if len(identity_fields) > 0
            else None
        )

        last_name = (
            get_value(row, identity_fields[1], normalized=True)
            if len(identity_fields) > 1
            else None
        )

        dob = (
            get_value(row, identity_fields[2], normalized=True)
            if len(identity_fields) > 2
            else None
        )

        zip_code = (
            get_value(row, identity_fields[3], normalized=True)
            if len(identity_fields) > 3
            else None
        )

        self._new_people_buffer.append(
            (
                person_id,
                first_name,
                last_name,
                dob,
                zip_code,
                strict,
                med_dob,
                med_zip,
                weak
            )
        )

        # --------------------------------------------------
        # Update lookup dictionaries
        # --------------------------------------------------

        if strict:
            self._person_by_strict[strict] = person_id

        if med_dob:
            self._person_by_med_dob[med_dob] = person_id

        if med_zip:
            self._person_by_med_zip[med_zip] = person_id

        return person_id

    def flush_new_people_buffer(self):
        """
        Persist buffered person records to the database.

        Writes all pending entries from ``self._new_people_buffer`` into the
        ``person`` table using a batched insert operation.

        Notes
        -----
        This method is typically called once near the end of a validation run
        after all rows have been processed.

        The in-memory buffer is cleared after a successful commit.
        """
        if not self._new_people_buffer:
            return

        clean = self._clean_sql_value

        self.conn.executemany("""
            INSERT INTO person (
                person_id,
                first_name, last_name, dob, zip,
                id_key_strict_name_dob_zip,
                id_key_medium_name_dob,
                id_key_medium_name_zip,
                id_key_weak_name,
                created_timestamp,
                updated_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            (
                pid,
                clean(first),
                clean(last),
                clean(dob),
                clean(zip),
                clean(strict),
                clean(med_dob),
                clean(med_zip),
                clean(weak),
            )
            for (
                pid, first, last, dob, zip,
                strict, med_dob, med_zip, weak
            ) in self._new_people_buffer
        ])

        self.conn.commit()
        self._new_people_buffer.clear()

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
        key = (person_id, dataset_name, org)

        pid = self._participant_map.get(key)
        
        if pid:
            return pid
        
        participant_id = str(uuid.uuid4())

        self._participant_map[key] = participant_id

        self._new_participants_buffer.append(
        (participant_id, person_id, dataset_name, org)
        )

        return participant_id
    
    def flush_new_participants(self):
        if not self._new_participants_buffer:
            return

        self.conn.executemany("""
            INSERT INTO participant (
                participant_id, person_id, dataset_name, org
            ) VALUES (?, ?, ?, ?)
        """, self._new_participants_buffer)

        self.conn.commit()
        self._new_participants_buffer.clear()
    
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

        # self.conn.execute(
        #     """
            # INSERT OR REPLACE INTO participant_presence_log
            #     (run_id, participant_id, status, row_number, sheet_name, quarter, timestamp)
            # VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        #     """,
        #     (run_id, participant_id, status, row_number, sheet_name, quarter)
        # )

        self._participant_presence_buffer.append((
        run_id,
        participant_id,
        status,
        row_number,
        sheet_name,
        quarter
        ))

    def flush_participant_presence(self):

        """
        Persist buffered participant presence records.

        Writes all queued presence records to
        ``participant_presence_log`` using a batched transaction.

        Notes
        -----
        Insertion uses ``INSERT OR REPLACE`` semantics so repeated writes for
        the same ``(run_id, participant_id)`` pair overwrite prior state.
        """

        if not self._participant_presence_buffer:
            return
        try:
            self.conn.execute("BEGIN")
            self.conn.executemany("""
            INSERT OR REPLACE INTO participant_presence_log
                (run_id, participant_id, status, row_number, sheet_name, quarter, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, self._participant_presence_buffer)
            self.conn.commit()

            self.conn.execute("SELECT 1").fetchone()

            cursor = self.conn.execute("""
                SELECT COUNT(*) 
                FROM participant_presence_log 
                WHERE run_id = ?
            """, (self._participant_presence_buffer[0][0],))

            print("Rows visible immediately after commit:", cursor.fetchone()[0])
        except Exception:
            self.conn.rollback()
            raise
        finally:
            self._participant_presence_buffer.clear()    

    def log_all_normalized_cell_values(
        self,
        run_id,
        dataset_name,
        df   # <- this is self.single_sheet
    ):
            
        """
        Persist normalized and raw cell values in long-form history tables.

        Transforms a validation dataframe from wide format into a normalized
        long-form structure suitable for longitudinal storage in the
        ``cell_value_history`` table. Both raw and normalized representations
        of each tracked value are preserved.

        This method is designed to support:
            - historical auditing of participant data
            - value change detection across runs
            - cross-sheet normalization analysis
            - downstream rule evaluation and diagnostics

        Parameters
        ----------
        run_id : str
            Validation run identifier associated with the logged values.
        dataset_name : str
            Dataset name used for column metadata normalization and lookup.
        df : pandas.DataFrame
            Combined validation dataframe containing:
            
            - ``person_id``
            - ``participant_id``
            - normalized columns
            - corresponding raw columns

            Normalized columns are expected to follow the convention:

                <column_name>_normalized_|_|_<sheet_name>

            Raw columns are expected to share the same base structure
            without the ``_normalized`` marker.

        Expected DataFrame Structure
        ----------------------------
        The dataframe should contain paired raw/normalized columns generated
        during workbook normalization. For example:

            First Name_|_|_Training
            First Name_normalized_|_|_Training

        The delimiter ``_|_|_`` is used to preserve sheet provenance while
        allowing multiple sheets to be merged into a single dataframe.

        Columns without sheet delimiters are assigned the fallback sheet name
        ``"combined"``.

        Transformation Process
        ----------------------
        The method performs the following operations:

        1. Identifies all normalized columns
        2. Derives corresponding raw column names
        3. Converts both normalized and raw values into long format using
        ``pandas.melt``
        4. Parses logical column names and sheet names from suffixed columns
        5. Verifies alignment between raw and normalized representations
        6. Resolves persistent ``column_id`` values
        7. Inserts records into ``cell_value_history``

        Alignment Validation
        --------------------
        Several assertions are intentionally enforced before merging raw and
        normalized values:

            - equal row counts
            - matching participant ordering
            - matching logical column names
            - matching sheet names

        Failure of these assertions indicates a structural mismatch between
        raw and normalized dataframe representations and should be treated as
        a critical pipeline error.

        Column Normalization
        --------------------
        Logical columns are normalized into persistent ``column_id`` values
        using ``get_or_create_column``. This allows:

            - stable column tracking across runs
            - cross-sheet comparisons
            - schema evolution analysis
            - reduced storage duplication

        Persistence Behavior
        --------------------
        Records are inserted in batches using ``executemany`` to reduce SQLite
        transaction overhead during large validation runs.

        Values are cleaned using ``_clean_sql_value`` before insertion so that:

            - Pandas missing values become ``NULL``
            - datetime objects become ISO-8601 strings

        Notes
        -----
        Only rows with non-null ``participant_id`` values are logged.

        This method assumes that normalized and raw columns were generated
        through the standard validation-engine normalization pipeline.
        """

        if "person_id" not in df.columns:
            raise ValueError("single_sheet must contain person_id")

        if "participant_id" not in df.columns:
            raise ValueError("single_sheet must contain participant_id")

        df = df[df["participant_id"].notna()].copy()    

        norm_cols = [
            c for c in df.columns
            if is_normalized(c)
        ]

        if not norm_cols:

            print(
                f"{dataset_name}: no normalized columns found, "
                "skipping cell value logging."
            )

            return    

        # -------------------------------------------------------
        # Melt normalized values
        # -------------------------------------------------------
        long_norm = df.melt(
            id_vars=["person_id", "participant_id"],
            value_vars=norm_cols,
            var_name="column_name",
            value_name="value_normalized"
        )

        long_norm["sheet_name"] = (
            long_norm["column_name"]
            .map(sheet_name)
        )

        missing_sheet = long_norm["sheet_name"].isna()

        if missing_sheet.any():

            bad_cols = (
                long_norm.loc[missing_sheet, "column_name"]
                .drop_duplicates()
                .tolist()
            )

            raise ValueError(
                "Columns missing sheet provenance:\n"
                + "\n".join(f"    - {c}" for c in bad_cols)
            )

        long_norm["column_name"] = (
            long_norm["column_name"]
            .map(base_name)
        )

        # -------------------------------------------------------
        # Melt raw values
        # -------------------------------------------------------
        raw_cols = [
            remove_normalized_suffix(c)
            for c in norm_cols
        ]

        missing_raw_cols = [
            c for c in raw_cols
            if c not in df.columns
        ]

        if missing_raw_cols:
            raise ValueError(
                "Missing raw columns for normalized columns:\n"
                + "\n".join(f"    - {c}" for c in missing_raw_cols)
            )

        long_raw = df.melt(
            id_vars=["person_id", "participant_id"],
            value_vars=raw_cols,
            var_name="column_name",
            value_name="value_raw"
        )

        long_raw["sheet_name"] = (
            long_raw["column_name"]
            .map(sheet_name)
        )

        missing_sheet = long_raw["sheet_name"].isna()

        if missing_sheet.any():

            bad_cols = (
                long_raw.loc[missing_sheet, "column_name"]
                .drop_duplicates()
                .tolist()
            )

            raise ValueError(
                "Columns missing sheet provenance:\n"
                + "\n".join(f"    - {c}" for c in bad_cols)
            )

        long_raw["column_name"] = (
            long_raw["column_name"]
            .map(base_name)
        )

        # -------------------------------------------------------
        # Combine
        # -------------------------------------------------------

        ### confirm alignment before merging, this is a critical failure if it doesn't pass
        if len(long_norm) != len(long_raw):
            raise ValueError(
                "Raw and normalized melts produced different row counts."
            )

        if not (long_norm["participant_id"].values == long_raw["participant_id"].values).all():
            raise ValueError(
                "Normalized and raw participant ID lists do not match."
            )


        if not (long_norm["column_name"].values == long_raw["column_name"].values).all():
            raise ValueError(
                "Normalized and raw column_name lists do not match."
            )

        if  not (long_norm["sheet_name"].values == long_raw["sheet_name"].values).all():
            raise ValueError(
                "Normalized and raw sheet_name lists do not match."
            )
        
        long_df = long_norm.copy()
        long_df["value_raw"] = long_raw["value_raw"].values

        # -------------------------------------------------------
        # Column ID mapping
        # -------------------------------------------------------
        column_ids = {
            (row["column_name"], row["sheet_name"]): self.get_or_create_column(
                dataset_name=dataset_name,
                sheet_name=row["sheet_name"],
                column_name=row["column_name"]
            )
            for _, row in long_df[["column_name", "sheet_name"]].drop_duplicates().iterrows()
        }

        key_series = list(zip(long_df["column_name"], long_df["sheet_name"]))
        long_df["column_id"] = [column_ids[k] for k in key_series]

        # -------------------------------------------------------
        # Metadata
        # -------------------------------------------------------
        long_df["run_id"] = run_id
        long_df["history_id"] = [uuid.uuid4().hex for _ in range(len(long_df))]

        clean = self._clean_sql_value

        long_df["value_raw"] = long_df["value_raw"].map(clean)
        long_df["value_normalized"] = long_df["value_normalized"].map(clean)

        records = list(
            long_df[
                [
                    "history_id",
                    "run_id",
                    "participant_id",
                    "column_id",
                    "value_raw",
                    "value_normalized",
                ]
            ].itertuples(index=False, name=None)
        )

        insert_sql = """
            INSERT INTO cell_value_history
            (history_id, run_id, participant_id, column_id, value_raw, value_normalized)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        batch_size = 10000
        cur = self.conn.cursor()

        for i in range(0, len(records), batch_size):
            cur.executemany(insert_sql, records[i:i + batch_size])

        self.conn.commit()

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
         
        # violation_id = str(uuid.uuid4())
        
        clean = self._clean_sql_value
        
        # self.conn.execute("""
            # INSERT INTO validation_violation (
            #     violation_id, run_id, rule_id, participant_id,
            #     column_id, normalized, raw_value, severity
            # ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        # """, (violation_id, run_id, rule_id, participant_id,
        #     column_id, clean(normalized), clean(raw_value), severity))
        
        # self.conn.commit()

        self._violation_buffer.append((
        uuid.uuid4().hex,
        run_id,
        rule_id,
        participant_id,
        column_id,
        clean(normalized),
        clean(raw_value),
        severity,
        ))

    def flush_violations(self):

        """
        Persist buffered validation violations to the database.

        Writes all queued entries from ``self._violation_buffer`` into the
        ``validation_violation`` table using a batched transaction.

        Violations are accumulated during validation through
        ``log_violation`` and deferred until this method is called in order
        to reduce transaction overhead during large validation runs.

        Persistence is performed using ``executemany`` within an explicit
        transaction boundary.

        Raises
        ------
        Exception
            Re-raises any database exception encountered during insertion
            after rolling back the transaction.

        Notes
        -----
        The in-memory violation buffer is cleared after successful insertion
        or rollback.

        This method is typically called near the end of a validation run
        after all rule evaluation has completed.
        """

        if not self._violation_buffer:
            return
        try:
            self.conn.execute("BEGIN")
            self.conn.executemany("""
            INSERT INTO validation_violation (
                violation_id, run_id, rule_id, participant_id,
                column_id, normalized, raw_value, severity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, self._violation_buffer)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            self._violation_buffer.clear()    

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

    def close(self):
        self.conn.close()

