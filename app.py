<<<<<<< HEAD
# app.py (NO-JS + NO-CHARTS: modern + responsive + stable)
# ✅ PM-only dashboard
# ✅ Same tags can repeat across stations (GC-01/GC-02 per station)
# ✅ Dashboard view modes: List | Big cards | Medium cards | Small cards
# ✅ Click station => Full details panel
# ✅ Add Station Pair (add-only)
# ✅ Edit Station tab
# ✅ Attachments upload + view/download
# ✅ Mobile friendly CSS
# ✅ NO JavaScript
# ✅ NO Charts

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes

from db import init_db, get_conn

st.set_page_config(page_title="GC Analyzer PM Dashboard", layout="wide")
init_db()

# ---- Mobile-friendly + responsive UI tweaks ----
st.markdown("""
<style>
/* Overall spacing */
div[data-testid="stVerticalBlock"] { gap: 0.65rem; }
section.main > div { padding-top: 1rem; padding-bottom: 1rem; }

/* Buttons */
button[kind="secondary"], button[kind="primary"] { padding: 0.35rem 0.6rem; }

/* Mobile adjustments */
@media (max-width: 700px) {
  html, body, [class*="css"] { font-size: 14px !important; }
  div[data-testid="column"] {
    width: 100% !important;
    flex: 1 1 100% !important;
    max-width: 100% !important;
  }
  div[data-testid="stDataFrame"] { overflow-x: auto; }
  h1 { font-size: 1.4rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.05rem !important; }
}

/* KPI cards */
=======
# app.py — Instrumentation Tasks Dashboard (Clean + Fixed)
# Streamlit + SQLite (via db.py: init_db(), get_conn())

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path
import mimetypes
from typing import Optional, Tuple

from db import init_db, get_conn

# -----------------------------
# App config + DB init
# -----------------------------
st.set_page_config(page_title="Instrumentation Tasks Dashboard", layout="wide")
init_db()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# Login (Secrets) - Modern Responsive (no JS)
# -----------------------------
# ✅ Replace ONLY your require_login_clean() with this fixed version
# (This puts the Streamlit form INSIDE the glass card, no extra form above/below)

# ✅ Replace ONLY your require_login_clean() with this version
# - Glass card becomes the BORDER/WRAPPER around the form
# - Form is perfectly centered in the page
# - Inputs are smaller + tighter spacing
# ✅ Replace ONLY your require_login_clean() with this SIMPLE clean one
# - No extra/empty cards
# - No glass wrapper at all
# - Responsive login form
# - Positioned at "middle-top" (not center of page)
# - Inputs look normal (not thin line)

# ✅ Replace ONLY your require_login_clean() with this updated responsive version
# - Responsive card width + padding
# - Password field EXACT same size/style as username
# - No separation (everything inside same card/container)
def require_login_clean():
    if st.session_state.get("logged_in"):
        return

    app_user = st.secrets.get("APP_USER", "sohar")
    app_pass = st.secrets.get("APP_PASS", "1234")

    # Basic clean styling
    st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .login-container {
        max-width: 400px;
        margin: auto;
        padding-top: 8vh;
    }

    .login-title {
        text-align: center;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center container
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">Login to Dashboard</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

        st.markdown('</div>', unsafe_allow_html=True)

        if login_btn:
            if username == app_user and password == app_pass:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid username or password")

    st.stop()








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

>>>>>>> 10e4590 (synce with changes in codes)
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

<<<<<<< HEAD
/* Control bar */
=======
>>>>>>> 10e4590 (synce with changes in codes)
.control-bar{
  display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; justify-content:space-between;
  margin: 0.2rem 0 0.6rem 0;
}
.control-box{
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 10px 12px;
  flex: 1 1 360px;
}
.small-label{ font-size: 0.78rem; opacity: .7; margin-bottom: 6px; }
</style>
<<<<<<< HEAD
""", unsafe_allow_html=True)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
=======
""",
    unsafe_allow_html=True,
)
>>>>>>> 10e4590 (synce with changes in codes)

# -----------------------------
# Helpers
# -----------------------------
<<<<<<< HEAD
def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def iso_to_dt(s: str):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def days_to_due(last_pm: str | None, interval_days: int) -> int | None:
    if not last_pm:
        return None
    due_dt = iso_to_dt(last_pm) + timedelta(days=interval_days)
    return (due_dt.date() - datetime.now().date()).days

def due_bucket(days_left: int | None) -> str:
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

def show_attachment(path_str: str | None, key_prefix: str):
    if not path_str or not str(path_str).strip():
        st.info("No attachment.")
        return

    p = Path(str(path_str))
=======
def safe_str(x, default: str = "-") -> str:
    if x is None:
        return default
    if isinstance(x, float) and pd.isna(x):
        return default
    if isinstance(x, str) and not x.strip():
        return default
    return str(x)

def is_pm_task(r) -> bool:
    tt = safe_str(r.get("task_type"), "").strip().lower()
    return "pm" in tt

def date_leq(a: Optional[date], b: Optional[date]) -> bool:
    if not a or not b:
        return False
    return a <= b

def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_date(s: Optional[str]) -> Optional[date]:
    if not s or not str(s).strip():
        return None
    return datetime.strptime(str(s), "%Y-%m-%d").date()

def show_attachment(path_str: str, key_prefix: str):
    p = Path(path_str)
>>>>>>> 10e4590 (synce with changes in codes)
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
<<<<<<< HEAD
        key=f"dl_{key_prefix}_{p.name}_{p.stat().st_mtime_ns}"
    )

def evidence_icon(attachment_path: str | None) -> str:
    if attachment_path is not None and pd.notna(attachment_path) and str(attachment_path).strip():
        return "📎"
    return "⚪"

def safe_str(x, default="-"):
    if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and not x.strip()):
        return default
    return str(x)

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
# DB functions
# -----------------------------
def fetch_kpis() -> pd.DataFrame:
    conn = get_conn()

    analyzers = pd.read_sql_query("""
        SELECT id, tag, location, station, role, pm_interval_days
        FROM analyzers
        ORDER BY station, role, id
    """, conn)

    last_pm_row = pd.read_sql_query("""
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
    """, conn)

    conn.close()

    df = analyzers.merge(last_pm_row, left_on="id", right_on="analyzer_id", how="left").drop(columns=["analyzer_id"])
    df["station"] = df["station"].fillna(df["location"])

    def _calc_days(r):
        pm_date = r.get("pm_date")
        last = None if (pm_date is None or pd.isna(pm_date)) else pm_date
        return days_to_due(last, int(r["pm_interval_days"]))
    df["pm_days_left"] = df.apply(_calc_days, axis=1)
    df["pm_bucket"] = df["pm_days_left"].apply(due_bucket)

    def _next_due(r):
        pm_date = r.get("pm_date")
        if pm_date is None or pd.isna(pm_date):
            return None
        due_dt = iso_to_dt(pm_date) + timedelta(days=int(r["pm_interval_days"]))
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
        conn, params=(station,)
    )
    if len(existing_station) > 0:
        conn.close()
        raise ValueError(
            f"Station '{station}' already exists.\n"
            "Use a different Station name OR use Edit Station tab."
        )

    existing_tags_same_station = pd.read_sql_query(
        "SELECT tag, role FROM analyzers WHERE station=? AND tag IN (?, ?)",
        conn, params=(station, duty_tag, standby_tag)
    )
    if len(existing_tags_same_station) > 0:
        conn.close()
        msg = "\n".join([f"- {r['tag']} already exists in this station (Role: {r['role']})"
                         for _, r in existing_tags_same_station.iterrows()])
        raise ValueError("These GC tags already exist in this station:\n" + msg)

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analyzers(tag, location, station, role, pm_interval_days)
        VALUES(?, ?, ?, 'Duty', ?)
    """, (duty_tag, location, station, int(pm_interval_days)))

    cur.execute("""
        INSERT INTO analyzers(tag, location, station, role, pm_interval_days)
        VALUES(?, ?, ?, 'Standby', ?)
    """, (standby_tag, location, station, int(pm_interval_days)))

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
        conn, params=(station_old,)
    )
    if len(existing) == 0:
        conn.close()
        raise ValueError("Selected station not found.")

    if station_new != station_old:
        check_new = pd.read_sql_query(
            "SELECT 1 FROM analyzers WHERE station=? LIMIT 1",
            conn, params=(station_new,)
        )
        if len(check_new) > 0:
            conn.close()
            raise ValueError(f"Station name '{station_new}' already exists.")

    duty_row = pd.read_sql_query(
        "SELECT id FROM analyzers WHERE station=? AND role='Duty' LIMIT 1",
        conn, params=(station_old,)
    )
    standby_row = pd.read_sql_query(
        "SELECT id FROM analyzers WHERE station=? AND role='Standby' LIMIT 1",
        conn, params=(station_old,)
    )
    if len(duty_row) == 0 or len(standby_row) == 0:
        conn.close()
        raise ValueError("This station must have both Duty and Standby.")

    duty_id = int(duty_row.iloc[0]["id"])
    standby_id = int(standby_row.iloc[0]["id"])

    dup = pd.read_sql_query("""
        SELECT id, role, tag
        FROM analyzers
        WHERE station=? AND tag IN (?, ?)
          AND id NOT IN (?, ?)
    """, conn, params=(station_new, duty_tag, standby_tag, duty_id, standby_id))
    if len(dup) > 0:
        conn.close()
        raise ValueError("Duplicate tag inside this station (station, tag must be unique).")

    cur = conn.cursor()
    cur.execute("BEGIN")
    cur.execute("""
        UPDATE analyzers
        SET station=?, location=?, tag=?, pm_interval_days=?
        WHERE id=?
    """, (station_new, location, duty_tag, int(pm_interval_days), duty_id))

    cur.execute("""
        UPDATE analyzers
        SET station=?, location=?, tag=?, pm_interval_days=?
        WHERE id=?
    """, (station_new, location, standby_tag, int(pm_interval_days), standby_id))

    conn.commit()
    conn.close()

