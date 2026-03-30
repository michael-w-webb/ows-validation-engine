import sqlite3
from config import DB_PATH

def add_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add 'completed' column (nullable, no default)
    try:
        cursor.execute("""
            ALTER TABLE validation_run 
            ADD COLUMN completed INTEGER;
        """)
        print("Added 'completed' column")
    except sqlite3.OperationalError as e:
        print(f"Skipped 'completed': {e}")

    # Add 'run_description' column
    try:
        cursor.execute("""
            ALTER TABLE validation_run 
            ADD COLUMN run_description TEXT;
        """)
        print("Added 'run_description' column")
    except sqlite3.OperationalError as e:
        print(f"Skipped 'run_description': {e}")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    add_columns()