import duckdb
import os
import sqlite3
from config import DB_PATH, PROJECT_ROOT

print("Working directory:", os.getcwd())
print("DB exists:", os.path.exists(DB_PATH))

# ---------------------------------------------------------------------
# 1. Validate that the file is really SQLite
# ---------------------------------------------------------------------
try:
    sqlite_tables_test = sqlite3.connect(DB_PATH).execute("SELECT name FROM sqlite_master").fetchall()
    print("SQLite file OK. Tables found in sqlite_master:", sqlite_tables_test)
except Exception as e:
    raise ValueError(f"Invalid or corrupt SQLite file: {e}")

# ---------------------------------------------------------------------
# 2. Connect + Load sqlite_scanner
# ---------------------------------------------------------------------
con = duckdb.connect(":memory:")
con.execute("INSTALL sqlite_scanner;")
con.execute("LOAD sqlite_scanner;")

print(con.sql("SELECT * FROM duckdb_extensions()").df())
print(duckdb.__version__)

# ---------------------------------------------------------------------
# 3. Attach SQLite DB
# ---------------------------------------------------------------------
print("\nAttaching SQLite DB...")
con.execute(f"ATTACH '{DB_PATH}' AS sqlite_db (TYPE SQLITE);")

print(con.sql("PRAGMA database_list").df())

db_list = con.sql("PRAGMA database_list").fetchall()
print("Database list:", db_list)
print(con.sql("SELECT * FROM sqlite_db.person LIMIT 5").df())

# ---------------------------------------------------------------------
# 4. Check tables visible in DuckDB
# ---------------------------------------------------------------------
schemas = con.sql("SELECT schema_name FROM information_schema.schemata").fetchall()
print("\nSchemas:", schemas)

all_tables = con.sql("""
    SELECT table_schema, table_name 
    FROM information_schema.tables
    ORDER BY table_schema, table_name
""").fetchall()
print("\nAll tables:", all_tables)

sqlite_tables = [
    "person",
    "validation_run",
    "participant",
    "dataset_column",
    "participant_presence_log",
    "cell_value_history",
    "validation_rule",
    "sqlite_sequence",
    "validation_violation",
    "participant_key_mismatch"
]

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "database" / "cc_db_parquet_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Columns to remove from person
PERSON_PII_COLUMNS = [
    "first_name",
    "last_name",
    "id_key_strict_name_dob_zip",
    "id_key_medium_name_dob",
    "id_key_medium_name_zip",
    "id_key_weak_name"
]

# Columns to remove from participant_key_mismatch
PKM_DROP_COLUMNS = [
    "id_key"
]

# Export each table directly from sqlite_db.{table}
for t in sqlite_tables:
    outpath = os.path.join(OUTPUT_DIR, f"{t}.parquet")
    print(f"Exporting sqlite_db.{t} → {outpath}")

    # --- PERSON special case (drop PII columns) ---
    if t == "person":
        col_list_sql = ", ".join([
            f"{col}" 
            for col in con.sql("PRAGMA table_info('sqlite_db.person')").df()["name"]
            if col not in PERSON_PII_COLUMNS
        ])

        con.sql(f"""
            COPY (
                SELECT {col_list_sql}
                FROM sqlite_db.person
            )
            TO '{outpath}'
            (FORMAT PARQUET);
        """)

    # --- PARTICIPANT_KEY_MISMATCH special case (drop id_key) ---
    elif t == "participant_key_mismatch":
        col_list_sql = ", ".join([
            f"{col}" 
            for col in con.sql("PRAGMA table_info('sqlite_db.participant_key_mismatch')").df()["name"]
            if col not in PKM_DROP_COLUMNS
        ])

        con.sql(f"""
            COPY (
                SELECT {col_list_sql}
                FROM sqlite_db.participant_key_mismatch
            )
            TO '{outpath}'
            (FORMAT PARQUET);
        """)

    # --- All other tables exported entirely ---
    else:
        con.sql(f"""
            COPY (
                SELECT *
                FROM sqlite_db.{t}
            )
            TO '{outpath}'
            (FORMAT PARQUET);
        """)

print("Done!")