def add_pm_log(analyzer_id: int, pm_date: str, checklist_complete: bool, performed_by: str,
               notes: str | None, attachment_path: str | None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pm_logs(analyzer_id, pm_date, checklist_complete, performed_by, notes, attachment_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (analyzer_id, pm_date, 1 if checklist_complete else 0, performed_by.strip(), notes, attachment_path))
    conn.commit()
    conn.close()

def get_pm_logs(analyzer_id: int):
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT pm_date, checklist_complete, performed_by, notes, attachment_path
        FROM pm_logs
        WHERE analyzer_id=?
        ORDER BY pm_date DESC
        LIMIT 50
    """, conn, params=(analyzer_id,))
=======
        key=f"dl_{key_prefix}_{p.name}_{p.stat().st_mtime_ns}",
    )

def kpi_cards(planned: int = 0, done: int = 0, overdue: int = 0, rate: int = 0):
    st.markdown(
        f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">Planned</div>
        <div class="kpi-value">{planned}</div>
        <div class="kpi-sub">In selected period</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Completed</div>
        <div class="kpi-value">{done}</div>
        <div class="kpi-sub">In selected period</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Overdue</div>
        <div class="kpi-value">{overdue}</div>
        <div class="kpi-sub">Due date passed</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Completion %</div>
        <div class="kpi-value">{rate}%</div>
        <div class="kpi-sub">On-time / Planned</div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

def compute_overdue(row) -> bool:
    stt = safe_str(row.get("status"), "")
    if stt in ["Done", "Cancelled"]:
        return False
    due = parse_date(row.get("due_date"))
    if not due:
        return False
    return due < date.today()

def period_range(mode: str, any_day: date) -> Tuple[date, date]:
    # Week = Sun..Sat
    if mode == "Weekly":
        days_since_sun = (any_day.weekday() + 1) % 7  # Sunday -> 0
        start = any_day - timedelta(days=days_since_sun)
        end = start + timedelta(days=6)
        return start, end

    start = any_day.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1, day=1)
    else:
        next_month = start.replace(month=start.month + 1, day=1)
    end = next_month - timedelta(days=1)
    return start, end

# -----------------------------
# DB Operations
# -----------------------------
def fetch_validations() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT *
        FROM validations
        ORDER BY
          CASE status
            WHEN 'Planned' THEN 1
            WHEN 'In Progress' THEN 2
            WHEN 'Done' THEN 3
            WHEN 'Failed' THEN 4
            WHEN 'Cancelled' THEN 5
            ELSE 9
          END,
          due_date IS NULL, due_date ASC,
          id DESC
    """,
        conn,
    )
    conn.close()
    return df

