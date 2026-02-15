# db.py (GC Analyzer PM Dashboard + Work Orders + Weekly Planner)
# ✅ tag is NOT unique globally (can repeat across stations)
# ✅ Enforces UNIQUE(station, role) => each station has 1 Duty + 1 Standby
# ✅ Enforces UNIQUE(station, tag)  => no duplicate tag inside same station
# ✅ Safe migration for analyzers
# ✅ Work orders supports priority + est_hours (safe migration)
# ✅ Weekly planning table wo_plans (FK to work_orders)

import sqlite3
from pathlib import Path

DB_PATH = Path("gc_dashboard.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
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
    # ------------------------
    # Work Order Updates / Evidence (Checklist + Attachment)
    # - Keeps history (multiple updates per WO)
    # ------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wo_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_id INTEGER NOT NULL,
        update_ts TEXT NOT NULL DEFAULT (datetime('now')),
        action TEXT NOT NULL DEFAULT 'Update',     -- Update / Done / In Progress / etc
        performed_by TEXT NOT NULL,
        checklist_complete INTEGER NOT NULL DEFAULT 0,
        notes TEXT DEFAULT NULL,
        attachment_path TEXT DEFAULT NULL,
        FOREIGN KEY(wo_id) REFERENCES work_orders(id) ON DELETE CASCADE
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_updates_wo ON wo_updates(wo_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_updates_ts ON wo_updates(update_ts);")

    # ------------------------
    # Work Orders (create FIRST because wo_plans FK depends on it)
    # ------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS work_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wo_number TEXT NOT NULL UNIQUE,
            station TEXT NOT NULL,
            location TEXT,
            task_type TEXT NOT NULL DEFAULT 'PM',
            priority INTEGER DEFAULT 99,
            est_hours REAL DEFAULT 1.0,
            planned_date TEXT,        -- YYYY-MM-DD
            due_date TEXT,            -- YYYY-MM-DD
            status TEXT NOT NULL DEFAULT 'Planned',   -- Planned / In Progress / Done / Cancelled
            assigned_to TEXT,
            completed_date TEXT,      -- YYYY-MM-DD
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )

    # Safe migration for older work_orders table
    if _table_exists(conn, "work_orders"):
        if not _col_exists(conn, "work_orders", "priority"):
            cur.execute("ALTER TABLE work_orders ADD COLUMN priority INTEGER DEFAULT 99;")
        if not _col_exists(conn, "work_orders", "est_hours"):
            cur.execute("ALTER TABLE work_orders ADD COLUMN est_hours REAL DEFAULT 1.0;")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_due ON work_orders(due_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_station ON work_orders(station);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_status ON work_orders(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_priority ON work_orders(priority);")

    # ------------------------
    # Technicians (Master list)
    # ------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            department TEXT DEFAULT 'Instrument',
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )
    # Safe migration if old table existed without new cols
    if _table_exists(conn, "technicians"):
        if not _col_exists(conn, "technicians", "department"):
            cur.execute("ALTER TABLE technicians ADD COLUMN department TEXT DEFAULT 'Instrument';")
        if not _col_exists(conn, "technicians", "is_active"):
            cur.execute("ALTER TABLE technicians ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1;")

    # ------------------------
    # Weekly Planning (wo_plans)
    # - FK to work_orders
    # - one active plan per WO
    # ------------------------
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS wo_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wo_id INTEGER NOT NULL,
            plan_date TEXT NOT NULL,             -- YYYY-MM-DD
            mode TEXT NOT NULL DEFAULT 'Manual', -- Manual / Auto
            tech_1 TEXT NOT NULL,
            tech_2 TEXT DEFAULT NULL,
            notes TEXT DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY(wo_id) REFERENCES work_orders(id) ON DELETE CASCADE,
            UNIQUE(wo_id)
        );
        """
    )
    # Safe migration
    if _table_exists(conn, "wo_plans"):
        if not _col_exists(conn, "wo_plans", "mode"):
            cur.execute("ALTER TABLE wo_plans ADD COLUMN mode TEXT NOT NULL DEFAULT 'Manual';")
        if not _col_exists(conn, "wo_plans", "tech_2"):
            cur.execute("ALTER TABLE wo_plans ADD COLUMN tech_2 TEXT DEFAULT NULL;")
        if not _col_exists(conn, "wo_plans", "notes"):
            cur.execute("ALTER TABLE wo_plans ADD COLUMN notes TEXT DEFAULT NULL;")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_plans_date ON wo_plans(plan_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_plans_wo ON wo_plans(wo_id);")

    # -------------------------
    # analyzers table (design)
    # -------------------------
    if not _table_exists(conn, "analyzers"):
        cur.execute(
            """
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
            """
        )
        conn.commit()
    else:
        # detect old schema then migrate
        needs_migration = False
        if not _col_exists(conn, "analyzers", "station"):
            needs_migration = True
        if not _col_exists(conn, "analyzers", "role"):
            needs_migration = True

        if needs_migration:
            if not _col_exists(conn, "analyzers", "station"):
                cur.execute("ALTER TABLE analyzers ADD COLUMN station TEXT;")
                cur.execute("UPDATE analyzers SET station = location WHERE station IS NULL;")
            if not _col_exists(conn, "analyzers", "role"):
                cur.execute("ALTER TABLE analyzers ADD COLUMN role TEXT;")
                cur.execute("UPDATE analyzers SET role = 'Duty' WHERE role IS NULL;")
            if not _col_exists(conn, "analyzers", "pm_interval_days"):
                cur.execute("ALTER TABLE analyzers ADD COLUMN pm_interval_days INTEGER;")
                cur.execute("UPDATE analyzers SET pm_interval_days = 90 WHERE pm_interval_days IS NULL;")
            if not _col_exists(conn, "analyzers", "created_at"):
                cur.execute("ALTER TABLE analyzers ADD COLUMN created_at TEXT;")
                cur.execute("UPDATE analyzers SET created_at = datetime('now') WHERE created_at IS NULL;")
            conn.commit()

        # rebuild to ensure constraints (and remove any old UNIQUE(tag))
        cur.execute(
            """
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
            """
        )
        conn.commit()

        cur.execute(
            """
            INSERT OR IGNORE INTO analyzers_new
            (id, tag, location, station, role, pm_interval_days, created_at)
            SELECT
                id,
                COALESCE(tag,''),
                COALESCE(location,''),
                COALESCE(station, location, ''),
                COALESCE(role, 'Duty'),
                COALESCE(pm_interval_days, 90),
                COALESCE(created_at, datetime('now'))
            FROM analyzers;
            """
        )
        conn.commit()

        cur.execute("DROP TABLE analyzers;")
        cur.execute("ALTER TABLE analyzers_new RENAME TO analyzers;")
        conn.commit()

    # -------------------------
    # Other tables used by app
    # -------------------------
    cur.execute(
        """
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
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS data_pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analyzer_id INTEGER NOT NULL,
            data_ts TEXT NOT NULL,
            note TEXT DEFAULT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(analyzer_id) REFERENCES analyzers(id) ON DELETE CASCADE
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS duty_switch_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station TEXT NOT NULL,
            from_duty_tag TEXT,
            to_duty_tag TEXT,
            performed_by TEXT NOT NULL,
            reason TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        """
    )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_analyzers_station ON analyzers(station);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pm_logs_analyzer_date ON pm_logs(analyzer_id, pm_date);")

    conn.commit()
    conn.close()
