<<<<<<< HEAD
# db.py (UPDATED for repeating tags across stations)
# - tag is NOT unique
# - Enforces UNIQUE(station, role) so each station has only 1 Duty + 1 Standby
# - Safe migration from old analyzers table (where tag was UNIQUE)
=======
# db.py (Tasks + Validation DB)
>>>>>>> 10e4590 (synce with changes in codes)

import sqlite3
from pathlib import Path

<<<<<<< HEAD
DB_PATH = Path("gc_dashboard.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn, name: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None


def _col_exists(conn, table: str, col: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return any(r["name"] == col for r in cur.fetchall())


=======
DB_PATH = Path("tasks.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


>>>>>>> 10e4590 (synce with changes in codes)
def init_db():
    conn = get_conn()
    cur = conn.cursor()

<<<<<<< HEAD
    # -------------------------
    # Create/keep other tables
    # -------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data_pings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analyzer_id INTEGER NOT NULL,
        data_ts TEXT NOT NULL,
        note TEXT DEFAULT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(analyzer_id) REFERENCES analyzers(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pm_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analyzer_id INTEGER NOT NULL,
        pm_date TEXT NOT NULL,
        checklist_complete INTEGER NOT NULL DEFAULT 0,
        performed_by TEXT NOT NULL,
        notes TEXT DEFAULT NULL,
        attachment_path TEXT DEFAULT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(analyzer_id) REFERENCES analyzers(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS duty_switch_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station TEXT NOT NULL,
        from_duty_tag TEXT,
        to_duty_tag TEXT,
        performed_by TEXT NOT NULL,
        reason TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # -------------------------
    # analyzers table (NEW DESIGN)
    # -------------------------
    if not _table_exists(conn, "analyzers"):
        cur.execute("""
        CREATE TABLE analyzers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL,
            location TEXT NOT NULL,
            station TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Duty','Standby')),
            pm_interval_days INTEGER NOT NULL DEFAULT 90,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(station, role),
            UNIQUE(station, tag)
        );
        """)
        conn.commit()
        conn.close()
        return

    # If analyzers exists, check if it has the new columns. If old schema -> migrate.
    # Old schema likely had: tag UNIQUE + no station/role constraints.
    needs_migration = False
    if not _col_exists(conn, "analyzers", "station"):
        needs_migration = True
    if not _col_exists(conn, "analyzers", "role"):
        needs_migration = True

    if needs_migration:
        # Add missing cols first (if needed)
        if not _col_exists(conn, "analyzers", "station"):
            cur.execute("ALTER TABLE analyzers ADD COLUMN station TEXT;")
            cur.execute("UPDATE analyzers SET station = location WHERE station IS NULL;")
        if not _col_exists(conn, "analyzers", "role"):
            cur.execute("ALTER TABLE analyzers ADD COLUMN role TEXT;")
        conn.commit()

    # Now we must remove UNIQUE(tag). SQLite can't drop constraints, so rebuild table.
    # We rebuild ALWAYS into new structure if the current table has UNIQUE(tag) behavior.
    # We'll detect by trying to create a new table with same name -> rebuild with tmp table.
    try:
        # Create new table temp with correct constraints
        cur.execute("""
        CREATE TABLE IF NOT EXISTS analyzers_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL,
            location TEXT NOT NULL,
            station TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Duty','Standby')),
            pm_interval_days INTEGER NOT NULL DEFAULT 90,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(station, role),
            UNIQUE(station, tag)
        );
        """)
        conn.commit()

        # Copy what we can. Old rows might have role NULL — keep them but normalize:
        # If role is NULL, set to 'Duty' (you can later fix in UI).
        cur.execute("""
            INSERT OR IGNORE INTO analyzers_new(id, tag, location, station, role, pm_interval_days, created_at)
            SELECT
                id,
                COALESCE(tag,''),
                COALESCE(location,''),
                COALESCE(station, location),
                COALESCE(role, 'Duty'),
                COALESCE(pm_interval_days, 90),
                COALESCE(created_at, datetime('now'))
            FROM analyzers;
        """)
        conn.commit()

        # Replace old table
        cur.execute("DROP TABLE analyzers;")
        cur.execute("ALTER TABLE analyzers_new RENAME TO analyzers;")
        conn.commit()

    finally:
        conn.close()
=======
    # ------------------------
    # Tasks Table
    # ------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_number TEXT NOT NULL,
        station TEXT NOT NULL,
        location TEXT,
        department TEXT NOT NULL,
        task_type TEXT NOT NULL,
        asset_tag TEXT,
        planned_date TEXT,
        due_date TEXT,
        status TEXT NOT NULL DEFAULT 'Planned',
        assigned_to TEXT,
        completed_date TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_wo ON tasks(wo_number);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tasks_station ON tasks(station);")

    # ------------------------
    # Attachments Table
    # ------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS task_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_attach_task ON task_attachments(task_id);")

    # ------------------------
    # Customers Table
    # ------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL UNIQUE
    );
    """)

    # ------------------------
    # Validations Table
    # ------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS validations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        validation_type TEXT NOT NULL,
        station TEXT,
        asset_tag TEXT,
        planned_date TEXT,
        due_date TEXT,
        status TEXT NOT NULL DEFAULT 'Planned',
        result TEXT,
        report_no TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_val_customer ON validations(customer_name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_val_type ON validations(validation_type);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_val_due ON validations(due_date);")

    conn.commit()
    conn.close()
>>>>>>> 10e4590 (synce with changes in codes)