def insert_validation(payload: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO validations
        (customer_name, validation_type, station, asset_tag, planned_date, due_date,
         status, result, report_no, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            payload["customer_name"],
            payload["validation_type"],
            payload.get("station"),
            payload.get("asset_tag"),
            payload.get("planned_date"),
            payload.get("due_date"),
            payload.get("status", "Planned"),
            payload.get("result"),
            payload.get("report_no"),
            payload.get("notes"),
            now_iso(),
            now_iso(),
        ),
    )
    vid = cur.lastrowid
    conn.commit()
    conn.close()
    return int(vid)

def fetch_tasks() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT *
        FROM tasks
        ORDER BY
          CASE status
            WHEN 'Planned' THEN 1
            WHEN 'In Progress' THEN 2
            WHEN 'On Hold' THEN 3
            WHEN 'Done' THEN 4
            WHEN 'Cancelled' THEN 5
            ELSE 9
          END,
          due_date IS NULL, due_date ASC,
          id DESC
    """,
        conn,
    )
    conn.close()

    if len(df):
        df["is_overdue"] = df.apply(compute_overdue, axis=1)
    else:
        df["is_overdue"] = False
    return df

def insert_task(payload: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tasks
        (wo_number, station, location, department, task_type, asset_tag,
         planned_date, due_date, status, assigned_to, completed_date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            payload["wo_number"],
            payload["station"],
            payload.get("location"),
            payload["department"],
            payload["task_type"],
            payload.get("asset_tag"),
            payload.get("planned_date"),
            payload.get("due_date"),
            payload.get("status", "Planned"),
            payload.get("assigned_to"),
            payload.get("completed_date"),
            payload.get("notes"),
            now_iso(),
            now_iso(),
        ),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(task_id)

def update_task(task_id: int, payload: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE tasks
        SET wo_number=?, station=?, location=?, department=?, task_type=?, asset_tag=?,
            planned_date=?, due_date=?, status=?, assigned_to=?, completed_date=?, notes=?, updated_at=?
        WHERE id=?
    """,
        (
            payload["wo_number"],
            payload["station"],
            payload.get("location"),
            payload["department"],
            payload["task_type"],
            payload.get("asset_tag"),
            payload.get("planned_date"),
            payload.get("due_date"),
            payload.get("status", "Planned"),
            payload.get("assigned_to"),
            payload.get("completed_date"),
            payload.get("notes"),
            now_iso(),
            task_id,
        ),
    )
    conn.commit()
    conn.close()

