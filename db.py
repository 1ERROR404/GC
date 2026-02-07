# db.py (UPDATED for repeating tags across stations)
# - tag is NOT unique
# - Enforces UNIQUE(station, role) so each station has only 1 Duty + 1 Standby
# - Safe migration from old analyzers table (where tag was UNIQUE)

import sqlite3
from pathlib import Path

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


def init_db():
    conn = get_conn()
    cur = conn.cursor()

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
