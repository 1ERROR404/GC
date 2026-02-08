# app.py (UPDATED: Customizable card views)
# ✅ PM-only dashboard
# ✅ Same tags can repeat across stations (GC-01/GC-02 per station)
# ✅ Dashboard view modes: List | Big cards | Medium cards | Small cards (icon buttons)
# ✅ Click station => Full details panel
# ✅ Add Station Pair (add-only)
# ✅ Edit Station tab
# ✅ Attachments upload + view/download

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes

from db import init_db, get_conn

st.set_page_config(page_title="GC Analyzer PM Dashboard", layout="wide")
init_db()
# ---- Mobile-friendly UI tweaks ----
st.markdown("""
<style>
            /* --- Responsive controls (filters + view buttons) --- */
.ctrl-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  align-items: center;
}

.ctrl-btn > div button {
  width: 100%;
  min-height: 42px;
}

/* Make icon buttons not too small */
.icon-btn > div button {
  min-width: 44px;
  min-height: 42px;
  padding: 0.35rem 0.6rem;
}

/* Mobile: bigger tap targets */
@media (max-width: 700px) {
  .ctrl-btn > div button,
  .icon-btn > div button {
    min-height: 46px;
    font-size: 15px !important;
  }
}
/* Make overall spacing tighter */
div[data-testid="stVerticalBlock"] { gap: 0.6rem; }

/* Reduce padding on containers */
section.main > div { padding-top: 1rem; padding-bottom: 1rem; }

/* Make buttons a bit more compact */
button[kind="secondary"], button[kind="primary"] { padding: 0.35rem 0.6rem; }

/* Mobile adjustments */
@media (max-width: 700px) {
  html, body, [class*="css"] { font-size: 14px !important; }

  /* Force columns to stack vertically */
  div[data-testid="column"] {
    width: 100% !important;
    flex: 1 1 100% !important;
    max-width: 100% !important;
  }

  /* Make tables scroll horizontally instead of squeezing */
  div[data-testid="stDataFrame"] { overflow-x: auto; }

  /* Smaller headers */
  h1 { font-size: 1.4rem !important; }
  h2 { font-size: 1.15rem !important; }
  h3 { font-size: 1.05rem !important; }
}
</style>
""", unsafe_allow_html=True)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# -----------------------------
# Helpers
# -----------------------------
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
    if not p.exists():
        st.warning("Attachment file not found on this PC.")
        st.code(str(p))
        return

    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "application/octet-stream"

    if mime.startswith("image/"):
        st.image(str(p), caption=p.name, use_container_width=True)

    st.download_button(
        label=f"📥 Download / View: {p.name}",
        data=p.read_bytes(),
        file_name=p.name,
        mime=mime,
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
    cur = conn.cursor()

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
    conn.close()
    return df

# -----------------------------
# UI
# -----------------------------
st.title("GC Analyzer PM Tracking Dashboard")

tab1, tab2, tab_edit, tab3 = st.tabs(["Dashboard", "Add Station Pair", "Edit Station", "Logs & Attachments"])

# -----------------------------
# Dashboard view renderer
# -----------------------------
def render_station_grid(df: pd.DataFrame, stations: list[str], mode: str):
    # grid sizes
    if mode == "BIG":
        cols_per_row = 1
    elif mode == "MED":
        cols_per_row = 2
    else:  # SMALL
        cols_per_row = 3

    rows = [stations[i:i+cols_per_row] for i in range(0, len(stations), cols_per_row)]
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
    # list view uses dataframe + open buttons
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
    # compact open buttons
    btn_cols = st.columns(6)
    idx = 0
    for station in stations:
        c = btn_cols[idx % 6]
        with c:
            if st.button(station, key=f"open_list_{station}"):
                st.session_state["selected_station"] = station
                st.rerun()
        idx += 1

# -----------------------------
# Tab 1: Dashboard
# -----------------------------
with tab1:
    df = fetch_kpis()

    total_analyzers = len(df)
    total_stations = df["station"].nunique() if len(df) else 0
    overdue_count = int((df["pm_bucket"] == "Overdue").sum())
    due_soon_count = int((df["pm_bucket"] == "Due Soon").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stations", total_stations)
    c2.metric("Total GC", total_analyzers)
    c3.metric("PM Overdue", overdue_count)
    c4.metric("PM Due Soon", due_soon_count)

    # Filters + View options
    left, right = st.columns([2, 1])

    with left:
        st.subheader("PM Filters (Stations)")
        f1, f2, f3 = st.columns(3)
        if f1.button("Show All", use_container_width=True):
            st.session_state["station_filter"] = "ALL"
        if f2.button("🔴 PM Overdue", use_container_width=True):
            st.session_state["station_filter"] = "OVERDUE"
        if f3.button("🟠 PM Due Soon", use_container_width=True):
            st.session_state["station_filter"] = "DUESOON"
        if "station_filter" not in st.session_state:
            st.session_state["station_filter"] = "ALL"

    with right:
        st.subheader("View")

        vrow1 = st.columns(2)
        vrow2 = st.columns(2)

        if vrow1[0].button("📋", help="List", use_container_width=True):
            st.session_state["view_mode"] = "LIST"
        if vrow1[1].button("🟥", help="Big cards", use_container_width=True):
            st.session_state["view_mode"] = "BIG"
        if vrow2[0].button("🟧", help="Medium cards", use_container_width=True):
            st.session_state["view_mode"] = "MED"
        if vrow2[1].button("🟨", help="Small cards", use_container_width=True):
            st.session_state["view_mode"] = "SMALL"

        if "view_mode" not in st.session_state:
            st.session_state["view_mode"] = "SMALL"
            
    if "selected_station" not in st.session_state:
        st.session_state["selected_station"] = None

    if len(df) == 0:
        st.info("No stations yet. Add station pairs first.")
    else:
        # station-level flags for filters
        stations = []
        for station, g in df.groupby("station"):
            any_overdue = (g["pm_bucket"] == "Overdue").any()
            any_due_soon = (g["pm_bucket"] == "Due Soon").any()
            stations.append((station, any_overdue, any_due_soon))
        station_df = pd.DataFrame(stations, columns=["station", "any_overdue", "any_due_soon"])

        mode = st.session_state["station_filter"]
        filtered_stations = station_df["station"].tolist()
        if mode == "OVERDUE":
            filtered_stations = station_df[station_df["any_overdue"]]["station"].tolist()
        elif mode == "DUESOON":
            filtered_stations = station_df[station_df["any_due_soon"]]["station"].tolist()

        filtered_stations = sorted(filtered_stations)

        st.caption("Click a station to open full details.")
        vm = st.session_state["view_mode"]
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

            cols = st.columns(2)

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

                        render_gc(cols[0], "GC-01", duty_df, "Duty")
                        render_gc(cols[1], "GC-02", standby_df, "Standby")

            


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
                performed_by = st.text_input(
                    "Performed by (saved for future)",
                    value=st.session_state.get("quick_name", "")
                )
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