def add_attachment(task_id: int, file_path: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO task_attachments(task_id, file_path, uploaded_at)
        VALUES (?, ?, ?)
    """,
        (task_id, file_path, now_iso()),
    )
    conn.commit()
    conn.close()

def fetch_attachments(task_id: int) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT id, file_path, uploaded_at
        FROM task_attachments
        WHERE task_id=?
        ORDER BY uploaded_at DESC
    """,
        conn,
        params=(task_id,),
    )
>>>>>>> 10e4590 (synce with changes in codes)
    conn.close()
    return df

# -----------------------------
# UI
# -----------------------------
<<<<<<< HEAD
st.title("GC Analyzer PM Tracking Dashboard")

tab1, tab2, tab_edit, tab3 = st.tabs(["Dashboard", "Add Station Pair", "Edit Station", "Logs & Attachments"])

# -----------------------------
# Dashboard renderers
# -----------------------------
def render_station_grid(df: pd.DataFrame, stations: list[str], mode: str):
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

def render_station_list(df: pd.DataFrame, stations: list[str]):
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
# Tab 1: Dashboard
# -----------------------------
with tab1:
    df = fetch_kpis()

    total_analyzers = len(df)
    total_stations = df["station"].nunique() if len(df) else 0
    overdue_count = int((df["pm_bucket"] == "Overdue").sum())
    due_soon_count = int((df["pm_bucket"] == "Due Soon").sum())

    # KPI cards
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">Stations</div>
        <div class="kpi-value">{total_stations}</div>
        <div class="kpi-sub">Active stations</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Total GC</div>
        <div class="kpi-value">{total_analyzers}</div>
        <div class="kpi-sub">All analyzers</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">PM Overdue</div>
        <div class="kpi-value">{overdue_count}</div>
        <div class="kpi-sub">Needs action</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">PM Due Soon</div>
        <div class="kpi-value">{due_soon_count}</div>
        <div class="kpi-sub">Next 14 days</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
=======
st.title("Instrumentation Tasks Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview (KPI)", "Add / Edit Tasks", "Attachments", "Validation"]
)

# -----------------------------
# Tab 1: Overview KPI
# -----------------------------
with tab1:
    df = fetch_tasks()
