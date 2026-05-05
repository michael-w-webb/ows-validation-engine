import os, uuid, sqlite3
from datetime import datetime
import pandas as pd
import datetime as dt
from config import DB_PATH

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

        self.raw_data_points = {}

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        Preload participant identifiers into an in-memory map for fast lookup.

        Populates self._participant_map with keys of the form:
            (person_id, dataset_name, org) -> participant_id

        This should be called once per run, before validation begins.
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
        Preload person identity key maps into memory.
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
                    strict_key, med_name_dob_key, med_name_zip_key, weak_key, gender, race, ethnicity): #todo: , race, ethnicity

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
        gender : str
            Gender
        race : str # todo: coming soon
            Race
        ethnicity : str # todo: coming soon
            Ethnicity

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
                gender,
                race,
                ethnicity,
                created_timestamp, updated_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
        """, (
            person_id,
            clean(first), clean(last), clean(dob), clean(zip_code),
            clean(strict_key),
            clean(med_name_dob_key),
            clean(med_name_zip_key),
            clean(weak_key),
            clean(gender),
            clean(race), # todo: add 2 ?'s for race and ethnicity and also above in the sql query
            clean(ethnicity)
        ))

        self.conn.commit()
        return person_id

    
    def resolve_person(self, row) -> str:
        """
        Resolve a person using in-memory identity key maps.
        Creates a new person *logically* if no match is found,
        deferring persistence until later.
        """

        strict  = row.get("id_key_strict_name_dob_zip")
        med_dob = row.get("id_key_medium_name_dob")
        med_zip = row.get("id_key_medium_name_zip")
        weak    = row.get("id_key_weak_name")

        # 1️⃣ strict
        if strict and strict in self._person_by_strict:
            return self._person_by_strict[strict]

        # 2️⃣ medium (name + dob)
        if med_dob and med_dob in self._person_by_med_dob:
            return self._person_by_med_dob[med_dob]

        # 3️⃣ medium (name + zip)
        if med_zip and med_zip in self._person_by_med_zip:
            return self._person_by_med_zip[med_zip]

        # 4️⃣ No match → register new person
        person_id = str(uuid.uuid4())

        self._new_people_buffer.append((
            person_id,
            row.get("First Name"),
            row.get("Last Name"),
            row.get("Client Date of Birth"),
            row.get("Zip Code"),
            strict,
            med_dob,
            med_zip,
            weak,
            row.get("Gender"),
            row.get("Race"),
            row.get("Ethnicity")
        ))

        # Register keys immediately for downstream rows
        if strict:
            self._person_by_strict[strict] = person_id
        if med_dob:
            self._person_by_med_dob[med_dob] = person_id
        if med_zip:
            self._person_by_med_zip[med_zip] = person_id

        return person_id

    def flush_new_people_buffer(self):
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
                gender,
                race,
                ethnicity,
                created_timestamp,
                updated_timestamp
            ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
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
                clean(gender),
                clean(race), # -- todo: add 2 ?'s for race and ethnicity above in sql query
                clean(ethnicity)
            )
            for (
                pid, first, last, dob, zip,
                strict, med_dob, med_zip, weak, gender, race, ethnicity 
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

        if "person_id" not in df.columns:
            raise ValueError("single_sheet must contain person_id")

        if "participant_id" not in df.columns:
            raise ValueError("single_sheet must contain participant_id")

        df = df[df["participant_id"].notna()].copy()

        DELIM = "_|_|_"

        def split_col(col):
            # remove normalization marker first
            col = col.replace("_normalized", "")
            
            if DELIM in col:
                base, sheet = col.split(DELIM, 1)
            else:
                base, sheet = col, "combined"  # fallback

            return base, sheet

        # -------------------------------------------------------
        # Identify normalized columns
        # -------------------------------------------------------
        norm_cols = [c for c in df.columns if "_normalized_" in c]

        if not norm_cols:
            return

        raw_cols = [c.replace("_normalized", "") for c in norm_cols]

        

        # -------------------------------------------------------
        # Melt normalized values
        # -------------------------------------------------------
        long_norm = df.melt(
            id_vars=["person_id", "participant_id"],
            value_vars=norm_cols,
            var_name="column_name",
            value_name="value_normalized"
        )

        parsed = long_norm["column_name"].apply(split_col)

        long_norm["column_name"] = parsed.map(lambda x: x[0])
        long_norm["sheet_name"] = parsed.map(lambda x: x[1])

        # -------------------------------------------------------
        # Melt raw values
        # -------------------------------------------------------
        raw_cols = [c for c in raw_cols if c in df.columns]

        long_raw = df.melt(
            id_vars=["person_id", "participant_id"],
            value_vars=raw_cols,
            var_name="column_name",
            value_name="value_raw"
        )

        parsed_raw = long_raw["column_name"].apply(split_col)

        long_raw["column_name"] = parsed_raw.map(lambda x: x[0])
        long_raw["sheet_name"] = parsed_raw.map(lambda x: x[1])

        # -------------------------------------------------------
        # Combine
        # -------------------------------------------------------

        ### confirm alignment before merging, this is a critical failure if it doesn't pass
        assert len(long_norm) == len(long_raw)

        assert (long_norm["participant_id"].values == long_raw["participant_id"].values).all()

        assert (long_norm["column_name"].values == long_raw["column_name"].values).all()

        assert (long_norm["sheet_name"].values == long_raw["sheet_name"].values).all()
        
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






















# # ############### GENDER ONLY #####################
# import os, uuid, sqlite3
# from datetime import datetime
# import pandas as pd

# DB_PATH = os.path.join(os.path.dirname(__file__), "validation_dev.db")

# class ValidationDBLogger:

#     """
#     SQLite-backed logging and persistence layer for the validation engine.

