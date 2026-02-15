# app.py (GC Analyzer PM Dashboard + Work Orders Compliance + Weekly Planner)
# ✅ NO JavaScript
# ✅ NO Charts
# ✅ Mobile friendly
# ✅ Stations: Duty + Standby
# ✅ PM logs + attachments
# ✅ Work Orders + Weekly/Monthly Compliance (based on DUE DATE from SAP / manual)
# ✅ Weekly Planner (PRIVATE): stores your plan in wo_plans (does NOT change SAP due dates)
# ✅ Manpower assign: Manual + Auto, supports 1 or 2 tech per WO

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
import mimetypes
from typing import Optional, Tuple

from db import init_db, get_conn

# -----------------------------
# App config + DB init
# -----------------------------
st.set_page_config(page_title="GC Analyzer PM Dashboard", layout="wide")
init_db()

# Upload folder (you can change this to OneDrive later)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# (Optional) Simple Login
# -----------------------------
def require_login_clean():
    # If you don't want login for now, comment out require_login_clean() call below.
    if st.session_state.get("logged_in"):
        return

    app_user = st.secrets.get("APP_USER", "demo")
    app_pass = st.secrets.get("APP_PASS", "1234")

    st.markdown(
        """
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .login-container {max-width: 420px; margin: auto; padding-top: 8vh;}
        .login-title {text-align: center; font-size: 26px; font-weight: 800; margin-bottom: 18px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Login to Dashboard</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    st.markdown("</div>", unsafe_allow_html=True)

    if login_btn:
        if username == app_user and password == app_pass:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()


# Enable login (comment this if you want no login)
require_login_clean()

with st.sidebar:
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()


# -----------------------------
# UI CSS (mobile friendly)
# -----------------------------
st.markdown(
    """
<style>
.badge{
  display:inline-block; padding:2px 10px; border-radius:999px;
  font-size: 0.78rem; border:1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05); opacity: 0.95;
}
.badge-done { background: rgba(46, 204, 113, 0.15); border-color: rgba(46, 204, 113, 0.35); }
.badge-plan { background: rgba(52, 152, 219, 0.15); border-color: rgba(52, 152, 219, 0.35); }
.badge-prog { background: rgba(241, 196, 15, 0.15); border-color: rgba(241, 196, 15, 0.35); }
.badge-over { background: rgba(231, 76, 60, 0.15); border-color: rgba(231, 76, 60, 0.35); }
.badge-auto { background: rgba(155, 89, 182, 0.15); border-color: rgba(155, 89, 182, 0.35); }

.card{
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 12px 12px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.10);
  margin-bottom: 10px;
}
.card-title{ font-weight: 750; font-size: 0.98rem; margin-bottom: 6px; }
.card-sub{ font-size: 0.82rem; opacity: 0.80; line-height: 1.35; }

.day-col-title{ font-weight: 800; margin: 0 0 8px 0; }
.day-chip{ font-size: 0.80rem; opacity: 0.85; margin-left: 6px; }

@media (max-width: 700px){
  .card-title { font-size: 0.95rem; }
  .card-sub { font-size: 0.80rem; }
}
div[data-testid="stVerticalBlock"] { gap: 0.65rem; }
section.main > div { padding-top: 1rem; padding-bottom: 1rem; }
button[kind="secondary"], button[kind="primary"] { padding: 0.35rem 0.6rem; }

@media (max-width: 700px) {
  html, body, [class*="css"] { font-size: 14px !important; }
  div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; max-width: 100% !important; }
  div[data-testid="stDataFrame"] { overflow-x: auto; }
  h1 { font-size: 1.35rem !important; }
  h2 { font-size: 1.12rem !important; }
  h3 { font-size: 1.03rem !important; }
}

/* KPI cards */
.kpi-row{
  display:flex; gap:12px; justify-content:center; align-items:stretch; flex-wrap:wrap;
  margin: 0.2rem 0 0.8rem 0;
}
.kpi-card{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 12px 14px;
  width: 210px;
  text-align:center;
  box-shadow: 0 8px 22px rgba(0,0,0,0.12);
}
.kpi-title{ font-size: 0.85rem; opacity: .8; margin-bottom: 4px;}
.kpi-value{ font-size: 2rem; font-weight: 750; line-height: 1.05; }
.kpi-sub{ font-size: 0.8rem; opacity: .65; margin-top: 2px;}
@media (max-width:700px){
  .kpi-card{ width: 46vw; min-width: 160px; }
  .kpi-value{ font-size: 1.6rem; }
}

/* Control bar */
.control-bar{
  display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; justify-content:space-between;
  margin: 0.2rem 0 0.6rem 0;
}
.control-box{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 10px 12px;
  flex: 1 1 260px;
}
.small-label{ font-size: 0.78rem; opacity: .7; margin-bottom: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def add_wo_update(wo_id: int, action: str, performed_by: str, checklist_complete: bool,
                  notes: Optional[str], attachment_path: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO wo_updates(wo_id, action, performed_by, checklist_complete, notes, attachment_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (wo_id, action, performed_by.strip(), 1 if checklist_complete else 0, notes, attachment_path))
    conn.commit()
    conn.close()

def get_wo_updates(wo_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT update_ts, action, performed_by, checklist_complete, notes, attachment_path
        FROM wo_updates
        WHERE wo_id=?
        ORDER BY update_ts DESC
        LIMIT 50
    """, conn, params=(wo_id,))
    conn.close()
    return df

def set_wo_status(wo_id: int, new_status: str, completed_date: Optional[str] = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE work_orders
        SET status=?,
            completed_date=?,
            updated_at=datetime('now')
        WHERE id=?
    """, (new_status, completed_date, wo_id))
    conn.commit()
    conn.close()

DAYS7 = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def iso_to_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def safe_str(x, default: str = "-") -> str:
    if x is None:
        return default
    if isinstance(x, float) and pd.isna(x):
        return default
    if isinstance(x, str) and not x.strip():
        return default
    return str(x)


def parse_date_ymd(s: Optional[str]) -> Optional[date]:
    if not s or not str(s).strip():
        return None
    return datetime.strptime(str(s).strip(), "%Y-%m-%d").date()


def week_start_sunday(d: date) -> date:
    # Mon=0..Sun=6  -> want Sunday start
    shift = (d.weekday() + 1) % 7
    return d - timedelta(days=shift)


def period_range_ymd(mode: str, anchor: date) -> Tuple[date, date]:
    if mode == "Weekly":
        start = week_start_sunday(anchor)
        end = start + timedelta(days=6)
        return start, end

    start = anchor.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1, day=1)
    else:
        next_month = start.replace(month=start.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return start, end


def show_attachment(path_str: Optional[str], key_prefix: str):
    if not path_str or not str(path_str).strip():
        st.info("No attachment.")
        return

    p = Path(str(path_str))
    if not p.exists():
        st.warning("Attachment file not found on this PC / server.")
        st.code(str(p))
        return

    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "application/octet-stream"

    if mime.startswith("image/"):
        st.image(str(p), caption=p.name, use_container_width=True)

    st.download_button(
        label=f"📥 Download: {p.name}",
        data=p.read_bytes(),
        file_name=p.name,
        mime=mime,
        key=f"dl_{key_prefix}_{p.name}_{p.stat().st_mtime_ns}",
    )


# -----------------------------
# Planning tables (ensure exist)
# -----------------------------
def ensure_planning_tables():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        department TEXT DEFAULT 'Instrument',
        is_active INTEGER NOT NULL DEFAULT 1
    );
    """)

    cur.execute("""
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
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_plans_date ON wo_plans(plan_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_plans_wo ON wo_plans(wo_id);")

    conn.commit()
    conn.close()


def fetch_technicians(dept: str = "Instrument") -> list[str]:
    ensure_planning_tables()
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT name FROM technicians WHERE is_active=1 AND department=? ORDER BY name",
        conn, params=(dept,)
    )
    conn.close()
    return df["name"].tolist()


def add_technician(name: str, dept: str = "Instrument"):
    ensure_planning_tables()
    name = name.strip()
    if not name:
        raise ValueError("Technician name is required.")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO technicians(name, department, is_active) VALUES (?, ?, 1)", (name, dept))
    conn.commit()
    conn.close()


def fetch_plans_in_period(start_ymd: str, end_ymd: str) -> pd.DataFrame:
    ensure_planning_tables()
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT p.*, w.wo_number, w.station, w.location, w.task_type, w.status, w.due_date
        FROM wo_plans p
        JOIN work_orders w ON w.id = p.wo_id
        WHERE p.plan_date BETWEEN ? AND ?
        ORDER BY p.plan_date ASC, w.station ASC, w.wo_number ASC
        """,
        conn, params=(start_ymd, end_ymd)
    )
    conn.close()
    return df


def upsert_plan(wo_id: int, plan_date: str, mode: str, tech_1: str, tech_2: Optional[str], notes: Optional[str]):
    ensure_planning_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO wo_plans(wo_id, plan_date, mode, tech_1, tech_2, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(wo_id) DO UPDATE SET
            plan_date=excluded.plan_date,
            mode=excluded.mode,
            tech_1=excluded.tech_1,
            tech_2=excluded.tech_2,
            notes=excluded.notes,
            updated_at=datetime('now')
    """, (wo_id, plan_date, mode, tech_1, tech_2, notes))
    conn.commit()
    conn.close()