>>>>>>> 10e4590 (synce with changes in codes)

    # Control bar
    st.markdown('<div class="control-bar">', unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown('<div class="small-label">Search</div>', unsafe_allow_html=True)
<<<<<<< HEAD
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

    if len(df) == 0:
        st.info("No stations yet. Add station pairs first.")
    else:
        # Search filter for stations
        station_list = sorted(df["station"].unique().tolist())
        if search and search.strip():
            q = search.strip().lower()
            station_list = [
                s for s in station_list
                if q in str(s).lower()
                or q in str(df[df["station"] == s]["location"].iloc[0]).lower()
                or q in " ".join(df[df["station"] == s]["tag"].astype(str).tolist()).lower()
            ]

        # Station-level flags for filters
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

        # Details panel
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

        # Shared PM+Attachment form
        open_for = st.session_state.get("open_attach_for")
        if open_for:
            st.divider()
            st.subheader("PM Log with Attachment")

            df2 = fetch_kpis()
            row = df2[df2["id"] == open_for]
            tag = row["tag"].iloc[0] if len(row) else "Unknown"

            with st.form("attach_form"):
                st.text_input("GC Tag", value=tag, disabled=True)
                performed_by = st.text_input("Performed by (saved for future)", value=st.session_state.get("quick_name", ""))
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
# Tab 2: Add Station Pair
# -----------------------------
with tab2:
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

# -----------------------------
# Tab: Edit Station
# -----------------------------
with tab_edit:
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
# Tab 3: Logs & Attachments
# -----------------------------
with tab3:
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
                        st.error("Invalid timestamp format.")
=======
    q = st.text_input(
        "Search",
        placeholder="WO / Station / Tag / Assigned / Type",
        label_visibility="collapsed",
        key="kpi_search",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="small-label">KPI Mode</div>', unsafe_allow_html=True)
        mode = st.radio("mode", ["Weekly", "Monthly"], horizontal=True, label_visibility="collapsed")
    with c2:
        st.markdown('<div class="small-label">Pick date inside period</div>', unsafe_allow_html=True)
        anchor = st.date_input("anchor", value=date.today(), label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Filters
    if len(df):
        departments = ["ALL"] + sorted(df["department"].dropna().unique().tolist())
        statuses = ["ALL", "Planned", "In Progress", "Done", "On Hold", "Cancelled"]
        types = ["ALL"] + sorted(df["task_type"].dropna().unique().tolist())
    else:
        departments, statuses, types = ["ALL"], ["ALL"], ["ALL"]

    f1, f2, f3 = st.columns(3)
    dep = f1.selectbox("Department", departments, key="kpi_dep")
    stt = f2.selectbox("Status", statuses, key="kpi_status")
    ttype = f3.selectbox("Task type", types, key="kpi_type")

    # Apply filters
    view = df.copy()

    if q and q.strip() and len(view):
        s = q.strip().lower()

        def _hit(r):
            txt = " ".join(
                [
                    safe_str(r.get("wo_number")),
                    safe_str(r.get("station")),
                    safe_str(r.get("location")),
                    safe_str(r.get("department")),
                    safe_str(r.get("task_type")),
                    safe_str(r.get("asset_tag")),
                    safe_str(r.get("assigned_to")),
                    safe_str(r.get("notes")),
                ]
            ).lower()
            return s in txt

        view = view[view.apply(_hit, axis=1)]

    if dep != "ALL" and len(view):
        view = view[view["department"] == dep]
    if stt != "ALL" and len(view):
        view = view[view["status"] == stt]
    if ttype != "ALL" and len(view):
        view = view[view["task_type"] == ttype]

    start, end = period_range(mode, anchor)

    # PM-only toggle
    pm_only = st.checkbox("PM tasks only", value=True, key="kpi_pm_only")

    kpi_df = view.copy()
    if pm_only and len(kpi_df):
        kpi_df = kpi_df[kpi_df.apply(is_pm_task, axis=1)]

    def in_period(d: Optional[date]) -> bool:
        return bool(d and start <= d <= end)

    # Planned = due_date in period (PM compliance)
    planned = 0
    done = 0
    on_time = 0
    backlog = 0
    overdue = int(kpi_df["is_overdue"].sum()) if len(kpi_df) else 0

    if len(kpi_df):
        planned_mask = kpi_df.apply(lambda r: in_period(parse_date(r.get("due_date"))), axis=1).astype(bool)
        planned = int(planned_mask.to_numpy().sum())

        done_mask = kpi_df.apply(
            lambda r: (r.get("status") == "Done") and in_period(parse_date(r.get("completed_date"))),
            axis=1,
        ).astype(bool)
        done = int(done_mask.to_numpy().sum())

        on_time_mask = kpi_df.apply(
            lambda r: (r.get("status") == "Done")
                      and in_period(parse_date(r.get("completed_date")))
                      and date_leq(parse_date(r.get("completed_date")), parse_date(r.get("due_date"))),
            axis=1,
        ).astype(bool)
        on_time = int(on_time_mask.to_numpy().sum())

        backlog_mask = kpi_df.apply(
            lambda r: (r.get("status") not in ["Done", "Cancelled"])
                      and (parse_date(r.get("due_date")) is not None)
                      and (parse_date(r.get("due_date")) < start),
            axis=1,
        ).astype(bool)
        backlog = int(backlog_mask.to_numpy().sum())

    compliance = int(round((on_time / planned) * 100, 0)) if planned > 0 else 0

    st.caption(f"Period: {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}")
    kpi_cards(planned=planned, done=done, overdue=overdue, rate=compliance)

    # Extra KPI row (Backlog + On-time count)
    st.markdown(
        f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-title">On-Time Completed</div>
        <div class="kpi-value">{on_time}</div>
        <div class="kpi-sub">Completed ≤ Due Date</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Backlog</div>
        <div class="kpi-value">{backlog}</div>
        <div class="kpi-sub">Due before period</div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Compliance breakdown
    st.subheader("PM Compliance breakdown")
    if len(kpi_df):
        tmp = kpi_df.copy()
        tmp["due_dt"] = tmp["due_date"].apply(parse_date)
        tmp["comp_dt"] = tmp["completed_date"].apply(parse_date)

        tmp_period = tmp[tmp["due_dt"].apply(lambda d: in_period(d))]
        if len(tmp_period):
            tmp_period = tmp_period.copy()
            tmp_period["planned_pm"] = 1
            tmp_period["done_ontime"] = tmp_period.apply(
                lambda r: 1
                if (
                    r.get("status") == "Done"
                    and r["comp_dt"]
                    and r["due_dt"]
                    and r["comp_dt"] <= r["due_dt"]
                )
                else 0,
                axis=1,
            )
            g = (
                tmp_period.groupby(["department", "station"], dropna=False)[["planned_pm", "done_ontime"]]
                .sum()
                .reset_index()
            )
            g["compliance_%"] = (g["done_ontime"] / g["planned_pm"] * 100).round(0).astype(int)
            g = g.sort_values(["compliance_%", "planned_pm"], ascending=[True, False])
            st.dataframe(g, use_container_width=True, hide_index=True)
        else:
            st.info("No PM planned in this period.")
    else:
        st.info("No tasks.")

    # Overdue / Due Soon (ALWAYS visible, not inside wrong else)
    st.subheader("Overdue / Due Soon")
    soon_days = 14

    def due_days_left(r):
        if r.get("status") in ["Done", "Cancelled"]:
            return None
        dd = parse_date(r.get("due_date"))
        if not dd:
            return None
        return (dd - date.today()).days

    if len(view):
        tmp2 = view.copy()
        tmp2["due_in_days"] = tmp2.apply(due_days_left, axis=1)

        def bucket(d):
            if d is None:
                return 9
            if d < 0:
                return 1
            if d <= soon_days:
                return 2
            return 3

        tmp2["bucket"] = tmp2["due_in_days"].apply(bucket)
        tmp2 = tmp2.sort_values(["bucket", "due_in_days"], ascending=[True, True])

        show_cols = [
            "wo_number",
            "station",
            "location",
            "department",
            "task_type",
            "asset_tag",
            "status",
            "assigned_to",
            "planned_date",
            "due_date",
            "completed_date",
            "due_in_days",
        ]
        st.dataframe(tmp2[show_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No tasks to show.")

# -----------------------------
# Tab 2: Add / Edit
# -----------------------------
with tab2:
    st.subheader("Add New Task (Work Order based)")
    with st.form("add_task_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        wo = c1.text_input("Work Order Number (WO)", placeholder="e.g., 4500xxxxx")
        station = c2.text_input("Station", placeholder="e.g., BCS-01")
        location = c3.text_input("Location / Area", placeholder="e.g., BCS")

        c4, c5, c6 = st.columns(3)
        department = c4.selectbox(
            "Department",
            ["Instrument", "Electrical", "Mechanical", "Network", "Facility", "Operation"],
        )
        task_type = c5.text_input("Task Type", placeholder="e.g., PM / Calibration / F&G")
        asset_tag = c6.text_input("Asset Tag (optional)", placeholder="e.g., PT-101 / GC-01 / FGD-22")

        c7, c8, c9 = st.columns(3)
        planned_date_val = c7.date_input("Planned Date", value=date.today())
        due_date_val = c8.date_input("Due Date", value=date.today())
        status = c9.selectbox("Status", ["Planned", "In Progress", "Done", "On Hold", "Cancelled"])

        assigned_to = st.text_input("Assigned To", placeholder="e.g., Omar")
        completed_date = st.text_input(
            "Completed Date (YYYY-MM-DD)",
            value="" if status != "Done" else today_str(),
        )
        notes = st.text_area("Notes")

        submit = st.form_submit_button("Save Task")

        if submit:
            if not wo.strip() or not station.strip() or not task_type.strip():
                st.error("WO Number, Station, and Task Type are required.")
                st.stop()

            # Validate completed_date
            if completed_date.strip():
                try:
                    parse_date(completed_date.strip())
                except Exception:
                    st.error("Completed Date format must be YYYY-MM-DD")
                    st.stop()

            task_id = insert_task(
                {
                    "wo_number": wo.strip(),
                    "station": station.strip(),
                    "location": location.strip() if location.strip() else None,
                    "department": department,
                    "task_type": task_type.strip(),
                    "asset_tag": asset_tag.strip() if asset_tag.strip() else None,
                    "planned_date": planned_date_val.strftime("%Y-%m-%d"),
                    "due_date": due_date_val.strftime("%Y-%m-%d"),
                    "status": status,
                    "assigned_to": assigned_to.strip() if assigned_to.strip() else None,
                    "completed_date": completed_date.strip() if completed_date.strip() else None,
                    "notes": notes.strip() if notes.strip() else None,
                }
            )
            st.success(f"Saved. Task ID: {task_id}")
            st.rerun()

    st.divider()
    st.subheader("Edit Existing Task")

    df2 = fetch_tasks()
    if len(df2) == 0:
        st.info("No tasks yet.")
    else:
        df2 = df2.copy()
        df2["display"] = df2.apply(
            lambda r: f"ID:{r['id']} | WO:{r['wo_number']} | {r['station']} | {r['task_type']} | {r['status']}",
            axis=1,
        )
        pick = st.selectbox("Pick task", df2["display"].tolist(), key="edit_pick")
        row = df2[df2["display"] == pick].iloc[0]
        task_id = int(row["id"])

        with st.form("edit_task_form"):
            c1, c2, c3 = st.columns(3)
            wo = c1.text_input("WO", value=safe_str(row.get("wo_number"), ""))
            station = c2.text_input("Station", value=safe_str(row.get("station"), ""))
            location = c3.text_input("Location", value=safe_str(row.get("location"), ""))

            c4, c5, c6 = st.columns(3)
            department = c4.text_input("Department", value=safe_str(row.get("department"), "Instrument"))
            task_type = c5.text_input("Task Type", value=safe_str(row.get("task_type"), ""))
            asset_tag = c6.text_input("Asset Tag", value=safe_str(row.get("asset_tag"), ""))

            c7, c8, c9 = st.columns(3)
            planned_date = c7.text_input("Planned Date (YYYY-MM-DD)", value=safe_str(row.get("planned_date"), ""))
            due_date = c8.text_input("Due Date (YYYY-MM-DD)", value=safe_str(row.get("due_date"), ""))

            status_list = ["Planned", "In Progress", "Done", "On Hold", "Cancelled"]
            current_status = safe_str(row.get("status"), "Planned")
            status_idx = status_list.index(current_status) if current_status in status_list else 0
            status = c9.selectbox("Status", status_list, index=status_idx)

            assigned_to = st.text_input("Assigned To", value=safe_str(row.get("assigned_to"), ""))
            completed_date = st.text_input("Completed Date (YYYY-MM-DD)", value=safe_str(row.get("completed_date"), ""))
            notes = st.text_area("Notes", value=safe_str(row.get("notes"), ""))

            save = st.form_submit_button("Save Changes")
            if save:
                if not wo.strip() or not station.strip() or not task_type.strip():
                    st.error("WO, Station, Task Type are required.")
                    st.stop()

                try:
                    if planned_date.strip():
                        parse_date(planned_date.strip())
                    if due_date.strip():
                        parse_date(due_date.strip())
                    if completed_date.strip():
                        parse_date(completed_date.strip())
                except Exception:
                    st.error("Date format must be YYYY-MM-DD")
                    st.stop()

                update_task(
                    task_id,
                    {
                        "wo_number": wo.strip(),
                        "station": station.strip(),
                        "location": location.strip() if location.strip() else None,
                        "department": department.strip(),
                        "task_type": task_type.strip(),
                        "asset_tag": asset_tag.strip() if asset_tag.strip() else None,
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
# Tab 3: Attachments
# -----------------------------
with tab3:
    df3 = fetch_tasks()
    if len(df3) == 0:
        st.info("Add tasks first.")
    else:
        df3 = df3.copy()
        df3["display"] = df3.apply(
            lambda r: f"ID:{r['id']} | WO:{r['wo_number']} | {r['station']} | {r['task_type']}",
            axis=1,
        )
        pick = st.selectbox("Pick task", df3["display"].tolist(), key="att_pick")
        row = df3[df3["display"] == pick].iloc[0]
        task_id = int(row["id"])

        st.write(
            f"**Task:** ID {task_id} | WO {row['wo_number']} | {row['station']} | "
            f"{row['task_type']} | {row['status']}"
        )

        st.subheader("Upload attachment")
        with st.form("upload_attach"):
            file = st.file_uploader("Attachment (photo/pdf/etc.)", type=None)
            ok = st.form_submit_button("Upload")
            if ok:
                if file is None:
                    st.error("Please choose a file.")
                else:
                    safe_name = f"task{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                    dest = UPLOAD_DIR / safe_name
                    dest.write_bytes(file.getbuffer())
                    add_attachment(task_id, str(dest))
                    st.success("Uploaded.")
                    st.rerun()

        st.divider()
        st.subheader("Attachments list")
        att = fetch_attachments(task_id)
        if len(att) == 0:
            st.info("No attachments yet.")
        else:
            for i, rr in att.iterrows():
                path = rr["file_path"]
                with st.expander(f"📎 {rr['uploaded_at']} — {Path(path).name}"):
                    show_attachment(path, key_prefix=f"t{task_id}_{i}")

# -----------------------------
# Tab 4: Validation
# -----------------------------
with tab4:
    st.subheader("Validation Dashboard")

    vdf = fetch_validations()
    if len(vdf) == 0:
        st.info("No validations yet. Add first below.")
    else:
        c1, c2, c3 = st.columns(3)
        vtype = c1.selectbox("Validation Type", ["ALL", "FMS", "GC", "PRT"], key="v_type")
        cust = c2.selectbox(
            "Customer",
            ["ALL"] + sorted(vdf["customer_name"].dropna().unique().tolist()),
            key="v_cust",
        )
        vstatus = c3.selectbox(
            "Status",
            ["ALL", "Planned", "In Progress", "Done", "Failed", "Cancelled"],
            key="v_status",
        )

        viewv = vdf.copy()
        if vtype != "ALL":
            viewv = viewv[viewv["validation_type"] == vtype]
        if cust != "ALL":
            viewv = viewv[viewv["customer_name"] == cust]
        if vstatus != "ALL":
            viewv = viewv[viewv["status"] == vstatus]

        planned_v = int((viewv["status"].isin(["Planned", "In Progress"])).sum())
        done_v = int((viewv["status"] == "Done").sum())
        failed_v = int((viewv["status"] == "Failed").sum())

        def is_overdue_val(r):
            if r.get("status") in ["Done", "Cancelled"]:
                return False
            dd = parse_date(r.get("due_date"))
            return bool(dd and dd < date.today())

        viewv = viewv.copy()
        viewv["is_overdue"] = viewv.apply(is_overdue_val, axis=1)
        overdue_v = int(viewv["is_overdue"].sum())

        st.markdown(
            f"""
        <div class="kpi-row">
          <div class="kpi-card"><div class="kpi-title">Open</div><div class="kpi-value">{planned_v}</div><div class="kpi-sub">Planned + In Progress</div></div>
          <div class="kpi-card"><div class="kpi-title">Done</div><div class="kpi-value">{done_v}</div><div class="kpi-sub">Completed</div></div>
          <div class="kpi-card"><div class="kpi-title">Failed</div><div class="kpi-value">{failed_v}</div><div class="kpi-sub">Requires action</div></div>
          <div class="kpi-card"><div class="kpi-title">Overdue</div><div class="kpi-value">{overdue_v}</div><div class="kpi-sub">Past due date</div></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.subheader("List")
        show_cols = [
            "customer_name",
            "validation_type",
            "station",
            "asset_tag",
            "planned_date",
            "due_date",
            "status",
            "result",
            "report_no",
            "notes",
        ]
        st.dataframe(viewv[show_cols], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Add New Validation (FMS / GC / PRT)")

    with st.form("add_validation_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        customer_name = c1.text_input("Customer Name", placeholder="e.g., Customer A")
        validation_type = c2.selectbox("Validation Type", ["FMS", "GC", "PRT"])
        station = c3.text_input("Station", placeholder="e.g., BCS-01")

        c4, c5, c6 = st.columns(3)
        asset_tag = c4.text_input("Asset Tag", placeholder="optional")
        planned_date = c5.date_input("Planned Date", value=date.today())
        due_date = c6.date_input("Due Date", value=date.today())

        c7, c8, c9 = st.columns(3)
        status = c7.selectbox("Status", ["Planned", "In Progress", "Done", "Failed", "Cancelled"])
        result = c8.selectbox("Result", ["NA", "Pass", "Fail"])
        report_no = c9.text_input("Report No", placeholder="optional")

        notes = st.text_area("Notes")

        save_val = st.form_submit_button("Save Validation")
        if save_val:
            if not customer_name.strip():
                st.error("Customer Name is required.")
                st.stop()

            insert_validation(
                {
                    "customer_name": customer_name.strip(),
                    "validation_type": validation_type,
                    "station": station.strip() if station.strip() else None,
                    "asset_tag": asset_tag.strip() if asset_tag.strip() else None,
                    "planned_date": planned_date.strftime("%Y-%m-%d") if planned_date else None,
                    "due_date": due_date.strftime("%Y-%m-%d") if due_date else None,
                    "status": status,
                    "result": result,
                    "report_no": report_no.strip() if report_no.strip() else None,
                    "notes": notes.strip() if notes.strip() else None,
                }
            )
            st.success("Saved.")
            st.rerun()
>>>>>>> 10e4590 (synce with changes in codes)