#     This class is responsible for recording validation runs, resolving and
#     persisting participant identities, and logging normalized data values
#     and validation violations to a SQLite database. It enables longitudinal
#     tracking of participants and datasets across repeated validation runs.

#     The logger supports:
#       - Run-level tracking via unique ``run_id`` values
#       - Deterministic person resolution using hashed identity keys
#       - Persistent participant identifiers scoped to (person, dataset)
#       - Column-level metadata normalization across sheets and datasets
#       - Cell-level value history logging for post-normalization analysis
#       - Structured violation logging with severity levels

#     SQLite is configured for concurrent-safe access using WAL mode and
#     foreign key enforcement. All timestamps are generated at write time
#     using the database clock.

#     Notes
#     -----
#     * This logger assumes the database schema already exists.
#     * Identity resolution prioritizes strict and medium-strength keys;
#       weak-name-only matching is intentionally disabled to avoid
#       accidental merges.
#     * All Pandas NA / NaN values are coerced to ``NULL`` prior to insertion.

#     Typical usage
#     -------------
#     >>> logger = ValidationDBLogger()
#     >>> run_id = logger.start_run(
#     ...     dataset_name="Q2 Submission",
#     ...     org="EWIB",
#     ...     quarter="2025Q2"
#     ... )
#     >>> person_id = logger.resolve_person(row)
#     >>> participant_id = logger.get_or_create_participant(
#     ...     person_id, dataset_name="Q2 Submission"
#     ... )

#     This class is designed to be called by higher-level orchestration
#     components (e.g., validation engines, workbook loaders) rather than
#     directly by end users.
#     """
#     def __init__(self):

#         """
#         Initialize a SQLite connection for validation logging.

#         Opens a connection to the validation database and configures
#         SQLite pragmas to support concurrent access and safe writes.

#         Configuration applied:
#         - Foreign key enforcement enabled
#         - WAL journal mode for concurrent readers/writers
#         - NORMAL synchronous mode for performance/safety balance