def delete_plan(wo_id: int):
    ensure_planning_tables()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM wo_plans WHERE wo_id=?", (wo_id,))
    conn.commit()
    conn.close()


def auto_assign_week(
    work_orders_df: pd.DataFrame,
    techs: list[str],
    start: date,
    end: date,
    max_per_tech_per_day: int = 2,
    two_tech_default: bool = False,
):
    """
    Auto-balances WOs across Sun–Thu and assigns tech_1 (+ optional tech_2).
    Stores plan in wo_plans (doesn't change SAP due_date).
    """
    if not techs:
        raise ValueError("No technicians found. Add technicians first.")

    # Working days Sun-Thu only
    days = []
    d = start
    while d <= end:
        if d.weekday() in [6, 0, 1, 2, 3]:  # Sun,Mon,Tue,Wed,Thu
            days.append(d)
        d += timedelta(days=1)
    if not days:
        raise ValueError("Selected period has no working days (Sun–Thu).")

    # load map: (date, tech)->count
    load = {(day.strftime("%Y-%m-%d"), t): 0 for day in days for t in techs}

    # count existing plans for week
    existing = fetch_plans_in_period(days[0].strftime("%Y-%m-%d"), days[-1].strftime("%Y-%m-%d"))
    for _, r in existing.iterrows():
        pd_ = str(r["plan_date"])
        t1 = str(r["tech_1"]) if r.get("tech_1") else None
        t2 = str(r["tech_2"]) if r.get("tech_2") else None
        if t1 and (pd_, t1) in load:
            load[(pd_, t1)] += 1
        if t2 and (pd_, t2) in load:
            load[(pd_, t2)] += 1

    # simple round-robin across days
    day_idx = 0
    for _, wo in work_orders_df.iterrows():
        wo_id = int(wo["id"])
        plan_day = days[day_idx % len(days)]
        plan_day_s = plan_day.strftime("%Y-%m-%d")
        day_idx += 1

        tech_sorted = sorted(techs, key=lambda t: load[(plan_day_s, t)])

        tech_1 = None
        for t in tech_sorted:
            if load[(plan_day_s, t)] < max_per_tech_per_day:
                tech_1 = t
                break
        if not tech_1:
            tech_1 = tech_sorted[0]
        load[(plan_day_s, tech_1)] += 1

        tech_2 = None
        if two_tech_default:
            for t in tech_sorted:
                if t != tech_1 and load[(plan_day_s, t)] < max_per_tech_per_day:
                    tech_2 = t
                    break
            if tech_2:
                load[(plan_day_s, tech_2)] += 1

        upsert_plan(
            wo_id=wo_id,
            plan_date=plan_day_s,
            mode="Auto",
            tech_1=tech_1,
            tech_2=tech_2,
            notes="Auto planned",
        )


# -----------------------------
# DB functions (GC / PM)
# -----------------------------
def days_to_due(last_pm: Optional[str], interval_days: int) -> Optional[int]:
    if not last_pm:
        return None
    due_dt = iso_to_dt(last_pm) + timedelta(days=interval_days)
    return (due_dt.date() - datetime.now().date()).days


def due_bucket(days_left: Optional[int]) -> str:
    if days_left is None:
        return "Unknown"
    if days_left < 0:
        return "Overdue"
    if days_left <= 14:
        return "Due Soon"
    return "OK"


def station_pm_header_status(station_df: pd.DataFrame) -> str:
    buckets = station_df["pm_bucket"].tolist() if "pm_bucket" in station_df.columns else []
    if "Overdue" in buckets:
        return "🔴 PM Overdue"
    if "Due Soon" in buckets:
        return "🟠 PM Due Soon"
    if "Unknown" in buckets:
        return "⚪ PM Unknown"
    return "🟢 PM OK"


def evidence_icon(attachment_path: Optional[str]) -> str:
    if attachment_path is not None and pd.notna(attachment_path) and str(attachment_path).strip():
        return "📎"
    return "⚪"


def fetch_kpis() -> pd.DataFrame:
    conn = get_conn()

    analyzers = pd.read_sql_query(
        """
        SELECT id, tag, location, station, role, pm_interval_days
        FROM analyzers
        ORDER BY station, role, id
        """,
        conn,
    )

    last_pm_row = pd.read_sql_query(
        """
        SELECT l.analyzer_id,
               l.pm_date,
               l.checklist_complete,
               l.performed_by,
               l.notes,
               l.attachment_path
        FROM pm_logs l
        INNER JOIN (
            SELECT analyzer_id, MAX(pm_date) AS max_pm_date
            FROM pm_logs
            GROUP BY analyzer_id
        ) x
        ON x.analyzer_id = l.analyzer_id
       AND x.max_pm_date = l.pm_date
        """,
        conn,
    )

    conn.close()

    df = analyzers.merge(last_pm_row, left_on="id", right_on="analyzer_id", how="left").drop(columns=["analyzer_id"])
    df["station"] = df["station"].fillna(df["location"])

    def _calc_days(r):
        pm_date = r.get("pm_date")
        last = None if (pm_date is None or pd.isna(pm_date)) else str(pm_date)
        return days_to_due(last, int(r["pm_interval_days"]))

    df["pm_days_left"] = df.apply(_calc_days, axis=1)
    df["pm_bucket"] = df["pm_days_left"].apply(due_bucket)

    def _next_due(r):
        pm_date = r.get("pm_date")
        if pm_date is None or pd.isna(pm_date):
            return None
        due_dt = iso_to_dt(str(pm_date)) + timedelta(days=int(r["pm_interval_days"]))
        return due_dt.strftime("%Y-%m-%d")

    df["next_pm_due"] = df.apply(_next_due, axis=1)
    return df


def add_station_pair_add_only(station: str, location: str, duty_tag: str, standby_tag: str, pm_interval_days: int):
    station = station.strip()
    location = location.strip()
    duty_tag = duty_tag.strip()
    standby_tag = standby_tag.strip()

    if not station or not location or not duty_tag or not standby_tag:
        raise ValueError("Please fill: station, location, duty tag, standby tag.")
    if duty_tag == standby_tag:
        raise ValueError("Duty tag and Standby tag cannot be the same.")

    conn = get_conn()

    existing_station = pd.read_sql_query(
        "SELECT tag, role FROM analyzers WHERE station=? AND role IN ('Duty','Standby')",
        conn,
        params=(station,),
    )
    if len(existing_station) > 0:
        conn.close()
        raise ValueError(
            f"Station '{station}' already exists.\n"
            "Use a different Station name OR use Edit Station tab."
        )

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO analyzers(tag, location, station, role, pm_interval_days)
        VALUES(?, ?, ?, 'Duty', ?)
        """,
        (duty_tag, location, station, int(pm_interval_days)),
    )
    cur.execute(
        """
        INSERT INTO analyzers(tag, location, station, role, pm_interval_days)
        VALUES(?, ?, ?, 'Standby', ?)
        """,
        (standby_tag, location, station, int(pm_interval_days)),
    )

    conn.commit()
    conn.close()


def update_station_pair(station_old: str, station_new: str, location: str,
                        duty_tag: str, standby_tag: str, pm_interval_days: int):
    station_old = station_old.strip()
    station_new = station_new.strip()
    location = location.strip()
    duty_tag = duty_tag.strip()
    standby_tag = standby_tag.strip()

    if not station_new or not location or not duty_tag or not standby_tag:
        raise ValueError("Please fill all fields.")
    if duty_tag == standby_tag:
        raise ValueError("Duty tag and Standby tag cannot be the same.")

    conn = get_conn()

    existing = pd.read_sql_query(
        "SELECT id, role FROM analyzers WHERE station=? AND role IN ('Duty','Standby')",
        conn,
        params=(station_old,),
    )
    if len(existing) == 0:
        conn.close()
        raise ValueError("Selected station not found.")

    if station_new != station_old:
        check_new = pd.read_sql_query(
            "SELECT 1 FROM analyzers WHERE station=? LIMIT 1",
            conn,
            params=(station_new,),
        )
        if len(check_new) > 0:
            conn.close()
            raise ValueError(f"Station name '{station_new}' already exists.")

    duty_row = pd.read_sql_query(
        "SELECT id FROM analyzers WHERE station=? AND role='Duty' LIMIT 1",
        conn,
        params=(station_old,),
    )
    standby_row = pd.read_sql_query(
        "SELECT id FROM analyzers WHERE station=? AND role='Standby' LIMIT 1",
        conn,
        params=(station_old,),
    )
    if len(duty_row) == 0 or len(standby_row) == 0:
        conn.close()
        raise ValueError("This station must have both Duty and Standby.")

    duty_id = int(duty_row.iloc[0]["id"])
    standby_id = int(standby_row.iloc[0]["id"])

    dup = pd.read_sql_query(
        """
        SELECT id, role, tag
        FROM analyzers
        WHERE station=? AND tag IN (?, ?)
          AND id NOT IN (?, ?)
        """,
        conn,
        params=(station_new, duty_tag, standby_tag, duty_id, standby_id),
    )
    if len(dup) > 0:
        conn.close()
        raise ValueError("Duplicate tag inside this station (station, tag must be unique).")

    cur = conn.cursor()
    cur.execute("BEGIN")
    cur.execute(
        """
        UPDATE analyzers
        SET station=?, location=?, tag=?, pm_interval_days=?
        WHERE id=?
        """,
        (station_new, location, duty_tag, int(pm_interval_days), duty_id),
    )
    cur.execute(
        """
        UPDATE analyzers
        SET station=?, location=?, tag=?, pm_interval_days=?
        WHERE id=?
        """,
        (station_new, location, standby_tag, int(pm_interval_days), standby_id),
    )

    conn.commit()
    conn.close()


def add_pm_log(analyzer_id: int, pm_date: str, checklist_complete: bool, performed_by: str,
               notes: Optional[str], attachment_path: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO pm_logs(analyzer_id, pm_date, checklist_complete, performed_by, notes, attachment_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (analyzer_id, pm_date, 1 if checklist_complete else 0, performed_by.strip(), notes, attachment_path),
    )
    conn.commit()
    conn.close()


def get_pm_logs(analyzer_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT pm_date, checklist_complete, performed_by, notes, attachment_path
        FROM pm_logs
        WHERE analyzer_id=?
        ORDER BY pm_date DESC
        LIMIT 50
        """,
        conn,
        params=(analyzer_id,),
    )
    conn.close()
    return df


