import duckdb
import os
import sqlite3
<<<<<<< HEAD:database/cc_db_to_parquet.py
from config import DB_PATH, PROJECT_ROOT
=======

# ---------------------------------------------------------------------
# 0. Define DB path (EDIT THIS!)
# ---------------------------------------------------------------------
DB_PATH = r"C:\Users\DalyRob\OneDrive - State of Connecticut\Documents\GitHub Repos\ows-validation-engine\validation_dev.db"
>>>>>>> daly:cc_db_to_parquet.py

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

# Confirm attach
db_list = con.sql("PRAGMA database_list").fetchall()
print("Database list:", db_list)
print(con.sql("SELECT * FROM sqlite_db.person LIMIT 5").df())
# ---------------------------------------------------------------------
# 4. Check tables visibile in DuckDB
# ---------------------------------------------------------------------
schemas = con.sql("SELECT schema_name FROM information_schema.schemata").fetchall()
print("\nSchemas:", schemas)

all_tables = con.sql("""
    SELECT table_schema, table_name 
    FROM information_schema.tables
    ORDER BY table_schema, table_name
""").fetchall()
print("All tables:", all_tables)

# Your already-working connection (must have sqlite_db attached)
# con = duckdb.connect(':memory:')
# con.execute("LOAD sqlite_scanner;")
# con.execute("ATTACH 'validation_dev.db' AS sqlite_db (TYPE SQLITE);")

# List of all known tables inside the SQLite DB
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
<<<<<<< HEAD:database/cc_db_to_parquet.py
OUTPUT_DIR = PROJECT_ROOT / "database" / "cc_db_parquet_output"
=======
OUTPUT_DIR = r"C:\Users\DalyRob\State of Connecticut\OWS PII Storage - Documents\Career_ConneCT\.Programmatic_Data\Cleaned Programmatic Data\cc_db_parquet_output"
>>>>>>> daly:cc_db_to_parquet.py
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Export each table directly from sqlite_db.{table}
for t in sqlite_tables:
    outpath = os.path.join(OUTPUT_DIR, f"{t}.parquet")
    print(f"Exporting sqlite_db.{t} → {outpath}")

    con.sql(f"""
        COPY (
            SELECT *
            FROM sqlite_db.{t}
        )
        TO '{outpath}'
        (FORMAT PARQUET);
    """)

print("Done!")