#         Notes
#         -----
#         The database file is expected to exist and have a valid schema.
#         This constructor does not create or migrate tables.
#         """
#         self._violation_buffer = []
#         self._participant_presence_buffer = []
#         self._column_cache = {}
#         self._participant_cache = {}

#         self._participant_map = {}
#         self._new_participants_buffer = []

#         self._person_by_strict = {}
#         self._person_by_med_dob = {}
#         self._person_by_med_zip = {}

#         self._new_people_buffer = []

#         self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#         self.conn.execute("PRAGMA foreign_keys = ON;")
#         self.conn.execute("PRAGMA journal_mode = WAL;")
#         self.conn.execute("PRAGMA synchronous = NORMAL;")
#         self.conn.commit()

#     #### some functions for mapping values: 

#     def load_participant_map(
#     self,
#     dataset_name: str,
#     org: str | None = None,
#     ):
#         """
#         Preload participant identifiers into an in-memory map for fast lookup.

#         Populates self._participant_map with keys of the form:
#             (person_id, dataset_name, org) -> participant_id

#         This should be called once per run, before validation begins.
#         """

#         self._participant_map.clear()

#         if org is None:
#             sql = """
#                 SELECT participant_id, person_id, dataset_name, org
#                 FROM participant
#                 WHERE dataset_name = ?
#             """
#             params = (dataset_name,)
#         else:
#             sql = """
#                 SELECT participant_id, person_id, dataset_name, org
#                 FROM participant
#                 WHERE dataset_name = ? AND org = ?
#             """
#             params = (dataset_name, org)

#         cur = self.conn.execute(sql, params)

#         for participant_id, person_id, dataset_name, org in cur.fetchall():
#             key = (person_id, dataset_name, org)
#             self._participant_map[key] = participant_id

#     def load_person_maps(self):

#         """
#         Preload person identity key maps into memory.
#         """

#         self._person_by_strict.clear()
#         self._person_by_med_dob.clear()
#         self._person_by_med_zip.clear()

#         cur = self.conn.execute("""
#             SELECT
#                 person_id,
#                 id_key_strict_name_dob_zip,
#                 id_key_medium_name_dob,
#                 id_key_medium_name_zip
#             FROM person
#         """)

#         for pid, strict, med_dob, med_zip in cur.fetchall():
#             if strict:
#                 self._person_by_strict[strict] = pid
#             if med_dob:
#                 self._person_by_med_dob[med_dob] = pid
#             if med_zip:
#                 self._person_by_med_zip[med_zip] = pid
 

#     def _clean_sql_value(self, v):

#         """
#         Normalize Python and Pandas missing values for SQLite insertion.

#         Converts Pandas NA, NaN, and ``None`` values to ``NULL`` so they
#         can be safely written to SQLite columns.

#         Parameters
#         ----------
#         v : Any
#             A value originating from Pandas or Python objects.

#         Returns
#         -------
#         Any or None
#             ``None`` if the value represents missing data; otherwise
#             the original value.
#         """

#         if v is pd.NA or v is None:
#             return None
#         if isinstance(v, float) and pd.isna(v):
#             return None
#         return v

#     def start_run(self, dataset_name, org, quarter, triggered_by=None):

#         """
#         Create and persist a new validation run.

#         Inserts a new row into the ``validation_run`` table and returns
#         a unique ``run_id`` that should be used to associate all
#         subsequent logging activity for this run.

#         Parameters
#         ----------
#         dataset_name : str
#             Logical name of the dataset submission.
#         org : str
#             Submitting organization.
#         quarter : str
#             Reporting quarter (e.g. ``"2025Q2"``).
#         triggered_by : str, optional
#             Identifier for the process or user that initiated the run.

#         Returns
#         -------
#         str
#             UUID string identifying the validation run.
#         """