def station_summary(df_all: pd.DataFrame, station: str):
    sg = df_all[df_all["station"] == station].copy()
    header = station_pm_header_status(sg)

    duty = sg[sg["role"] == "Duty"].head(1)
    standby = sg[sg["role"] == "Standby"].head(1)

    duty_tag = safe_str(duty["tag"].iloc[0] if len(duty) else None)
    standby_tag = safe_str(standby["tag"].iloc[0] if len(standby) else None)

    duty_due = safe_str(duty["next_pm_due"].iloc[0] if (len(duty) and pd.notna(duty["next_pm_due"].iloc[0])) else None)
    standby_due = safe_str(standby["next_pm_due"].iloc[0] if (len(standby) and pd.notna(standby["next_pm_due"].iloc[0])) else None)

    duty_ev = evidence_icon(duty["attachment_path"].iloc[0]) if len(duty) else "⚪"
    standby_ev = evidence_icon(standby["attachment_path"].iloc[0]) if len(standby) else "⚪"

    return {
        "header": header,
        "duty_tag": duty_tag,
        "standby_tag": standby_tag,
        "duty_due": duty_due,
        "standby_due": standby_due,
        "duty_ev": duty_ev,
        "standby_ev": standby_ev,
    }


# -----------------------------
# Work Orders table (auto create + migrate if needed)
# -----------------------------
def ensure_work_orders_table():
    conn = get_conn()
    cur = conn.cursor()

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
            planned_date TEXT,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'Planned',
            assigned_to TEXT,
            completed_date TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )

    cur.execute("PRAGMA table_info(work_orders);")
    cols = {r[1] for r in cur.fetchall()}

    if "priority" not in cols:
        cur.execute("ALTER TABLE work_orders ADD COLUMN priority INTEGER DEFAULT 99;")
    if "est_hours" not in cols:
        cur.execute("ALTER TABLE work_orders ADD COLUMN est_hours REAL DEFAULT 1.0;")

    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_due ON work_orders(due_date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_station ON work_orders(station);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_status ON work_orders(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wo_priority ON work_orders(priority);")

    conn.commit()
    conn.close()


def fetch_work_orders() -> pd.DataFrame:
    ensure_work_orders_table()
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        ORDER BY
          CASE status
            WHEN 'Planned' THEN 1
            WHEN 'In Progress' THEN 2
            WHEN 'Done' THEN 3
            WHEN 'Cancelled' THEN 4
            ELSE 9
          END,
          due_date IS NULL, due_date ASC,
          priority ASC,
          id DESC
        """,
        conn,
    )
    conn.close()
    return df


def insert_work_order(payload: dict) -> int:
    ensure_work_orders_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO work_orders
        (wo_number, station, location, task_type, priority, est_hours, planned_date, due_date, status,
         assigned_to, completed_date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (
            payload["wo_number"],
            payload["station"],
            payload.get("location"),
            payload.get("task_type", "PM"),
            int(payload.get("priority", 99)),
            float(payload.get("est_hours", 1.0)),
            payload.get("planned_date"),
            payload.get("due_date"),
            payload.get("status", "Planned"),
            payload.get("assigned_to"),
            payload.get("completed_date"),
            payload.get("notes"),
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(new_id)


def update_work_order(wo_id: int, payload: dict):
    ensure_work_orders_table()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE work_orders
        SET wo_number=?, station=?, location=?, task_type=?, priority=?, est_hours=?,
            planned_date=?, due_date=?, status=?, assigned_to=?, completed_date=?, notes=?,
            updated_at=datetime('now')
        WHERE id=?
        """,
        (
            payload["wo_number"],
            payload["station"],
            payload.get("location"),
            payload.get("task_type", "PM"),
            int(payload.get("priority", 99)),
            float(payload.get("est_hours", 1.0)),
            payload.get("planned_date"),
            payload.get("due_date"),
            payload.get("status", "Planned"),
            payload.get("assigned_to"),
            payload.get("completed_date"),
            payload.get("notes"),
            wo_id,
        ),
    )
    conn.commit()
    conn.close()


# -----------------------------
# UI: Title + Tabs
# -----------------------------
st.title("GC Analyzer PM Tracking Dashboard")

tab_dash, tab_stations, tab_pm, tab_wo, tab_today, tab_weekly = st.tabs(
    ["📊 Dashboard", "🏭 Stations Management", "🛠 PM Logs & Attachments", "📋 Work Orders & Compliance", "📌 Today & Tomorrow", "📅 Weekly Planner (Private Plan)"]
)

# -----------------------------
# Dashboard render helpers
# -----------------------------
def render_station_grid(df: pd.DataFrame, stations: list, mode: str):
    if mode == "BIG":
        cols_per_row = 1
    elif mode == "MED":
        cols_per_row = 2
    else:
        cols_per_row = 3

    rows = [stations[i:i + cols_per_row] for i in range(0, len(stations), cols_per_row)]
    for row_stations in rows:
        cols = st.columns(cols_per_row)
        for i, station in enumerate(row_stations):
            s = station_summary(df, station)
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{station}**")
                    st.markdown(s["header"])

                    if mode == "BIG":
                        st.markdown(
                            f"""
                            <div style="font-size: 1rem; line-height: 1.55;">
                              <b>GC-01 (Duty)</b>: {s["duty_tag"]} &nbsp; {s["duty_ev"]}<br/>
                              <span style="opacity:0.8;">Next Due:</span> {s["duty_due"]}<br/>
                              <b>GC-02 (Standby)</b>: {s["standby_tag"]} &nbsp; {s["standby_ev"]}<br/>
                              <span style="opacity:0.8;">Next Due:</span> {s["standby_due"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    elif mode == "MED":
                        st.markdown(
                            f"""
                            <div style="font-size: 0.95rem; line-height: 1.45;">
                              <b>GC-01</b>: {s["duty_tag"]} {s["duty_ev"]}<br/>
                              <span style="opacity:0.8;">Due:</span> {s["duty_due"]}<br/>
                              <b>GC-02</b>: {s["standby_tag"]} {s["standby_ev"]}<br/>
                              <span style="opacity:0.8;">Due:</span> {s["standby_due"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="font-size: 0.9rem; line-height: 1.35;">
                              <b>GC-01</b>: {s["duty_tag"]} {s["duty_ev"]}<br/>
                              <b>GC-02</b>: {s["standby_tag"]} {s["standby_ev"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if st.button("Open", key=f"open_station_{mode}_{station}"):
                        st.session_state["selected_station"] = station
                        st.rerun()


def render_station_list(df: pd.DataFrame, stations: list):
    rows = []
    for station in stations:
        s = station_summary(df, station)
        rows.append({
            "Station": station,
            "PM": s["header"].replace("PM ", ""),
            "GC-01 Tag": s["duty_tag"],
            "GC-01 Due": s["duty_due"],
            "GC-01 Ev": s["duty_ev"],
            "GC-02 Tag": s["standby_tag"],
            "GC-02 Due": s["standby_due"],
            "GC-02 Ev": s["standby_ev"],
        })

    t = pd.DataFrame(rows)
    st.dataframe(t, use_container_width=True, hide_index=True)

    st.caption("Open station details:")
    btn_cols = st.columns(6)
    for idx, station in enumerate(stations):
        with btn_cols[idx % 6]:
            if st.button(station, key=f"open_list_{station}"):
                st.session_state["selected_station"] = station
                st.rerun()


# -----------------------------
# Tab: Dashboard
# -----------------------------
with tab_dash:
    df = fetch_kpis()

    total_analyzers = len(df)
    total_stations = df["station"].nunique() if len(df) else 0
    overdue_count = int((df["pm_bucket"] == "Overdue").sum()) if len(df) else 0
    due_soon_count = int((df["pm_bucket"] == "Due Soon").sum()) if len(df) else 0

    st.markdown(
        f"""
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-title">Stations</div><div class="kpi-value">{total_stations}</div><div class="kpi-sub">Active stations</div></div>
          <div class="kpi-card"><div class="kpi-title">Total GC</div><div class="kpi-value">{total_analyzers}</div><div class="kpi-sub">All analyzers</div></div>
          <div class="kpi-card"><div class="kpi-title">PM Overdue</div><div class="kpi-value">{overdue_count}</div><div class="kpi-sub">Needs action</div></div>
          <div class="kpi-card"><div class="kpi-title">PM Due Soon</div><div class="kpi-value">{due_soon_count}</div><div class="kpi-sub">Next 14 days</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="control-bar">', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Search</div>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="Station / Location / Tag", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    cols = st.columns([1.2, 1])
    with cols[0]:
        st.markdown('<div class="small-label">PM Filter</div>', unsafe_allow_html=True)
        filter_choice = st.radio(
            "PM Filter",
            ["ALL", "OVERDUE", "DUESOON"],
            index=["ALL", "OVERDUE", "DUESOON"].index(st.session_state.get("station_filter", "ALL")),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["station_filter"] = filter_choice

    with cols[1]:
        st.markdown('<div class="small-label">View</div>', unsafe_allow_html=True)
        view_choice = st.radio(
            "View",
            ["LIST", "BIG", "MED", "SMALL"],
            index=["LIST", "BIG", "MED", "SMALL"].index(st.session_state.get("view_mode", "SMALL")),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state["view_mode"] = view_choice

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if "selected_station" not in st.session_state:
        st.session_state["selected_station"] = None
    if "open_attach_for" not in st.session_state:
        st.session_state["open_attach_for"] = None

    if len(df) == 0:
        st.info("No stations yet. Add station pairs first.")
    else:
        station_list = sorted(df["station"].unique().tolist())
        if search and search.strip():
            q = search.strip().lower()
            station_list = [
                s for s in station_list
                if q in str(s).lower()
                or q in str(df[df["station"] == s]["location"].iloc[0]).lower()
                or q in " ".join(df[df["station"] == s]["tag"].astype(str).tolist()).lower()
            ]

        stations = []
        for station, g in df.groupby("station"):
            if station not in station_list:
                continue
            any_overdue = (g["pm_bucket"] == "Overdue").any()
            any_due_soon = (g["pm_bucket"] == "Due Soon").any()
            stations.append((station, any_overdue, any_due_soon))
        station_df = pd.DataFrame(stations, columns=["station", "any_overdue", "any_due_soon"])

        mode = st.session_state.get("station_filter", "ALL")
        filtered_stations = station_df["station"].tolist()
        if mode == "OVERDUE":
            filtered_stations = station_df[station_df["any_overdue"]]["station"].tolist()
        elif mode == "DUESOON":
            filtered_stations = station_df[station_df["any_due_soon"]]["station"].tolist()

        filtered_stations = sorted(filtered_stations)

        st.caption("Click a station to open full details.")
        vm = st.session_state.get("view_mode", "SMALL")
        if vm == "LIST":
            render_station_list(df, filtered_stations)
        elif vm == "BIG":
            render_station_grid(df, filtered_stations, "BIG")
        elif vm == "MED":
            render_station_grid(df, filtered_stations, "MED")
        else:
            render_station_grid(df, filtered_stations, "SMALL")

        sel = st.session_state.get("selected_station")
        if sel:
            st.divider()
            with st.expander(f"📌 Station Details — {sel}", expanded=True):
                if st.button("Close Details", key="close_details"):
                    st.session_state["selected_station"] = None
                    st.rerun()

                sg = df[df["station"] == sel].copy()
                st.markdown(f"### {station_pm_header_status(sg)}")

                duty_df = sg[sg["role"] == "Duty"]
                standby_df = sg[sg["role"] == "Standby"]

                cols2 = st.columns(2)

                def render_gc(col, label, role_df, role_name):
                    with col:
                        st.markdown(f"#### {label}")
                        if len(role_df) == 0:
                            st.warning(f"{role_name} GC not defined.")
                            return

                        item = role_df.iloc[0]
                        aid = int(item["id"])

                        pm_date = item["pm_date"] if pd.notna(item.get("pm_date")) else "-"
                        pm_by = item["performed_by"] if pd.notna(item.get("performed_by")) else "-"
                        pm_attach = item.get("attachment_path")
                        evidence = "📎 Attached" if (pm_attach is not None and pd.notna(pm_attach) and str(pm_attach).strip()) else "⚪ No attachment"
                        next_due = item["next_pm_due"] if pd.notna(item.get("next_pm_due")) else "-"

                        st.write(f"**Tag:** {item['tag']}")
                        st.write(f"**Status:** {role_name}")
                        st.write(f"**Last PM Date:** {pm_date}")
                        st.write(f"**Performed By:** {pm_by}")
                        st.write(f"**Evidence:** {evidence}")
                        st.write(f"**Next PM Due:** {next_due}")

                        if st.button("📎 PM + Attachment", key=f"pmatt_details_{sel}_{aid}"):
                            st.session_state["open_attach_for"] = aid
                            st.rerun()

                        if pm_attach is not None and pd.notna(pm_attach) and str(pm_attach).strip():
                            with st.expander("📎 View / Download last PM attachment"):
                                show_attachment(str(pm_attach), key_prefix=f"details_{sel}_{aid}")

                render_gc(cols2[0], "GC-01", duty_df, "Duty")
                render_gc(cols2[1], "GC-02", standby_df, "Standby")

        open_for = st.session_state.get("open_attach_for")
        if open_for:
            st.divider()
            st.subheader("PM Log with Attachment")

            df2 = fetch_kpis()
            row = df2[df2["id"] == open_for]
            tag = row["tag"].iloc[0] if len(row) else "Unknown"

            with st.form("attach_form"):
                st.text_input("GC Tag", value=tag, disabled=True)
                performed_by = st.text_input("Performed by", value=st.session_state.get("quick_name", ""))
                pm_date = st.text_input("PM date (YYYY-MM-DD HH:MM:SS)", value=now_iso())
                checklist = st.checkbox("PM checklist completion", value=True)
                notes = st.text_area("Notes", placeholder="Findings / parts changed / WO ref")
                file = st.file_uploader("Attachment", type=None)
                submit = st.form_submit_button("Save PM + Attachment")

                if submit:
                    if not performed_by.strip():
                        st.error("Please enter performed by.")
                    else:
                        try:
                            iso_to_dt(pm_date)
                            st.session_state["quick_name"] = performed_by.strip()

                            attach_path = None
                            if file is not None:
                                safe_name = f"{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                                dest = UPLOAD_DIR / safe_name
                                dest.write_bytes(file.getbuffer())
                                attach_path = str(dest)

                            add_pm_log(open_for, pm_date, checklist, performed_by,
                                       notes.strip() if notes else None, attach_path)
                            st.success("Saved PM log with attachment.")
                            st.session_state["open_attach_for"] = None
                            st.rerun()
                        except Exception:
                            st.error("Invalid timestamp format. Use: YYYY-MM-DD HH:MM:SS")


# -----------------------------
# Tab: Stations Management
# -----------------------------
with tab_stations:
    sub_add, sub_edit = st.tabs(["➕ Add Station Pair", "✏️ Edit Station"])

    with sub_add:
        st.subheader("Add Station Pair (Duty + Standby)")
        with st.form("station_pair_form", clear_on_submit=True):
            station = st.text_input("Station name (unique)", placeholder="e.g., BCS-01")
            location = st.text_input("Location / Area", placeholder="e.g., BCS")
            duty_tag = st.text_input("Duty GC tag", value="GC-01")
            standby_tag = st.text_input("Standby GC tag", value="GC-02")
            pm_interval_days = st.number_input("PM interval (days)", min_value=1, value=90, step=1)
            submitted = st.form_submit_button("Add Station Pair")

            if submitted:
                try:
                    add_station_pair_add_only(station, location, duty_tag, standby_tag, int(pm_interval_days))
                    st.success("Added. Go to Dashboard to see it.")
                except Exception as e:
                    st.error(str(e))

    with sub_edit:
        st.subheader("Edit Station")
        df = fetch_kpis()
        if len(df) == 0:
            st.info("No stations yet.")
        else:
            stations = sorted(df["station"].unique().tolist())
            selected = st.selectbox("Select station to edit", stations)

            sg = df[df["station"] == selected].copy()
            location_current = sg["location"].iloc[0] if len(sg) else ""

            duty = sg[sg["role"] == "Duty"].head(1)
            standby = sg[sg["role"] == "Standby"].head(1)

            duty_tag_current = duty["tag"].iloc[0] if len(duty) else "GC-01"
            standby_tag_current = standby["tag"].iloc[0] if len(standby) else "GC-02"
            interval_current = int(sg["pm_interval_days"].iloc[0]) if len(sg) else 90

            with st.form("edit_station_form"):
                station_new = st.text_input("Station name", value=selected)
                location_new = st.text_input("Location / Area", value=location_current)
                col1, col2 = st.columns(2)
                with col1:
                    duty_tag_new = st.text_input("Duty tag", value=duty_tag_current)
                with col2:
                    standby_tag_new = st.text_input("Standby tag", value=standby_tag_current)
                pm_interval_new = st.number_input("PM interval (days)", min_value=1, value=interval_current, step=1)

                save = st.form_submit_button("Save Changes")
                if save:
                    try:
                        update_station_pair(
                            station_old=selected,
                            station_new=station_new,
                            location=location_new,
                            duty_tag=duty_tag_new,
                            standby_tag=standby_tag_new,
                            pm_interval_days=int(pm_interval_new)
                        )
                        st.success("Station updated successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# -----------------------------
# Tab: PM Logs & Attachments
# -----------------------------
with tab_pm:
    df = fetch_kpis()
    if len(df) == 0:
        st.info("Add station pairs first.")
    else:
        df["display"] = df.apply(lambda r: f"{r['station']} | {r['role']} | {r['tag']} (ID:{r['id']})", axis=1)
        pick = st.selectbox("Select GC", df["display"].tolist())
        row = df[df["display"] == pick].iloc[0]
        aid = int(row["id"])

        st.write(f"**Station:** {row['station']} | **Role:** {row['role']} | **Tag:** {row['tag']}")

        st.subheader("PM Logs (last 50) + Attachments")
        logs = get_pm_logs(aid)
        if len(logs) == 0:
            st.write("No PM logs yet.")
        else:
            logs_view = logs.copy()
            logs_view["checklist_complete"] = logs_view["checklist_complete"].map({0: "No", 1: "Yes"})
            st.dataframe(logs_view, use_container_width=True, hide_index=True)

            st.markdown("### Open attachments from logs")
            for i, rr in logs.iterrows():
                ap = rr.get("attachment_path")
                if ap and str(ap).strip():
                    with st.expander(f"📎 {rr['pm_date']} — {rr['performed_by']}"):
                        if rr.get("notes"):
                            st.write(rr["notes"])
                        show_attachment(str(ap), key_prefix=f"log_{aid}_{i}")

        st.subheader("Add PM (with optional attachment)")
        with st.form("pm_form"):
            performed_by = st.text_input("Who performed", value=st.session_state.get("quick_name", ""))
            pm_date = st.text_input("PM date (YYYY-MM-DD HH:MM:SS)", value=now_iso())
            checklist = st.checkbox("PM checklist completion", value=True)
            notes = st.text_area("Notes")
            file = st.file_uploader("Attachment", type=None, key="pm_file2")
            ok2 = st.form_submit_button("Save PM")

            if ok2:
                if not performed_by.strip():
                    st.error("Please enter who performed.")
                else:
                    try:
                        iso_to_dt(pm_date)
                        st.session_state["quick_name"] = performed_by.strip()

                        attach_path = None
                        if file is not None:
                            safe_name = f"{row['station']}_{row['role']}_{row['tag']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                            dest = UPLOAD_DIR / safe_name
                            dest.write_bytes(file.getbuffer())
                            attach_path = str(dest)

                        add_pm_log(aid, pm_date, checklist, performed_by,
                                   notes.strip() if notes else None, attach_path)
                        st.success("PM saved.")
                        st.rerun()
                    except Exception:
                        st.error("Invalid timestamp format. Use: YYYY-MM-DD HH:MM:SS")


# -----------------------------
# Tab: Work Orders & Compliance
# -----------------------------
with tab_wo:
    st.subheader("Work Orders Compliance (Weekly / Monthly)")

    # =========================
    # 📥 SAP Import (CSV / Excel)
    # =========================
    st.markdown("### 📥 Import Work Orders from SAP (CSV / Excel)")
    sap_file = st.file_uploader("Upload SAP export file", type=["csv", "xlsx"], key="sap_upload")

    def norm_col(s: str) -> str:
        return str(s).strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    def find_col(cols, candidates):
        cols_norm = {norm_col(c): c for c in cols}
        for cand in candidates:
            key = norm_col(cand)
            if key in cols_norm:
                return cols_norm[key]
        return None

    def upsert_work_orders_from_df(df_import: pd.DataFrame) -> int:
        cols = df_import.columns

        col_wo = find_col(cols, ["AUFNR", "order", "order number", "wo", "work order", "workorder", "ordernumber"])
        col_station = find_col(cols, ["TPLNR", "functional location", "functionallocation", "station", "equipment", "eqnr"])
        col_loc = find_col(cols, ["KTEXT", "short text", "shorttext", "description", "location text", "locationtext"])
        col_due = find_col(cols, ["GLTRP", "Latest Allowable End Date", "basic finish", "basicfinish", "due date", "duedate", "required end", "req.end"])
        col_pri = find_col(cols, ["PRIOK", "priority", "prio", "pri"])
        col_hours = find_col(cols, ["ARBEIT", "planned work", "plannedwork", "work", "est hours", "estimated hours", "esthours"])

        missing = []
        if not col_wo:
            missing.append("WO Number (AUFNR)")
        if not col_station:
            missing.append("Station / Functional Location (TPLNR)")
        if not col_due:
            missing.append("Due Date (GLTRP / Basic finish)")
        if missing:
            raise ValueError("Missing required columns in SAP export: " + ", ".join(missing))

        df = df_import.copy()
        df["wo_number"] = df[col_wo].astype(str).str.strip()
        df["station"] = df[col_station].astype(str).str.strip()
        df["location"] = df[col_loc].astype(str).str.strip() if col_loc else None
        df["due_date"] = pd.to_datetime(df[col_due], errors="coerce").dt.strftime("%Y-%m-%d")

        df["priority"] = pd.to_numeric(df[col_pri], errors="coerce").fillna(99).astype(int) if col_pri else 99
        df["est_hours"] = pd.to_numeric(df[col_hours], errors="coerce").fillna(1.0).astype(float) if col_hours else 1.0

        df["task_type"] = "PM"
        df["status"] = "Planned"

        df = df[df["wo_number"].str.len() > 0]
        df = df[df["station"].str.len() > 0]
        df = df[df["due_date"].notna()]

        ensure_work_orders_table()
        conn = get_conn()
        cur = conn.cursor()

        sql = """
        INSERT INTO work_orders
          (wo_number, station, location, task_type, priority, est_hours, due_date, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(wo_number) DO UPDATE SET
          station=excluded.station,
          location=excluded.location,
          task_type=excluded.task_type,
          priority=excluded.priority,
          est_hours=excluded.est_hours,
          due_date=excluded.due_date,
          updated_at=datetime('now');
        """

        count = 0
        for _, r in df.iterrows():
            cur.execute(
                sql,
                (
                    r["wo_number"],
                    r["station"],
                    r["location"],
                    r["task_type"],
                    int(r["priority"]),
                    float(r["est_hours"]),
                    r["due_date"],
                    r["status"],
                ),
            )
            count += 1

        conn.commit()
        conn.close()
        return count

    if sap_file is not None:
        try:
            df_imp = pd.read_csv(sap_file) if sap_file.name.lower().endswith(".csv") else pd.read_excel(sap_file)
            st.write("Preview (first 20 rows):")
            st.dataframe(df_imp.head(20), use_container_width=True)

            if st.button("✅ Import / Update from SAP file", key="btn_import_sap"):
                n = upsert_work_orders_from_df(df_imp)
                st.success(f"Imported/Updated {n} work orders.")
                st.rerun()

        except Exception as e:
            st.error(str(e))

    st.divider()

    # =========================
    # Compliance (Weekly/Monthly)
    # =========================
    df = fetch_work_orders()

    st.markdown('<div class="control-bar">', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Mode", ["Weekly", "Monthly"], horizontal=True, label_visibility="collapsed", key="wo_mode")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Pick date inside period</div>', unsafe_allow_html=True)
    anchor = st.date_input("Pick date", value=date.today(), label_visibility="collapsed", key="wo_anchor")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Filter</div>', unsafe_allow_html=True)
    pm_only = st.checkbox("PM work orders only", value=True, key="wo_pm_only")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    start, end = period_range_ymd(mode, anchor)
    st.caption(f"Period: {start} → {end}")

    if len(df) == 0:
        st.info("No work orders yet. Import from SAP above or add manually below.")
    else:
        view = df.copy()

        if pm_only and "task_type" in view.columns:
            view = view[view["task_type"].fillna("").str.lower().str.contains("pm")]

        view["due_dt"] = view["due_date"].apply(parse_date_ymd)
        view["comp_dt"] = view["completed_date"].apply(parse_date_ymd)

        def in_period(d: Optional[date]) -> bool:
            return bool(d and start <= d <= end)

        planned = int(view["due_dt"].apply(in_period).sum())
        done = int(view.apply(lambda r: r.get("status") == "Done" and in_period(r["comp_dt"]), axis=1).sum())
        on_time = int(
            view.apply(
                lambda r: (r.get("status") == "Done")
                          and in_period(r["comp_dt"])
                          and (r["due_dt"] is not None)
                          and (r["comp_dt"] is not None)
                          and (r["comp_dt"] <= r["due_dt"]),
                axis=1,
            ).sum()
        )
        overdue = int(
            view.apply(
                lambda r: (r.get("status") not in ["Done", "Cancelled"])
                          and (r["due_dt"] is not None)
                          and (r["due_dt"] < date.today()),
                axis=1,
            ).sum()
        )
        compliance = int(round((on_time / planned) * 100, 0)) if planned > 0 else 0

        st.markdown(
            f"""
            <div class="kpi-row">
              <div class="kpi-card"><div class="kpi-title">Planned</div><div class="kpi-value">{planned}</div><div class="kpi-sub">Due in period</div></div>
              <div class="kpi-card"><div class="kpi-title">Done</div><div class="kpi-value">{done}</div><div class="kpi-sub">Completed in period</div></div>
              <div class="kpi-card"><div class="kpi-title">Overdue</div><div class="kpi-value">{overdue}</div><div class="kpi-sub">Past due date</div></div>
              <div class="kpi-card"><div class="kpi-title">Compliance</div><div class="kpi-value">{compliance}%</div><div class="kpi-sub">On-time / Planned</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ---- Plan map (PRIVATE plan from wo_plans) for this period ----
        ensure_planning_tables()
        plans = fetch_plans_in_period(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        plan_map = {int(r["wo_id"]): r for _, r in plans.iterrows()}

        # =========================
        # Modern weekly board (DUE date)
        # =========================
        if mode == "Weekly":
            st.subheader("Weekly Plan Layout (Based on DUE Date)")
            week_days = [start + timedelta(days=i) for i in range(7)]
            cols = st.columns(7)

            for i in range(7):
                d = week_days[i]
                day_df = view[view["due_dt"] == d].copy()

                # sort: status rank then station then priority
                if len(day_df):
                    def _rank_status(stt: str) -> int:
                        if stt == "Planned":
                            return 1
                        if stt == "In Progress":
                            return 2
                        if stt == "Done":
                            return 4
                        return 3

                    day_df["rank"] = day_df["status"].astype(str).apply(_rank_status)
                    day_df = day_df.sort_values(["rank", "priority", "station", "wo_number"], ascending=[True, True, True, True])

                with cols[i]:
                    st.markdown(
                        f'<div class="day-col-title">{DAYS7[i]}<span class="day-chip">({d.strftime("%d %b")})</span></div>',
                        unsafe_allow_html=True
                    )

                    if len(day_df) == 0:
                        st.caption("— no items —")
                        continue

                    for _, r in day_df.iterrows():
                        stt = str(r.get("status") or "Planned")
                        if stt == "Done":
                            badge = '<span class="badge badge-done">Done</span>'
                        elif stt == "In Progress":
                            badge = '<span class="badge badge-prog">In Progress</span>'
                        elif stt == "Planned":
                            badge = '<span class="badge badge-plan">Planned</span>'
                        else:
                            badge = f'<span class="badge">{stt}</span>'

                        over_badge = ""
                        if r.get("status") not in ["Done", "Cancelled"] and r.get("due_dt") and r["due_dt"] < date.today():
                            over_badge = ' <span class="badge badge-over">Overdue</span>'

                        p = plan_map.get(int(r["id"]))
                        if p is not None:
                            who = f"{p['tech_1']}" + (f" + {p['tech_2']}" if p.get("tech_2") else "")
                            mode_badge = ' <span class="badge badge-auto">Auto</span>' if str(p.get("mode")) == "Auto" else ""
                            plan_line = f"<br/>Planned: <b>{who}</b>{mode_badge}"
                        else:
                            plan_line = "<br/>Planned: <span class='badge'>Not planned</span>"

                        st.markdown(
                            f"""
                            <div class="card">
                              <div class="card-title">
                                WO {safe_str(r.get('wo_number'), '')} {badge}{over_badge}
                              </div>
                              <div class="card-sub">
                                <b>{safe_str(r.get('station'))}</b> • {safe_str(r.get('location'))}<br/>
                                Type: {safe_str(r.get('task_type'))} • P{safe_str(r.get('priority'))} • {safe_str(r.get('est_hours'))}h
                                {plan_line}
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.caption("This board is based on **SAP Due Date**. Your private manpower plan shows under each card.")

        else:
            st.subheader("Monthly List")
            tmp = view[view["due_dt"].apply(in_period)].copy()
            tmp = tmp.sort_values(["due_dt", "status", "priority", "station", "wo_number"], ascending=[True, True, True, True, True])
            show_cols = [
                "wo_number", "station", "location", "task_type", "priority", "est_hours", "status",
                "assigned_to", "planned_date", "due_date", "completed_date", "notes"
            ]
            st.dataframe(tmp[[c for c in show_cols if c in tmp.columns]], use_container_width=True, hide_index=True)

    st.divider()

    # =========================
    # Add New Work Order
    # =========================
    st.subheader("Add New Work Order")
    with st.form("add_wo_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        wo_number = c1.text_input("WO Number", placeholder="e.g., 4500xxxxx")
        station = c2.text_input("Station", placeholder="e.g., BCS-01")
        location = c3.text_input("Location", placeholder="optional")

        c4, c5, c6 = st.columns(3)
        task_type = c4.text_input("Task Type", value="PM", placeholder="PM / Calibration / F&G")
        status = c5.selectbox("Status", ["Planned", "In Progress", "Done", "Cancelled"])
        assigned_to = c6.text_input("Assigned To (optional)", placeholder="(SAP field)")

        c7, c8, c9 = st.columns(3)
        priority = c7.number_input("Priority (1 = highest)", min_value=1, max_value=99, value=3, step=1)
        est_hours = c8.number_input("Estimated Hours", min_value=0.25, max_value=200.0, value=1.0, step=0.25)
        planned_date = c9.date_input("Planned Date (optional)", value=date.today())

        c10, c11 = st.columns(2)
        due_date = c10.date_input("Due Date", value=date.today())
        completed_date = c11.text_input("Completed Date (YYYY-MM-DD)", value="" if status != "Done" else date.today().strftime("%Y-%m-%d"))

        notes = st.text_area("Notes", placeholder="Details / WO notes")
        save = st.form_submit_button("Save WO")

        if save:
            if not wo_number.strip() or not station.strip():
                st.error("WO Number and Station are required.")
                st.stop()

            if completed_date.strip():
                try:
                    _ = parse_date_ymd(completed_date.strip())
                except Exception:
                    st.error("Completed Date must be YYYY-MM-DD")
                    st.stop()

            try:
                new_id = insert_work_order(
                    {
                        "wo_number": wo_number.strip(),
                        "station": station.strip(),
                        "location": location.strip() if location.strip() else None,
                        "task_type": task_type.strip() if task_type.strip() else "PM",
                        "priority": int(priority),
                        "est_hours": float(est_hours),
                        "planned_date": planned_date.strftime("%Y-%m-%d") if planned_date else None,
                        "due_date": due_date.strftime("%Y-%m-%d") if due_date else None,
                        "status": status,
                        "assigned_to": assigned_to.strip() if assigned_to.strip() else None,
                        "completed_date": completed_date.strip() if completed_date.strip() else None,
                        "notes": notes.strip() if notes else None,
                    }
                )
                st.success(f"Saved WO (ID: {new_id})")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    st.divider()

    # =========================
    # Edit Work Order
    # =========================
    st.subheader("Edit Work Order")
    df2 = fetch_work_orders()
    if len(df2) == 0:
        st.info("No work orders to edit.")
    else:
        df2 = df2.copy()
        df2["display"] = df2.apply(
            lambda r: f"ID:{r['id']} | WO:{r['wo_number']} | {r['station']} | {r['task_type']} | P{r.get('priority',99)} | {r['status']}",
            axis=1
        )
        pick = st.selectbox("Pick WO", df2["display"].tolist(), key="edit_wo_pick")
        row = df2[df2["display"] == pick].iloc[0]
        wo_id = int(row["id"])

        with st.form("edit_wo_form"):
            c1, c2, c3 = st.columns(3)
            wo_number = c1.text_input("WO Number", value=str(row.get("wo_number") or ""))
            station = c2.text_input("Station", value=str(row.get("station") or ""))
            location = c3.text_input("Location", value=str(row.get("location") or ""))

            c4, c5, c6 = st.columns(3)
            task_type = c4.text_input("Task Type", value=str(row.get("task_type") or "PM"))
            priority = c5.number_input("Priority (1 = highest)", min_value=1, max_value=99, value=int(row.get("priority") or 99), step=1)
            est_hours = c6.number_input("Estimated Hours", min_value=0.25, max_value=200.0, value=float(row.get("est_hours") or 1.0), step=0.25)

            c7, c8, c9 = st.columns(3)
            status_list = ["Planned", "In Progress", "Done", "Cancelled"]
            current_status = str(row.get("status") or "Planned")
            status_idx = status_list.index(current_status) if current_status in status_list else 0
            status = c7.selectbox("Status", status_list, index=status_idx)
            assigned_to = c8.text_input("Assigned To (optional)", value=str(row.get("assigned_to") or ""))
            planned_date = c9.text_input("Planned Date (YYYY-MM-DD)", value=str(row.get("planned_date") or ""))

            c10, c11 = st.columns(2)
            due_date = c10.text_input("Due Date (YYYY-MM-DD)", value=str(row.get("due_date") or ""))
            completed_date = c11.text_input("Completed Date (YYYY-MM-DD)", value=str(row.get("completed_date") or ""))

            notes = st.text_area("Notes", value=str(row.get("notes") or ""))

            save = st.form_submit_button("Save Changes")
            if save:
                try:
                    if planned_date.strip():
                        _ = parse_date_ymd(planned_date.strip())
                    if due_date.strip():
                        _ = parse_date_ymd(due_date.strip())
                    if completed_date.strip():
                        _ = parse_date_ymd(completed_date.strip())
                except Exception:
                    st.error("Date must be YYYY-MM-DD")
                    st.stop()

                update_work_order(
                    wo_id,
                    {
                        "wo_number": wo_number.strip(),
                        "station": station.strip(),
                        "location": location.strip() if location.strip() else None,
                        "task_type": task_type.strip() if task_type.strip() else "PM",
                        "priority": int(priority),
                        "est_hours": float(est_hours),
                        "planned_date": planned_date.strip() if planned_date.strip() else None,
                        "due_date": due_date.strip() if due_date.strip() else None,
                        "status": status,
                        "assigned_to": assigned_to.strip() if assigned_to.strip() else None,
                        "completed_date": completed_date.strip() if completed_date.strip() else None,
                        "notes": notes.strip() if notes.strip() else None,
                    },
                )
                st.success("Updated.")
                st.rerun()


# -----------------------------
# Tab: Weekly Planner (Private Plan in wo_plans)
# -----------------------------
with tab_weekly:
    ensure_planning_tables()
    st.subheader("Weekly Planner (Private) — Manual + Auto (1–2 Tech per WO)")

    # ---- Tech master list ----
    st.markdown("### Technicians (Instrument)")
    techs = fetch_technicians("Instrument")

    cA, cB = st.columns([1.2, 1])
    with cA:
        with st.form("add_tech_form", clear_on_submit=True):
            new_name = st.text_input("Add technician name")
            add_btn = st.form_submit_button("Add")
            if add_btn:
                try:
                    add_technician(new_name, "Instrument")
                    st.success("Added.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with cB:
        st.caption(f"Active: {', '.join(techs) if techs else 'None'}")

    st.divider()

    df = fetch_work_orders()
    if len(df) == 0:
        st.info("No work orders available.")
        st.stop()

    # Exclude closed WOs
    df_open = df[~df["status"].isin(["Done", "Cancelled"])].copy()

    pm_only = st.checkbox("PM only", value=True, key="planner_pm_only")
    if pm_only:
        df_open = df_open[df_open["task_type"].fillna("").str.lower().str.contains("pm")]

    anchor = st.date_input("Pick a date inside the week", value=date.today(), key="planner_anchor")
    ws = week_start_sunday(anchor)
    we = ws + timedelta(days=6)
    st.caption(f"Week: {ws} → {we} (Work days: Sun–Thu)")

    # ---- Auto plan controls ----
    st.markdown("### ⚡ Auto Plan (Balanced across Sun–Thu)")
    max_per_day = st.number_input("Max tasks per technician per day", min_value=1, value=2, step=1)
    two_tech_default = st.checkbox("Auto assign 2 technicians per WO", value=False)

    # pick WOs for this week based on DUE date inside week
    df_open["due_dt"] = df_open["due_date"].apply(parse_date_ymd)
    wos_this_week = df_open[df_open["due_dt"].apply(lambda d: bool(d and ws <= d <= we))].copy()

    if st.button("Auto Plan This Week", key="btn_auto_plan_week"):
        if not techs:
            st.error("Add technicians first.")
        elif len(wos_this_week) == 0:
            st.warning("No open work orders with DUE dates inside this week.")
        else:
            auto_assign_week(
                work_orders_df=wos_this_week,
                techs=techs,
                start=ws,
                end=we,
                max_per_tech_per_day=int(max_per_day),
                two_tech_default=two_tech_default,
            )
            st.success("Auto plan saved to wo_plans.")
            st.rerun()

    st.divider()

    # ---- Manual plan per WO ----
    st.markdown("### ✍️ Manual Plan (Select WO → choose day + 1–2 tech)")
    df_open["display"] = df_open.apply(
        lambda r: f"ID:{r['id']} | WO:{r['wo_number']} | {r['station']} | P{r.get('priority',99)} | Due:{r.get('due_date','-')} | {r['status']}",
        axis=1
    )
    pick = st.selectbox("Select WO", df_open["display"].tolist(), key="manual_wo_pick")
    row = df_open[df_open["display"] == pick].iloc[0]
    wo_id = int(row["id"])

    with st.form("manual_plan_form"):
        plan_date = st.date_input("Plan execution date", value=ws, key="manual_plan_date")
        if not techs:
            st.warning("Add technicians above first.")
            tech_1 = ""
            tech_2_opt = "(None)"
        else:
            tech_1 = st.selectbox("Technician 1", techs, key="m_tech1")
            tech_2_opt = st.selectbox("Technician 2 (optional)", ["(None)"] + techs, key="m_tech2")
        notes = st.text_area("Planning notes (optional)")
        save = st.form_submit_button("Save Plan")

        if save:
            if not techs:
                st.error("No technicians. Add technicians first.")
            else:
                t2 = None if tech_2_opt == "(None)" else tech_2_opt
                if t2 == tech_1:
                    st.error("Technician 2 cannot be the same as Technician 1.")
                else:
                    upsert_plan(
                        wo_id=wo_id,
                        plan_date=plan_date.strftime("%Y-%m-%d"),
                        mode="Manual",
                        tech_1=tech_1,
                        tech_2=t2,
                        notes=notes.strip() if notes else None,
                    )
                    st.success("Plan saved.")
                    st.rerun()

    if st.button("🗑 Remove plan for selected WO", key="btn_remove_plan"):
        delete_plan(wo_id)
        st.success("Plan removed.")
        st.rerun()

    st.divider()

    # ---- Show private plan board (Sun–Thu) ----
    st.markdown("### 📅 Private Plan Board (Sun–Thu)")
    plans = fetch_plans_in_period(ws.strftime("%Y-%m-%d"), we.strftime("%Y-%m-%d"))
    if len(plans) == 0:
        st.info("No planned items yet for this week.")
    else:
        # show board by plan_date
        work_days = [ws + timedelta(days=i) for i in range(5)]  # Sun..Thu
        cols = st.columns(5)
        for i in range(5):
            d = work_days[i]
            ds = d.strftime("%Y-%m-%d")
            dayp = plans[plans["plan_date"] == ds].copy()
            dayp = dayp.sort_values(["station", "wo_number"])

            with cols[i]:
                st.markdown(
                    f'<div class="day-col-title">{DAYS7[i]}<span class="day-chip">({d.strftime("%d %b")})</span></div>',
                    unsafe_allow_html=True
                )
                if len(dayp) == 0:
                    st.caption("— no planned —")
                else:
                    for _, r in dayp.iterrows():
                        who = f"{r['tech_1']}" + (f" + {r['tech_2']}" if pd.notna(r.get("tech_2")) and str(r.get("tech_2")).strip() else "")
                        mode_badge = '<span class="badge badge-auto">Auto</span>' if str(r.get("mode")) == "Auto" else '<span class="badge badge-plan">Manual</span>'
                        st.markdown(
                            f"""
                            <div class="card">
                              <div class="card-title">
                                WO {safe_str(r.get('wo_number'))} {mode_badge}
                              </div>
                              <div class="card-sub">
                                <b>{safe_str(r.get('station'))}</b> • {safe_str(r.get('location'))}<br/>
                                {safe_str(r.get('task_type'))} • Due: {safe_str(r.get('due_date'))}<br/>
                                Tech: <b>{who}</b>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        st.caption("This plan is stored in wo_plans and does NOT change SAP due dates.")
with tab_today:
    st.subheader("Today & Tomorrow Tasks (Execution Plan)")

    # Work days in Oman: Sun–Thu
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # If tomorrow is Fri/Sat, you can still show it, but here we keep it simple:
    st.caption(f"Today: {today} | Tomorrow: {tomorrow}")

    techs = fetch_technicians("Instrument")
    if not techs:
        st.warning("No technicians in master list. Add them first (Technicians table).")
        st.stop()

    # Load planned tasks from wo_plans + details from work_orders
    conn = get_conn()
    plans = pd.read_sql_query("""
        SELECT
            p.wo_id, p.plan_date, p.mode, p.tech_1, p.tech_2, p.notes as plan_notes,
            w.wo_number, w.station, w.location, w.task_type, w.priority, w.est_hours,
            w.due_date, w.status, w.assigned_to, w.completed_date
        FROM wo_plans p
        JOIN work_orders w ON w.id = p.wo_id
        WHERE p.plan_date IN (?, ?)
        ORDER BY p.plan_date ASC,
                 CASE w.status WHEN 'Planned' THEN 1 WHEN 'In Progress' THEN 2 WHEN 'Done' THEN 3 ELSE 9 END,
                 w.priority ASC,
                 w.due_date ASC
    """, conn, params=(today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")))
    conn.close()

    if plans.empty:
        st.info("No planned work orders for Today/Tomorrow yet. Create plans in Weekly Planner / Manual planning.")
        st.stop()

    # Filter view
    top = st.columns([1.2, 1, 1])
    view_day = top[0].radio("View", ["Today", "Tomorrow", "Both"], horizontal=True)
    status_filter = top[1].multiselect("Status", ["Planned", "In Progress", "Done", "Cancelled"], default=["Planned", "In Progress"])
    tech_filter = top[2].multiselect("Technicians", techs, default=techs)

    v = plans.copy()
    if view_day != "Both":
        target = today if view_day == "Today" else tomorrow
        v = v[v["plan_date"] == target.strftime("%Y-%m-%d")]

    if status_filter:
        v = v[v["status"].isin(status_filter)]

    # Keep only WOs where tech_1 or tech_2 is in selected list
    v = v[
        v["tech_1"].isin(tech_filter) |
        v["tech_2"].fillna("").isin(tech_filter)
    ]

    if v.empty:
        st.info("No items after filters.")
        st.stop()

    # Group by day then technician
    for day_s, day_df in v.groupby("plan_date"):
        day_dt = parse_date_ymd(day_s)
        st.markdown(f"### 🗓 {day_s} ({day_dt.strftime('%a') if day_dt else ''})")

        # build "tech -> rows" (if WO has two techs, show under both)
        tech_map = {t: [] for t in tech_filter}
        for _, r in day_df.iterrows():
            t1 = str(r["tech_1"]).strip() if r.get("tech_1") else ""
            t2 = str(r["tech_2"]).strip() if r.get("tech_2") else ""
            if t1 in tech_map:
                tech_map[t1].append(r)
            if t2 in tech_map and t2 != t1:
                tech_map[t2].append(r)

        for tech, items in tech_map.items():
            if not items:
                continue

            with st.expander(f"👷 {tech} — {len(items)} task(s)", expanded=True):
                for r in items:
                    wo_id = int(r["wo_id"])
                    wo_num = safe_str(r.get("wo_number"))
                    station = safe_str(r.get("station"))
                    loc = safe_str(r.get("location"))
                    task_type = safe_str(r.get("task_type"))
                    status = safe_str(r.get("status"))
                    due = safe_str(r.get("due_date"))
                    pr = safe_str(r.get("priority"))
                    hrs = safe_str(r.get("est_hours"))

                    # Status badge
                    if status == "Done":
                        badge = '<span class="badge badge-done">Done</span>'
                    elif status == "In Progress":
                        badge = '<span class="badge badge-prog">In Progress</span>'
                    elif status == "Planned":
                        badge = '<span class="badge badge-plan">Planned</span>'
                    else:
                        badge = f'<span class="badge">{status}</span>'

                    st.markdown(
                        f"""
                        <div class="card">
                          <div class="card-title">
                            WO {wo_num} {badge}
                          </div>
                          <div class="card-sub">
                            <b>{station}</b> • {loc}<br/>
                            Type: {task_type} • Priority: {pr} • Est: {hrs}h<br/>
                            SAP Due: {due}
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # ===== Action form (update + checklist + attachment) =====
                    with st.form(f"wo_update_form_{wo_id}_{tech}_{day_s}"):
                        cols = st.columns([1.2, 1, 1])
                        new_status = cols[0].selectbox(
                            "Update Status",
                            ["Planned", "In Progress", "Done", "Cancelled"],
                            index=["Planned", "In Progress", "Done", "Cancelled"].index(status) if status in ["Planned", "In Progress", "Done", "Cancelled"] else 0,
                        )
                        performed_by = cols[1].text_input("Performed by", value=tech)
                        checklist_ok = cols[2].checkbox("Checklist complete", value=False)

                        note = st.text_area("Notes (finding / parts / SAP comment)", height=80)
                        file = st.file_uploader("Attachment (photo / PDF / report)", key=f"wo_file_{wo_id}_{tech}_{day_s}")

                        save_btn = st.form_submit_button("✅ Save Update")

                        if save_btn:
                            if not performed_by.strip():
                                st.error("Performed by is required.")
                                st.stop()

                            attach_path = None
                            if file is not None:
                                safe_name = f"WO_{wo_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                                dest = UPLOAD_DIR / safe_name
                                dest.write_bytes(file.getbuffer())
                                attach_path = str(dest)

                            # Update status + completed date if Done
                            comp_date = None
                            if new_status == "Done":
                                comp_date = date.today().strftime("%Y-%m-%d")

                            set_wo_status(wo_id, new_status, comp_date)

                            # Log evidence/history
                            action = "Done" if new_status == "Done" else "Update"
                            add_wo_update(
                                wo_id=wo_id,
                                action=action,
                                performed_by=performed_by.strip(),
                                checklist_complete=bool(checklist_ok),
                                notes=note.strip() if note else None,
                                attachment_path=attach_path,
                            )

                            st.success("Saved.")
                            st.rerun()

                    # ===== History (last 50) =====
                    hist = get_wo_updates(wo_id)
                    if len(hist):
                        with st.expander("📜 Updates History / Evidence"):
                            hv = hist.copy()
                            hv["checklist_complete"] = hv["checklist_complete"].map({0: "No", 1: "Yes"})
                            st.dataframe(hv[["update_ts", "action", "performed_by", "checklist_complete", "notes", "attachment_path"]],
                                         use_container_width=True, hide_index=True)

                            # show attachments
                            for i, rr in hist.iterrows():
                                ap = rr.get("attachment_path")
                                if ap and str(ap).strip():
                                    with st.expander(f"📎 {rr['update_ts']} — {rr['performed_by']}"):
                                        if rr.get("notes"):
                                            st.write(rr["notes"])
                                        show_attachment(str(ap), key_prefix=f"wohist_{wo_id}_{i}")
