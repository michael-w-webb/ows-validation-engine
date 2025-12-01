import os, uuid, sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "validation_dev.db")

class ValidationDBLogger:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.commit()

    def _clean_sql_value(self, v):
        """Convert Pandas NA and similar to None so SQLite accepts them."""
        if v is pd.NA or v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        return v

    def start_run(self, dataset_name, org, quarter, triggered_by=None):
        run_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO validation_run (run_id, dataset_name, organization, quarter, triggered_by) VALUES (?, ?, ?, ?, ?)",
            (run_id, dataset_name, org, quarter, triggered_by),
        )
        self.conn.commit()
        return run_id

    def get_or_create_column(self, dataset_name, sheet_name, column_name):
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
        Return one person row matching the given hashed identity key.
        Returns None if no match.
        """
        sql = f"SELECT * FROM person WHERE {key_field} = ?"
        cur = self.conn.execute(sql, (key_value,))
        return cur.fetchone()

    def insert_person(self, first, last, dob, zip_code,
                    strict_key, med_name_dob_key, med_name_zip_key, weak_key):

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
        sheet_name=None,
        org=None,
        quarter=None):

        """
        Return a persistent participant_id for (person_id, dataset_name).
        Create it only if it does not exist.
        """

        # 1. Try fetch existing participant
        cur = self.conn.execute("""
            SELECT participant_id 
            FROM participant
            WHERE person_id=? AND dataset_name=?
        """, (person_id, dataset_name))

        row = cur.fetchone()
        if row:
            return row[0]  # <-- existing persistent participant_id

        # 2. Create new participant
        participant_id = str(uuid.uuid4())

        self.conn.execute("""
            INSERT INTO participant (
                participant_id, person_id, dataset_name, 
                sheet_name, org, quarter
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (participant_id, person_id, dataset_name, sheet_name, org, quarter))

        self.conn.commit()
        return participant_id
    
    def mark_presence_participant(self, run_id, participant_id, status):
        """
        Record whether a participant is present or missing in a given run.
        Writes to participant_presence_log with a composite PK (run_id, participant_id).
        """

        self.conn.execute(
            """
            INSERT OR REPLACE INTO participant_presence_log
                (run_id, participant_id, status, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (run_id, participant_id, status)
        )

        self.conn.commit()


    def bulk_log_cell_history(self, records):

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
        Log cell values for all normalized sheets,
        aligning each sheet's rows to participants using id_key.
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