#         run_id = str(uuid.uuid4())
#         self.conn.execute(
#             "INSERT INTO validation_run (run_id, dataset_name, organization, quarter, triggered_by) VALUES (?, ?, ?, ?, ?)",
#             (run_id, dataset_name, org, quarter, triggered_by),
#         )
#         self.conn.commit()
#         return run_id

#     def get_or_create_column(self, dataset_name, sheet_name, column_name):

#         """
#         Retrieve or create a normalized column identifier.

#         Ensures that each logical (dataset, sheet, column) combination
#         is represented by a single persistent ``column_id`` across runs.

#         Parameters
#         ----------
#         dataset_name : str
#             Dataset to which the column belongs.
#         sheet_name : str
#             Sheet name within the dataset.
#         column_name : str
#             Column name as it appears in the sheet.

#         Returns
#         -------
#         str
#             UUID string identifying the column.
#         """
#         key = (dataset_name, sheet_name, column_name)

#         cached = self._column_cache.get(key)

#         if cached:
#             return cached

#         cur = self.conn.execute(
#             "SELECT column_id FROM dataset_column WHERE dataset_name=? AND sheet_name=? AND column_name=?",
#             (dataset_name, sheet_name, column_name)
#         )
#         row = cur.fetchone()
#         if row:
#             return row[0]

#         column_id = str(uuid.uuid4())
#         self.conn.execute(
#             "INSERT INTO dataset_column (column_id, dataset_name, sheet_name, column_name) VALUES (?, ?, ?, ?)",
#             (column_id, dataset_name, sheet_name, column_name)
#         )
#         self.conn.commit()
#         self._column_cache[key] = column_id
#         return column_id

#     def get_person_by_key(self, key_field, key_value):

#         """
#         Retrieve a person record using a hashed identity key.

#         Parameters
#         ----------
#         key_field : str
#             Name of the identity key column (e.g.
#             ``id_key_strict_name_dob_zip``).
#         key_value : str
#             Hashed identity key value.

#         Returns
#         -------
#         tuple or None
#             The full ``person`` row if a match is found, otherwise ``None``.
#         """

#         sql = f"SELECT * FROM person WHERE {key_field} = ?"
#         cur = self.conn.execute(sql, (key_value,))
#         return cur.fetchone()

#     def insert_person(self, first, last, dob, zip_code,
#                     strict_key, med_name_dob_key, med_name_zip_key, weak_key, gender): #todo: , race, ethnicity

#         """
#         Insert a new person record into the database.

#         Persists identifying information and associated hashed identity
#         keys. Missing values are safely coerced to ``NULL``.

#         Parameters
#         ----------
#         first : str
#             First name.
#         last : str
#             Last name.
#         dob : date or str
#             Date of birth.
#         zip_code : str
#             ZIP code.
#         strict_key : str
#             Strict identity hash (name + DOB + ZIP).
#         med_name_dob_key : str
#             Medium identity hash (name + DOB).
#         med_name_zip_key : str
#             Medium identity hash (name + ZIP).
#         weak_key : str
#             Weak identity hash (name only).
#         gender : str
#             Gender
#         race : str # todo: coming soon
#             Race
#         ethnicity : str # todo: coming soon
#             Ethnicity

#         Returns
#         -------
#         str
#             UUID string identifying the new person.
#         """


#         clean = self._clean_sql_value  # shortcut alias
    
#         person_id = str(uuid.uuid4())

#         self.conn.execute("""
#             INSERT INTO person (
#                 person_id,
#                 first_name, last_name, dob, zip,
#                 id_key_strict_name_dob_zip,
#                 id_key_medium_name_dob,
#                 id_key_medium_name_zip,
#                 id_key_weak_name,
#                 gender,
#                 -- race,
#                 -- ethnicity,
#                 created_timestamp, updated_timestamp
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
#         """, (
#             person_id,
#             clean(first), clean(last), clean(dob), clean(zip_code),
#             clean(strict_key),
#             clean(med_name_dob_key),
#             clean(med_name_zip_key),
#             clean(weak_key),
#             clean(gender)
#             # clean(race), # todo: add 2 ?'s for race and ethnicity and also above in the sql query
#             # clean(ethnicity)
#         ))

#         self.conn.commit()
#         return person_id

    
#     def resolve_person(self, row) -> str:
#         """
#         Resolve a person using in-memory identity key maps.
#         Creates a new person *logically* if no match is found,
#         deferring persistence until later.
#         """

#         strict  = row.get("id_key_strict_name_dob_zip")
#         med_dob = row.get("id_key_medium_name_dob")
#         med_zip = row.get("id_key_medium_name_zip")
#         weak    = row.get("id_key_weak_name")

#         # 1️⃣ strict
#         if strict and strict in self._person_by_strict:
#             return self._person_by_strict[strict]

#         # 2️⃣ medium (name + dob)
#         if med_dob and med_dob in self._person_by_med_dob:
#             return self._person_by_med_dob[med_dob]

#         # 3️⃣ medium (name + zip)
#         if med_zip and med_zip in self._person_by_med_zip:
#             return self._person_by_med_zip[med_zip]

#         # 4️⃣ No match → register new person
#         person_id = str(uuid.uuid4())

#         self._new_people_buffer.append((
#             person_id,
#             row.get("First Name"),
#             row.get("Last Name"),
#             row.get("Client Date of Birth"),
#             row.get("Zip Code"),
#             strict,
#             med_dob,
#             med_zip,
#             weak,
#             row.get("Gender")
#             # row.get("Race"),
#             # row.get("Ethnicity")
#         ))

#         # Register keys immediately for downstream rows
#         if strict:
#             self._person_by_strict[strict] = person_id
#         if med_dob:
#             self._person_by_med_dob[med_dob] = person_id
#         if med_zip:
#             self._person_by_med_zip[med_zip] = person_id

#         return person_id

#     def flush_new_people_buffer(self):
#         if not self._new_people_buffer:
#             return

#         clean = self._clean_sql_value

#         self.conn.executemany("""
#             INSERT INTO person (
#                 person_id,
#                 first_name, last_name, dob, zip,
#                 id_key_strict_name_dob_zip,
#                 id_key_medium_name_dob,
#                 id_key_medium_name_zip,
#                 id_key_weak_name,
#                 gender,
#                 -- race,
#                 -- ethnicity,
#                 created_timestamp,
#                 updated_timestamp
#             ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
#         """, [
#             (
#                 pid,
#                 clean(first),
#                 clean(last),
#                 clean(dob),
#                 clean(zip),
#                 clean(strict),
#                 clean(med_dob),
#                 clean(med_zip),
#                 clean(weak),
#                 clean(gender)
#                 # clean(race), -- todo: add 2 ?'s for race and ethnicity above in sql query
#                 # clean(ethnicity)
#             )
#             for (
#                 pid, first, last, dob, zip,
#                 strict, med_dob, med_zip, weak, gender # race, ethnicity
#             ) in self._new_people_buffer
#         ])

#         self.conn.commit()
#         self._new_people_buffer.clear()

#     def get_or_create_participant(
#         self,
#         person_id,
#         dataset_name,
#         org=None):

#         """
#         Retrieve or create a persistent participant identifier.

#         A participant represents a specific person's presence within
#         a given dataset. The identifier is stable across runs and reused
#         whenever the same (person, dataset) pair is encountered.

#         Parameters
#         ----------
#         person_id : str
#             Identifier of the resolved person.
#         dataset_name : str
#             Dataset to which the participant belongs.
#         sheet_name : str, optional
#             Sheet name where the participant appears.
#         org : str, optional
#             Organization associated with the participant.
#         quarter : str, optional
#             Reporting quarter.

#         Returns
#         -------
#         str
#             UUID string identifying the participant.
#         """
#         key = (person_id, dataset_name, org)

#         pid = self._participant_map.get(key)
        
#         if pid:
#             return pid
        
#         participant_id = str(uuid.uuid4())

#         self._participant_map[key] = participant_id

#         self._new_participants_buffer.append(
#         (participant_id, person_id, dataset_name, org)
#         )

#         return participant_id
    
#     def flush_new_participants(self):
#         if not self._new_participants_buffer:
#             return

#         self.conn.executemany("""
#             INSERT INTO participant (
#                 participant_id, person_id, dataset_name, org
#             ) VALUES (?, ?, ?, ?)
#         """, self._new_participants_buffer)

#         self.conn.commit()
#         self._new_participants_buffer.clear()
        
    
#     def mark_presence_participant(self, run_id, participant_id, status, row_number, sheet_name, quarter):
        
#         """
#         Record participant presence or absence for a validation run.

#         Writes to ``participant_presence_log`` using a composite key
#         of (run_id, participant_id), allowing presence state to be
#         updated idempotently.

#         Parameters
#         ----------
#         run_id : str
#             Validation run identifier.
#         participant_id : str
#             Participant identifier.
#         status : str
#             Presence status (e.g. ``"present"``, ``"missing"``).
#         """

#         # self.conn.execute(
#         #     """
#             # INSERT OR REPLACE INTO participant_presence_log
#             #     (run_id, participant_id, status, row_number, sheet_name, quarter, timestamp)
#             # VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
#         #     """,
#         #     (run_id, participant_id, status, row_number, sheet_name, quarter)
#         # )

#         self._participant_presence_buffer.append((
#         run_id,
#         participant_id,
#         status,
#         row_number,
#         sheet_name,
#         quarter
#         ))

#     def flush_participant_presence(self):

#         if not self._participant_presence_buffer:
#             return
#         try:
#             self.conn.execute("BEGIN")
#             self.conn.executemany("""
#             INSERT OR REPLACE INTO participant_presence_log
#                 (run_id, participant_id, status, row_number, sheet_name, quarter, timestamp)
#             VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
#         """, self._participant_presence_buffer)
#             self.conn.commit()
#         except Exception:
#             self.conn.rollback()
#             raise
#         finally:
#             self._participant_presence_buffer.clear()   

#     def log_all_normalized_cell_values(
#         self,
#         run_id,
#         dataset_name,
#         normalized_data,   # dict: sheet_name → normalized df
#         id_df              # identity df containing id_key, person_id, participant_id
#     ):
        
#         """
#         Log normalized cell values for all sheets in a dataset.

#         Aligns rows from normalized dataframes to participants using
#         identity keys, then records normalized values for each
#         non-metadata column.

#         Parameters
#         ----------
#         logger : ValidationDBLogger
#             Active logger instance.
#         run_id : str
#             Validation run identifier.
#         dataset_name : str
#             Dataset being logged.
#         normalized_data : dict
#             Mapping of ``sheet_name`` to normalized Pandas DataFrames.
#         id_df : pandas.DataFrame
#             DataFrame containing ``id_key`` to ``participant_id`` mappings.
#         """

#         # -------------------------------------------------------
#         # 1. Build a lookup table: id_key → participant_id
#         # -------------------------------------------------------
#         key_to_participant = (
#             id_df[["id_key", "participant_id"]]
#             .dropna(subset=["participant_id"])
#             .set_index("id_key")["participant_id"]
#             .to_dict()
#         )

#         # -------------------------------------------------------
#         # 2. Loop through each normalized sheet
#         # -------------------------------------------------------
#         for sheet_name, df_norm in normalized_data.items():

#             if "id_key" not in df_norm.columns:
#                 print(f"[WARN] Sheet '{sheet_name}' has no id_key column; skipping logging.")
#                 continue
            
#             df_norm = df_norm[df_norm["id_key"].isin(key_to_participant)].copy()


#             column_ids = {}

#             for col in df_norm.columns:
#                     if col in ("id_key", "row_number", "person_id", "participant_id"):
#                         continue

#                     column_ids[col] = self.get_or_create_column(
#                         dataset_name=dataset_name,
#                         sheet_name=sheet_name,
#                         column_name=col
#                     )

#             value_cols = [
#                 c for c in df_norm.columns
#                 if c not in ("id_key", "row_number", "person_id", "participant_id")
#             ]

#             long_df = df_norm.melt(
#                 id_vars=["id_key"],
#                 value_vars=value_cols,
#                 var_name="column_name",
#                 value_name="value_normalized"
#             )

#             long_df["participant_id"] = long_df["id_key"].map(key_to_participant)
#             long_df["column_id"] = long_df["column_name"].map(column_ids)
#             long_df["run_id"] = run_id
#             long_df["history_id"] = [uuid.uuid4().hex for _ in range(len(long_df))]
#             long_df["value_raw"] = None

#             long_df = long_df.drop(columns=["id_key", "column_name"])

#             long_df.to_sql(
#                 "cell_value_history",
#                 self.conn,
#                 if_exists="append",
#                 index=False,
#                 chunksize=5_000
#             )
    
#     def log_violation(self, run_id, rule_id, participant_id,
#                     column_id, normalized, raw_value, severity="error"):

#         """
#         Record a validation rule violation.

#         Inserts a structured violation record capturing the rule,
#         affected participant, column, and observed values.

#         Parameters
#         ----------
#         run_id : str
#             Validation run identifier.
#         rule_id : int
#             Identifier of the violated rule.
#         participant_id : str
#             Participant associated with the violation.
#         column_id : str
#             Column associated with the violation.
#         normalized : Any
#             Normalized value that triggered the violation.
#         raw_value : Any
#             Original raw value prior to normalization.
#         severity : str, optional
#             Severity level (default: ``"error"``).
#         """
         
#         # violation_id = str(uuid.uuid4())
        
#         clean = self._clean_sql_value
        
#         # self.conn.execute("""
#             # INSERT INTO validation_violation (
#             #     violation_id, run_id, rule_id, participant_id,
#             #     column_id, normalized, raw_value, severity
#             # ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         # """, (violation_id, run_id, rule_id, participant_id,
#         #     column_id, clean(normalized), clean(raw_value), severity))
        
#         # self.conn.commit()

#         self._violation_buffer.append((
#         uuid.uuid4().hex,
#         run_id,
#         rule_id,
#         participant_id,
#         column_id,
#         clean(normalized),
#         clean(raw_value),
#         severity,
#         ))

#     def flush_violations(self):

#         if not self._violation_buffer:
#             return
#         try:
#             self.conn.execute("BEGIN")
#             self.conn.executemany("""
#             INSERT INTO validation_violation (
#                 violation_id, run_id, rule_id, participant_id,
#                 column_id, normalized, raw_value, severity
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         """, self._violation_buffer)
#             self.conn.commit()
#         except Exception:
#             self.conn.rollback()
#             raise
#         finally:
#             self._violation_buffer.clear()    

#     def log_key_mismatches(self, run_id, mismatches):
#         """
#         Persist unresolved identity-key mismatches detected during validation.

#         Parameters
#         ----------
#         run_id : str
#             Validation run identifier.
#         mismatches : list[dict]
#             Each dict must contain:
#             org, period, sheet, id_key, issue
#         """
#         rows = [
#             (
#                 str(uuid.uuid4()),
#                 run_id,
#                 m["org"],
#                 m["period"],
#                 m["sheet"],
#                 m["id_key"],
#                 m["issue"],
#             )
#             for m in mismatches
#         ]

#         self.conn.executemany(
#             """
#             INSERT INTO participant_key_mismatch (
#                 mismatch_id,
#                 run_id,
#                 org,
#                 quarter,
#                 sheet_name,
#                 id_key,
#                 issue
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#             """,
#             rows
#         )
#         self.conn.commit()

