import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone

st.set_page_config(page_title="Reporter Dashboard (Jira)", page_icon="👤",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif!important;box-sizing:border-box;}
.main,[data-testid="stAppViewContainer"]{background:#f0f4f8;}
.block-container{padding:1.5rem 2.2rem 3rem!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #e2e8f0;}
[data-testid="stSidebar"] .block-container{padding:1.4rem 1rem!important;}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden;}
.banner{background:linear-gradient(120deg,#1e40af,#2563eb 55%,#0ea5e9);
  border-radius:18px;padding:28px 36px;margin-bottom:26px;
  box-shadow:0 8px 32px rgba(37,99,235,.22);}
.banner-title{font-size:1.7rem;font-weight:900;color:#fff;letter-spacing:-.02em;}
.banner-sub{font-size:.84rem;color:rgba(255,255,255,.78);margin-top:4px;}
.bstat{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.28);
  border-radius:9px;padding:4px 13px;font-size:.79rem;font-weight:700;color:#fff;
  display:inline-block;margin:4px 4px 0 0;}
.proj-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.72rem;
  font-weight:800;margin-right:4px;color:#fff;}
.kpi-row{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:24px;}
.kpi{background:#fff;border-radius:16px;padding:20px 20px 16px;
  border:1px solid #e2e8f0;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.kpi-icon{font-size:1.5rem;margin-bottom:7px;}
.kpi-val{font-size:2rem;font-weight:900;color:#0f172a;line-height:1;}
.kpi-lbl{font-size:.7rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
  letter-spacing:.09em;margin-top:5px;}
.kpi-note{font-size:.72rem;color:#64748b;margin-top:3px;}
.proj-kpi-grid{display:grid;gap:18px;margin-bottom:24px;}
.proj-card{background:#fff;border-radius:16px;padding:18px 22px;border:1px solid #e2e8f0;
  box-shadow:0 1px 6px rgba(0,0,0,.05);}
.proj-card-title{font-size:1rem;font-weight:900;margin-bottom:12px;}
.proj-stats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;}
.pstat{text-align:center;padding:10px 6px;background:#f8fafc;border-radius:10px;}
.pstat-val{font-size:1.3rem;font-weight:900;color:#0f172a;}
.pstat-lbl{font-size:.62rem;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-top:3px;}
.stitle{font-size:.77rem;font-weight:800;color:#64748b;text-transform:uppercase;
  letter-spacing:.1em;border-left:3px solid #2563eb;padding-left:9px;margin:0 0 14px;}
.wcard{background:#fff;border:1px solid #e2e8f0;border-radius:16px;
  padding:22px 22px 14px;margin-bottom:20px;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.rep-row{background:#fff;border:1px solid #e2e8f0;border-radius:13px;
  padding:15px 18px;margin-bottom:9px;display:grid;
  grid-template-columns:200px 60px 80px 150px 150px 80px 80px 80px 1fr;
  align-items:center;gap:10px;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.rep-row:hover{box-shadow:0 4px 16px rgba(37,99,235,.1);border-color:#bfdbfe;}
.avatar{width:36px;height:36px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:.82rem;font-weight:900;color:#fff;}
.rep-name{font-size:.86rem;font-weight:700;color:#1e293b;}
.rep-sub{font-size:.68rem;color:#94a3b8;margin-top:1px;}
.mbar-lbl{font-size:.67rem;display:flex;justify-content:space-between;margin-bottom:3px;}
.mbar-track{background:#f1f5f9;border-radius:6px;height:7px;overflow:hidden;display:flex;}
.stat-center{text-align:center;}
.stat-val{font-size:1rem;font-weight:800;}
.stat-lbl{font-size:.63rem;color:#94a3b8;font-weight:700;text-transform:uppercase;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:4px 9px;
  border-radius:20px;font-size:.69rem;font-weight:700;}
.pbar{margin-bottom:13px;}
.pbar-head{display:flex;justify-content:space-between;align-items:center;
  font-size:.79rem;margin-bottom:4px;}
.pbar-name{font-weight:700;color:#1e293b;}
.pbar-val{font-weight:800;font-size:.81rem;}
.pbar-track{background:#f1f5f9;border-radius:8px;height:9px;overflow:hidden;}
.pbar-fill{height:100%;border-radius:8px;}
.insight-box{background:#eff6ff;border:1px solid #bfdbfe;border-radius:12px;
  padding:14px 18px;margin-bottom:14px;}
.insight-title{font-size:.78rem;font-weight:800;color:#1d4ed8;margin-bottom:6px;text-transform:uppercase;}
.insight-item{font-size:.8rem;color:#1e293b;margin-bottom:4px;display:flex;align-items:center;gap:6px;}
[data-testid="stTabs"]>div:first-child{border-bottom:2px solid #e2e8f0;}
[data-testid="stTabs"] button{font-size:.82rem!important;font-weight:600!important;color:#64748b!important;}
[data-testid="stTabs"] button[aria-selected="true"]{color:#2563eb!important;border-bottom:2px solid #2563eb!important;}
p,span,div,label,li,h1,h2,h3,h4,h5{color:#0f172a;}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] strong{color:#0f172a!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label{color:#0f172a!important;}
[data-testid="stMultiSelect"] span,[data-testid="stSelectbox"] span{color:#0f172a!important;}
[data-testid="stTextInput"] input{color:#0f172a!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#f1f5f9;}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:5px;}
</style>
""", unsafe_allow_html=True)

# ── Colours ───────────────────────────────────────────────────────────────────
AV = ["#2563eb","#7c3aed","#db2777","#ea580c","#059669",
      "#0891b2","#d97706","#9333ea","#dc2626","#0284c7"]
SC = {"NEW":"#3b82f6","To Do":"#8b5cf6","In Progress":"#f97316",
      "Assigned To Developer":"#06b6d4","IN TESTING":"#eab308",
      "RE-TEST FAIL":"#ef4444","ACCEPTED":"#10b981","Done":"#22c55e",
      "Closed":"#22c55e","Rejected":"#94a3b8","BLOCKED":"#dc2626","Blocked":"#dc2626"}

# ── Configurable field matchers (case-insensitive) ────────────────────────────
RESOLVED_STATUSES  = {"done", "accepted", "closed", "resolved", "fixed"}
OPEN_STATUSES      = {"new", "open", "to do", "todo"}
BLOCKED_STATUSES   = {"blocked"}
RETEST_FAIL_STATUS = {"re-test fail", "retest fail"}
BUG_TYPES          = {"bug", "defect"}
IMPROVEMENT_TYPES  = {"improvement", "enhancement", "new feature"}
HIGH_PRIORITIES    = {"highest", "high", "critical", "blocker"}

def is_resolved(s):   return str(s).strip().lower() in RESOLVED_STATUSES
def is_open(s):       return str(s).strip().lower() in OPEN_STATUSES
def is_blocked(s):    return str(s).strip().lower() in BLOCKED_STATUSES
def is_retest(s):     return str(s).strip().lower() in RETEST_FAIL_STATUS
def is_bug(t):        return str(t).strip().lower() in BUG_TYPES
def is_improvement(t):return str(t).strip().lower() in IMPROVEMENT_TYPES
def is_high_prio(p):  return str(p).strip().lower() in HIGH_PRIORITIES
PC_COL = {"Highest":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e","Lowest":"#3b82f6"}
TC = {"Bug":"#ef4444","Improvement":"#3b82f6","Task":"#8b5cf6","Epic":"#f97316",
      "Story":"#22c55e","New Feature":"#06b6d4","Sub-task":"#eab308","Initiative":"#ec4899"}
PROJ_COLORS = ["#2563eb","#7c3aed","#059669","#ea580c","#0891b2","#db2777"]
BG="#fff"; GRID="#edf0f5"; TXT="#0f172a"; TXT2="#475569"

def B(h=360):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TXT, family="Inter,sans-serif", size=12),
        height=h,
        xaxis=dict(gridcolor=GRID, linecolor="#d1d9e6", zerolinecolor=GRID,
                   tickfont=dict(size=11, color=TXT2), title_font=dict(color=TXT2)),
        yaxis=dict(gridcolor=GRID, linecolor="#d1d9e6", zerolinecolor=GRID,
                   tickfont=dict(size=11, color=TXT2), title_font=dict(color=TXT2)),
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#475569",
                        font_color="#f8fafc", font_size=12),
    )

LEG_H = dict(bgcolor="#fff", bordercolor="#e2e8f0", font=dict(size=11, color=TXT),
             orientation="h", y=1.08, x=0)
LEG_V = dict(bgcolor="#fff", bordercolor="#e2e8f0", font=dict(size=10, color=TXT),
             orientation="v", x=1.01, y=0.5)

def initials(n):
    p = n.strip().split()
    return (p[0][0]+(p[-1][0] if len(p)>1 else "")).upper()

REPORTER_IDS = (
    "reporter in (712020:a685ca99-6022-4256-93fd-ec3883cb5dad,"
    "712020:316426a6-cf5c-41ef-9616-d3afb6c93c13,"
    "712020:6fba3e29-74d4-4157-8e00-d8f0e6d9cac1,"
    "712020:77f75184-11d8-42af-8ecf-96ca5c1b6e0f,"
    "712020:8a463aa9-dfca-4084-ab92-6767d45b89a9,"
    "712020:7ad67c60-6092-419f-842e-e54ff0319397,"
    "712020:1a36b20a-3e85-4c7b-a127-b22c2de52097,"
    "712020:dd54aff3-0ac7-46e7-a396-fba3d71cc6ef,"
    "61a5fa5bf24150007202bf14,"
    "712020:2dfcbecb-7ec3-4e3a-b254-cce35dfa1566,"
    "712020:4d18b64a-cfa6-4195-80d9-75679183fc4f)"
)

# ── Jira config (sidebar) ─────────────────────────────────────────────────────
_raw_secrets = st.secrets.get("jira", {})
_s = dict(_raw_secrets) if _raw_secrets else {}
with st.sidebar:
    st.markdown("## ⚙️ Jira Connection")
    JIRA_URL   = st.text_input("Jira URL",  value=_s.get("url",   "https://grampower.atlassian.net"), key="jurl")
    JIRA_EMAIL = st.text_input("Email",     value=_s.get("email", "lalit.tak@polarisgrids.com"),      key="jemail")
    JIRA_TOKEN = st.text_input("API Token", value=_s.get("token", ""), type="password",               key="jtoken")
    raw_projects = st.text_input(
        "Project Key(s)",
        value=_s.get("project", "PC"),
        placeholder="PC, PCS, DEMO",
        help="Enter one or more project keys separated by commas",
        key="jproject"
    )
    connect_btn = st.button("🔗 Connect", use_container_width=True)
    st.markdown("---")

PROJECT_KEYS = [p.strip().upper() for p in raw_projects.split(",") if p.strip()]

# ── Jira data loader (per project) ───────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_project_data(url, email, token, project):
    auth    = (email, token)
    headers = {"Accept": "application/json"}
    fields  = "summary,status,priority,assignee,reporter,issuetype,created,resolutiondate"
    issues  = []
    next_token = None
    while True:
        payload = {
            "jql": f"project={project} AND {REPORTER_IDS} ORDER BY created DESC",
            "maxResults": 100,
            "fields": fields.split(","),
        }
        if next_token:
            payload["nextPageToken"] = next_token
        resp = requests.post(
            f"{url}/rest/api/3/search/jql",
            auth=auth, headers={**headers, "Content-Type": "application/json"},
            json=payload, timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        for issue in data.get("issues", []):
            f = issue["fields"]
            issues.append({
                "issue_key":       issue["key"],
                "project":         project,
                "summary":         f.get("summary", ""),
                "issue_type":      (f.get("issuetype")   or {}).get("name", ""),
                "status":          (f.get("status")      or {}).get("name", ""),
                "priority":        (f.get("priority")    or {}).get("name", ""),
                "assignee":        (f.get("assignee")    or {}).get("displayName", "Unassigned"),
                "reporter":        (f.get("reporter")    or {}).get("displayName", "Unknown"),
                "created":         f.get("created", ""),
                "resolutiondate":  f.get("resolutiondate", None),
            })
        if data.get("isLast", True) or not data.get("nextPageToken"):
            break
        next_token = data["nextPageToken"]

    df = pd.DataFrame(issues)
    if df.empty:
        return df
    df["issue_type"]      = df["issue_type"].str.strip()
    df                    = df[df["reporter"].notna() & (df["reporter"].str.strip() != "")]
    df["created_dt"]      = pd.to_datetime(df["created"], errors="coerce", utc=True)
    df["created_dt"]      = df["created_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["resolved_dt"]     = pd.to_datetime(df["resolutiondate"], errors="coerce", utc=True)
    df["resolved_dt"]     = df["resolved_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    now                   = datetime.now()
    df["age_days"]        = (now - df["created_dt"]).dt.days
    df["resolution_days"] = (df["resolved_dt"] - df["created_dt"]).dt.days
    df["month_period"]    = df["created_dt"].dt.to_period("M")
    df["week_period"]     = df["created_dt"].dt.to_period("W")
    df["age_bucket"]      = pd.cut(
        df["age_days"],
        bins=[-1, 7, 30, 90, 180, 99999],
        labels=["0–7 days","8–30 days","31–90 days","91–180 days","180+ days"]
    )
    return df

def load_all_projects(url, email, token, projects):
    frames = {}
    for p in projects:
        with st.spinner(f"Fetching {p}…"):
            try:
                frames[p] = load_project_data(url, email, token, p)
            except Exception as e:
                st.error(f"Error loading {p}: {e}")
                frames[p] = pd.DataFrame()
    return frames

# ── Load ──────────────────────────────────────────────────────────────────────
if not JIRA_TOKEN:
    st.info("Enter your Jira API Token in the sidebar and click **Connect**."); st.stop()

if connect_btn or st.session_state.pop("do_refresh", False):
    load_project_data.clear()

project_frames = load_all_projects(JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEYS)
combined_df    = pd.concat([f for f in project_frames.values() if not f.empty], ignore_index=True)

if combined_df.empty:
    st.warning("No issues found across any project."); st.stop()

fetched_at = datetime.now().strftime("%d %b %Y, %H:%M:%S")

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
all_rep  = sorted(combined_df["reporter"].dropna().unique())
all_type = sorted(combined_df["issue_type"].dropna().unique())
all_stat = sorted(combined_df["status"].dropna().unique())
all_prio = sorted(combined_df["priority"].dropna().unique())
sel_rep  = st.sidebar.multiselect("Reporter",   all_rep,  default=all_rep)
sel_type = st.sidebar.multiselect("Issue Type", all_type, default=all_type)
sel_stat = st.sidebar.multiselect("Status",     all_stat, default=all_stat)
sel_prio = st.sidebar.multiselect("Priority",   all_prio, default=all_prio)
if combined_df["created_dt"].notna().any():
    mn = combined_df["created_dt"].min().date()
    mx = combined_df["created_dt"].max().date()
    dr = st.sidebar.date_input("Date Range", (mn, mx), min_value=mn, max_value=mx)
else:
    dr = None
st.sidebar.markdown("---")
with st.sidebar.expander("🔬 Data Inspector", expanded=False):
    st.markdown("**Actual Issue Types in data:**")
    if not combined_df.empty:
        type_counts = combined_df["issue_type"].value_counts()
        for t, c in type_counts.items():
            st.markdown(f"- `{t}`: {c}")
    st.markdown("**Actual Statuses in data:**")
    if not combined_df.empty:
        stat_counts = combined_df["status"].value_counts()
        for s, c in stat_counts.items():
            st.markdown(f"- `{s}`: {c}")
    st.markdown("**Actual Priorities in data:**")
    if not combined_df.empty:
        prio_counts = combined_df["priority"].value_counts()
        for p, c in prio_counts.items():
            st.markdown(f"- `{p}`: {c}")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh"):
    st.session_state["do_refresh"] = True
    st.rerun()

def apply_filters(df):
    if sel_rep:  df = df[df["reporter"].isin(sel_rep)]
    if sel_type: df = df[df["issue_type"].isin(sel_type)]
    if sel_stat: df = df[df["status"].isin(sel_stat)]
    if sel_prio: df = df[df["priority"].isin(sel_prio)]
    if dr and len(dr) == 2:
        df = df[(df["created_dt"].dt.date >= dr[0]) & (df["created_dt"].dt.date <= dr[1])]
    return df

df = apply_filters(combined_df.copy())
filtered_frames = {p: apply_filters(f.copy()) for p, f in project_frames.items() if not f.empty}

# ── Helper: aggregate per-reporter ───────────────────────────────────────────
def agg_reporters(data):
    if data.empty:
        return pd.DataFrame()
    rep = (
        data.groupby("reporter").agg(
            total      =("issue_key","count"),
            bugs       =("issue_type", lambda x: x.apply(is_bug).sum()),
            improv     =("issue_type", lambda x: x.apply(is_improvement).sum()),
            resolved   =("status",     lambda x: x.apply(is_resolved).sum()),
            new_open   =("status",     lambda x: x.apply(is_open).sum()),
            retest_fail=("status",     lambda x: x.apply(is_retest).sum()),
            blocked    =("status",     lambda x: x.apply(is_blocked).sum()),
            high_prio  =("priority",   lambda x: x.apply(is_high_prio).sum()),
            avg_age    =("age_days",   "mean"),
            avg_res_days=("resolution_days", lambda x: x.dropna().mean() if x.notna().any() else float("nan")),
        ).reset_index().sort_values("total", ascending=False)
    )
    rep["res_pct"]  = (rep["resolved"] / rep["total"] * 100).round(1)
    rep["open_pct"] = (rep["new_open"]  / rep["total"] * 100).round(1)
    return rep

rep_df    = agg_reporters(df)
n_rep     = len(rep_df)
rep_order = rep_df["reporter"].tolist() if not rep_df.empty else []
bar_h     = max(420, n_rep * 48 + 100)

total_all    = len(df)
resolved_all = int(df["status"].apply(is_resolved).sum())
res_rate     = round(resolved_all / total_all * 100, 1) if total_all else 0
bugs_all     = int(df["issue_type"].apply(is_bug).sum())
impr_all     = int(df["issue_type"].apply(is_improvement).sum())
open_all     = int(df["status"].apply(is_open).sum())
blocked_all  = int(df["status"].apply(is_blocked).sum())
avg_age      = round(df["age_days"].mean(), 1) if total_all else 0
avg_res_d    = df["resolution_days"].dropna()
avg_res_days = round(avg_res_d.mean(), 1) if len(avg_res_d) > 0 else None

# ── PDF Export (sidebar) ──────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("## 📄 Export Report")
if st.sidebar.button("⬇️ Generate PDF Report", use_container_width=True):
    from pdf_report import generate_pdf_report
    with st.sidebar:
        with st.spinner("Building PDF…"):
            pdf_buf = generate_pdf_report(
                df, rep_df, total_all, resolved_all, res_rate,
                bugs_all, impr_all, open_all, n_rep,
                fetched_at, ", ".join(PROJECT_KEYS),
                filtered_frames=filtered_frames,
            )
    st.sidebar.download_button(
        label="📥 Download Report PDF",
        data=pdf_buf,
        file_name=f"jira_reporter_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ════════════════════════════════════════════════════════════════
# BANNER
# ════════════════════════════════════════════════════════════════
proj_badges = "".join(
    f'<span class="proj-badge" style="background:{PROJ_COLORS[i % len(PROJ_COLORS)]};">{p}</span>'
    for i, p in enumerate(PROJECT_KEYS)
)
st.markdown(f"""
<div class="banner">
  <div class="banner-title">👤 Reporter Analytics Dashboard</div>
  <div class="banner-sub">
    {proj_badges}
    {total_all:,} issues · {n_rep} reporters · Data fetched: {fetched_at}
  </div>
  <div style="margin-top:12px;">
    <span class="bstat">🐛 {bugs_all} Bugs</span>
    <span class="bstat">⬆️ {impr_all} Improvements</span>
    <span class="bstat">✅ {resolved_all} Resolved</span>
    <span class="bstat">📊 {res_rate}% Resolution Rate</span>
    <span class="bstat">🚫 {blocked_all} Blocked</span>
    {'<span class="bstat">⏱️ Avg Res: ' + str(avg_res_days) + 'd</span>' if avg_res_days else ''}
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# KPI ROW — Combined
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-icon">📋</div>
    <div class="kpi-val">{total_all:,}</div>
    <div class="kpi-lbl">Total Issues</div>
    <div class="kpi-note">{n_rep} active reporters</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">🐛</div>
    <div class="kpi-val">{bugs_all:,}</div>
    <div class="kpi-lbl">Total Bugs</div>
    <div class="kpi-note">{round(bugs_all/total_all*100,1) if total_all else 0}% of all issues</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">⬆️</div>
    <div class="kpi-val">{impr_all:,}</div>
    <div class="kpi-lbl">Improvements</div>
    <div class="kpi-note">{round(impr_all/total_all*100,1) if total_all else 0}% of all issues</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">🔴</div>
    <div class="kpi-val">{open_all:,}</div>
    <div class="kpi-lbl">Still Open (NEW)</div>
    <div class="kpi-note">{round(open_all/total_all*100,1) if total_all else 0}% unresolved</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">✅</div>
    <div class="kpi-val">{res_rate}%</div>
    <div class="kpi-lbl">Resolution Rate</div>
    <div class="kpi-note">{resolved_all} Done / Accepted</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">⏱️</div>
    <div class="kpi-val">{'N/A' if avg_res_days is None else f'{avg_res_days}d'}</div>
    <div class="kpi-lbl">Avg Resolution Time</div>
    <div class="kpi-note">Avg age: {avg_age}d</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# PROJECT-WISE BREAKDOWN CARDS
# ════════════════════════════════════════════════════════════════
if len(PROJECT_KEYS) > 1:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">📁 Project-wise Breakdown</p>', unsafe_allow_html=True)

    proj_cols = st.columns(len(PROJECT_KEYS))
    for i, (proj, col) in enumerate(zip(PROJECT_KEYS, proj_cols)):
        pf = filtered_frames.get(proj, pd.DataFrame())
        pt  = len(pf)
        pb  = int(pf["issue_type"].apply(is_bug).sum()) if pt else 0
        pim = int(pf["issue_type"].apply(is_improvement).sum()) if pt else 0
        pr  = int(pf["status"].apply(is_resolved).sum()) if pt else 0
        prr = round(pr/pt*100, 1) if pt else 0
        po  = int(pf["status"].apply(is_open).sum()) if pt else 0
        pbl = int(pf["status"].apply(is_blocked).sum()) if pt else 0
        prd = pf["resolution_days"].dropna()
        prd_avg = round(prd.mean(), 1) if len(prd) > 0 else None
        pcolor = PROJ_COLORS[i % len(PROJ_COLORS)]
        with col:
            st.markdown(f"""
            <div class="proj-card" style="border-top:4px solid {pcolor};">
              <div class="proj-card-title" style="color:{pcolor};">📁 {proj}</div>
              <div class="proj-stats">
                <div class="pstat">
                  <div class="pstat-val">{pt:,}</div><div class="pstat-lbl">Total</div>
                </div>
                <div class="pstat">
                  <div class="pstat-val" style="color:#ef4444;">{pb}</div><div class="pstat-lbl">Bugs</div>
                </div>
                <div class="pstat">
                  <div class="pstat-val" style="color:#22c55e;">{prr}%</div><div class="pstat-lbl">Resolved</div>
                </div>
                <div class="pstat">
                  <div class="pstat-val" style="color:#f97316;">{po}</div><div class="pstat-lbl">Open</div>
                </div>
                <div class="pstat">
                  <div class="pstat-val" style="color:#dc2626;">{pbl}</div><div class="pstat-lbl">Blocked</div>
                </div>
              </div>
              {'<div style="margin-top:10px;font-size:.74rem;color:#64748b;">⏱️ Avg resolution: <b>' + str(prd_avg) + 'd</b></div>' if prd_avg else ''}
            </div>
            """, unsafe_allow_html=True)

    # Project comparison bar chart
    st.markdown("<br>", unsafe_allow_html=True)
    proj_cmp = []
    for proj in PROJECT_KEYS:
        pf = filtered_frames.get(proj, pd.DataFrame())
        pt = len(pf)
        if pt == 0:
            continue
        proj_cmp.append({
            "Project": proj,
            "Bugs":        int(pf["issue_type"].apply(is_bug).sum()),
            "Improvements":int(pf["issue_type"].apply(is_improvement).sum()),
            "Resolved":    int(pf["status"].apply(is_resolved).sum()),
            "Open":        int(pf["status"].apply(is_open).sum()),
            "Blocked":     int(pf["status"].apply(is_blocked).sum()),
        })
    if proj_cmp:
        cmp_df = pd.DataFrame(proj_cmp)
        metrics = ["Bugs","Improvements","Resolved","Open","Blocked"]
        colors  = ["#ef4444","#3b82f6","#22c55e","#f97316","#dc2626"]
        fig = go.Figure()
        for m, c in zip(metrics, colors):
            fig.add_trace(go.Bar(name=m, x=cmp_df["Project"], y=cmp_df[m],
                                 marker_color=c, marker_line_color="#fff", marker_line_width=1.5,
                                 text=cmp_df[m], textposition="outside",
                                 textfont=dict(size=11, color="#0f172a")))
        fig.update_layout(**B(340), barmode="group", xaxis_title=None,
                          yaxis_title="Count", legend=LEG_H, bargap=0.2, bargroupgap=0.08)
        fig.update_layout(margin=dict(t=55, b=40, l=40, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Choose view scope ─────────────────────────────────────────────────────────
view_tabs_labels = ["🔗 Combined"] + [f"📁 {p}" for p in PROJECT_KEYS]
view_tabs = st.tabs(view_tabs_labels)

def render_dashboard(data, scope_label):
    if data.empty:
        st.warning(f"No data for {scope_label}.")
        return

    r_df     = agg_reporters(data)
    n_r      = len(r_df)
    r_order  = r_df["reporter"].tolist()
    b_h      = max(420, n_r * 48 + 100)
    t_all    = len(data)
    res_all  = int(data["status"].apply(is_resolved).sum())
    rr       = round(res_all / t_all * 100, 1) if t_all else 0

    if r_df.empty:
        st.warning("No reporter data.")
        return

    # ── Smart Insights ────────────────────────────────────────────
    insights = []
    top_reporter = r_df.iloc[0]["reporter"] if len(r_df) else None
    if top_reporter:
        insights.append(f"🏆 <b>{top_reporter}</b> is the top contributor with {int(r_df.iloc[0]['total'])} issues")
    worst_res = r_df[r_df["total"] >= 5].sort_values("res_pct").iloc[0] if len(r_df[r_df["total"]>=5]) else None
    if worst_res is not None:
        insights.append(f"⚠️ <b>{worst_res['reporter']}</b> has the lowest resolution rate ({worst_res['res_pct']:.0f}%)")
    blocked_reps = r_df[r_df["blocked"] > 0]
    if not blocked_reps.empty:
        names = ", ".join(blocked_reps["reporter"].tolist())
        insights.append(f"🚫 Reporters with blocked issues: <b>{names}</b>")
    high_open = r_df[r_df["open_pct"] > 60]
    if not high_open.empty:
        insights.append(f"🔴 <b>{', '.join(high_open['reporter'].tolist())}</b> have >60% issues still open (NEW)")
    avg_age_v = round(data["age_days"].mean(), 1)
    stale = data[data["age_days"] > 90]
    if len(stale):
        insights.append(f"🕰️ {len(stale)} issues are older than 90 days — avg age across all: {avg_age_v}d")

    if insights:
        html = '<div class="insight-box"><div class="insight-title">💡 Smart Insights</div>'
        for ins in insights:
            html += f'<div class="insight-item">• {ins}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # LEADERBOARD
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Reporter Leaderboard</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid;grid-template-columns:200px 60px 80px 150px 150px 80px 80px 80px 1fr;
         gap:10px;padding:0 18px 10px;border-bottom:2px solid #f1f5f9;margin-bottom:6px;">
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;">Reporter</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;text-align:center;">Total</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;text-align:center;">Avg Age</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;">Bug vs Improvement</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;">Resolution</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;text-align:center;">High Prio</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;text-align:center;">Retest Fail</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;text-align:center;">Blocked</div>
      <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;">Status</div>
    </div>
    """, unsafe_allow_html=True)

    for i, (_, r) in enumerate(r_df.iterrows()):
        av_c  = AV[i % len(AV)]
        bug_w = r["bugs"]   / r["total"] * 100 if r["total"] else 0
        imp_w = r["improv"] / r["total"] * 100 if r["total"] else 0
        res_w = r["res_pct"]
        avg_a = f"{r['avg_age']:.0f}d" if pd.notna(r["avg_age"]) else "—"
        age_color = "#ef4444" if (pd.notna(r["avg_age"]) and r["avg_age"] > 90) else \
                    "#f97316" if (pd.notna(r["avg_age"]) and r["avg_age"] > 30) else "#22c55e"
        if r["res_pct"] >= 40:
            badge = '<span class="badge" style="background:#dcfce7;color:#16a34a;">✅ Good Resolver</span>'
        elif r["blocked"] > 0:
            badge = '<span class="badge" style="background:#fee2e2;color:#dc2626;">🚫 Blocked</span>'
        elif r["open_pct"] > 80:
            badge = '<span class="badge" style="background:#fef3c7;color:#b45309;">⚠️ High Open</span>'
        elif r["retest_fail"] > 5:
            badge = '<span class="badge" style="background:#fce7f3;color:#be185d;">🔁 High Retest</span>'
        else:
            badge = '<span class="badge" style="background:#eff6ff;color:#2563eb;">🔄 Active</span>'
        st.markdown(f"""
        <div class="rep-row">
          <div style="display:flex;align-items:center;gap:9px;">
            <div class="avatar" style="background:{av_c};">{initials(r['reporter'])}</div>
            <div>
              <div class="rep-name">{r['reporter']}</div>
              <div class="rep-sub">{int(r['new_open'])} open</div>
            </div>
          </div>
          <div class="stat-center">
            <div style="font-size:1.45rem;font-weight:900;color:#2563eb;">{int(r['total'])}</div>
          </div>
          <div class="stat-center">
            <div class="stat-val" style="color:{age_color};">{avg_a}</div>
            <div class="stat-lbl">avg age</div>
          </div>
          <div>
            <div class="mbar-lbl">
              <span style="color:#ef4444;font-weight:700;">🐛 {int(r['bugs'])}</span>
              <span style="color:#3b82f6;font-weight:700;">⬆️ {int(r['improv'])}</span>
            </div>
            <div class="mbar-track">
              <div style="width:{bug_w:.1f}%;background:#ef4444;height:7px;"></div>
              <div style="width:{imp_w:.1f}%;background:#3b82f6;height:7px;"></div>
            </div>
          </div>
          <div>
            <div class="mbar-lbl">
              <span style="color:#10b981;font-weight:700;">{int(r['resolved'])} resolved</span>
              <span style="color:#64748b;">{r['res_pct']:.0f}%</span>
            </div>
            <div style="background:#f1f5f9;border-radius:6px;height:7px;overflow:hidden;">
              <div style="width:{res_w:.1f}%;background:#10b981;height:7px;border-radius:6px;"></div>
            </div>
          </div>
          <div class="stat-center">
            <div class="stat-val" style="color:#f97316;">{int(r['high_prio'])}</div>
            <div class="stat-lbl">high prio</div>
          </div>
          <div class="stat-center">
            <div class="stat-val" style="color:#ef4444;">{int(r['retest_fail'])}</div>
            <div class="stat-lbl">retest fail</div>
          </div>
          <div class="stat-center">
            <div class="stat-val" style="color:{'#dc2626' if r['blocked']>0 else '#94a3b8'};">{int(r['blocked'])}</div>
            <div class="stat-lbl">blocked</div>
          </div>
          <div>{badge}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # BUG vs IMPROVEMENT
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">🐛 Bug vs ⬆️ Improvement — Breakdown</p>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["  Grouped Bar  ", "  Per-Reporter Progress Bars  ", "  Status × Type Heatmap  "])

    with t1:
        max_y = max(int(r_df["bugs"].max()), int(r_df["improv"].max())) if not r_df.empty else 10
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Bug", x=r_df["reporter"], y=r_df["bugs"],
                             marker_color="#ef4444", marker_line_color="#fff", marker_line_width=1.5,
                             text=r_df["bugs"].astype(int), textposition="outside",
                             textfont=dict(size=11, color="#0f172a")))
        fig.add_trace(go.Bar(name="Improvement", x=r_df["reporter"], y=r_df["improv"],
                             marker_color="#3b82f6", marker_line_color="#fff", marker_line_width=1.5,
                             text=r_df["improv"].astype(int), textposition="outside",
                             textfont=dict(size=11, color="#0f172a")))
        fig.update_layout(**B(420), barmode="group", xaxis_title=None, yaxis_title="Issues",
                          bargap=0.25, bargroupgap=0.1, legend=LEG_H)
        fig.update_layout(margin=dict(t=50, b=90, l=30, r=20))
        fig.update_yaxes(range=[0, max_y * 1.25])
        fig.update_xaxes(tickangle=-20, tickfont=dict(size=11, color="#1e293b"))
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        c_bug, c_imp = st.columns(2)
        for col_obj, field, label, color, icon in [
            (c_bug, "bugs",   "Bug",         "#ef4444", "🐛"),
            (c_imp, "improv", "Improvement", "#3b82f6", "⬆️"),
        ]:
            with col_obj:
                total_t = int(r_df[field].sum())
                max_v   = r_df[field].max()
                st.markdown(f"""
                <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;padding:18px;">
                  <div style="font-size:.95rem;font-weight:800;color:{color};margin-bottom:16px;">
                    {icon} {label}
                    <span style="color:#94a3b8;font-size:.78rem;font-weight:500;margin-left:6px;">({total_t} total)</span>
                  </div>
                """, unsafe_allow_html=True)
                for _, r in r_df.sort_values(field, ascending=False).iterrows():
                    pct   = (r[field]/max_v*100) if max_v else 0
                    share = round(r[field]/total_t*100, 1) if total_t else 0
                    av_c  = AV[list(r_df["reporter"]).index(r["reporter"]) % len(AV)]
                    st.markdown(f"""
                    <div class="pbar">
                      <div class="pbar-head">
                        <div style="display:flex;align-items:center;gap:7px;">
                          <div style="width:8px;height:8px;border-radius:50%;background:{av_c};flex-shrink:0;"></div>
                          <span class="pbar-name">{r['reporter']}</span>
                        </div>
                        <span class="pbar-val" style="color:{color};">{int(r[field])}
                          <span style="color:#94a3b8;font-weight:500;font-size:.7rem;">({share}%)</span>
                        </span>
                      </div>
                      <div class="pbar-track">
                        <div class="pbar-fill" style="width:{pct:.1f}%;background:{color};opacity:.82;"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        focus = data[data["issue_type"].apply(lambda x: is_bug(x) or is_improvement(x))]
        if not focus.empty:
            piv  = focus.groupby(["reporter","issue_type","status"]).size().reset_index(name="Count")
            piv2 = piv.pivot_table(index=["reporter","issue_type"], columns="status",
                                   values="Count", fill_value=0).reset_index()
            stat_cols = [c for c in piv2.columns if c not in ["reporter","issue_type"]]
            heat_data = piv2.set_index(["reporter","issue_type"])[stat_cols].astype(int)
            heat_h    = max(480, len(heat_data) * 34 + 120)
            fig = px.imshow(heat_data, text_auto=True, aspect="auto",
                            color_continuous_scale=[[0,"#f0f9ff"],[0.01,"#bfdbfe"],[1,"#1d4ed8"]], zmin=0)
            fig.update_traces(textfont=dict(size=11, color="#0f172a"))
            fig.update_layout(**B(heat_h), coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
            fig.update_layout(margin=dict(t=20, b=90, l=200, r=20))
            fig.update_xaxes(tickangle=-35, tickfont=dict(size=11, color="#1e293b"), side="bottom")
            fig.update_yaxes(tickfont=dict(size=11, color="#1e293b"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Bug/Improvement data to display.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # STATUS + PRIORITY DISTRIBUTION
    # ════════════════════════════════════════════════════════════════
    col_stat, col_prio = st.columns(2)
    with col_stat:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">Status Distribution</p>', unsafe_allow_html=True)
        sg  = data.groupby(["reporter","status"]).size().reset_index(name="Count")
        fig = px.bar(sg, y="reporter", x="Count", color="status",
                     color_discrete_map=SC, barmode="stack", orientation="h",
                     category_orders={"reporter": r_order})
        fig.update_traces(marker_line_color="#fff", marker_line_width=0.6)
        fig.update_layout(**B(b_h), xaxis_title="Issues", yaxis_title=None, legend=LEG_H)
        fig.update_layout(margin=dict(t=60, b=40, l=160, r=20))
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color="#1e293b"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_prio:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">Priority Distribution</p>', unsafe_allow_html=True)
        pg       = data.groupby(["reporter","priority"]).size().reset_index(name="Count")
        prio_ord = ["Highest","High","Medium","Low","Lowest"]
        fig = px.bar(pg, y="reporter", x="Count", color="priority",
                     color_discrete_map=PC_COL, barmode="stack", orientation="h",
                     category_orders={"reporter": r_order, "priority": prio_ord})
        fig.update_traces(marker_line_color="#fff", marker_line_width=0.6)
        fig.update_layout(**B(b_h), xaxis_title="Issues", yaxis_title=None, legend=LEG_H)
        fig.update_layout(margin=dict(t=60, b=40, l=160, r=20))
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color="#1e293b"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # ISSUE AGE BUCKETS + AVG RESOLUTION TIME
    # ════════════════════════════════════════════════════════════════
    col_age, col_res = st.columns(2)
    with col_age:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">📅 Issue Age Buckets (Open Issues)</p>', unsafe_allow_html=True)
        open_issues = data[~data["status"].apply(is_resolved)]
        if not open_issues.empty:
            age_grp = open_issues.groupby("age_bucket").size().reset_index(name="Count")
            age_grp["age_bucket"] = age_grp["age_bucket"].astype(str)
            age_colors = {"0–7 days":"#22c55e","8–30 days":"#84cc16",
                          "31–90 days":"#eab308","91–180 days":"#f97316","180+ days":"#ef4444"}
            fig = go.Figure(go.Bar(
                x=age_grp["age_bucket"], y=age_grp["Count"],
                marker_color=[age_colors.get(b,"#94a3b8") for b in age_grp["age_bucket"]],
                marker_line_color="#fff", marker_line_width=1.5,
                text=age_grp["Count"], textposition="outside",
                textfont=dict(size=12, color="#0f172a"),
            ))
            fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Open Issues", showlegend=False)
            fig.update_layout(margin=dict(t=30, b=30, l=50, r=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No open issues.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_res:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">⏱️ Avg Resolution Time per Reporter</p>', unsafe_allow_html=True)
        res_time = (data.dropna(subset=["resolution_days"])
                       .groupby("reporter")["resolution_days"]
                       .mean().round(1).reset_index()
                       .sort_values("resolution_days"))
        if not res_time.empty:
            max_rt = res_time["resolution_days"].max()
            fig = go.Figure(go.Bar(
                x=res_time["resolution_days"], y=res_time["reporter"], orientation="h",
                marker=dict(
                    color=res_time["resolution_days"],
                    colorscale=[[0,"#86efac"],[0.5,"#fde68a"],[1,"#fca5a5"]],
                    line_color="#fff", line_width=1.5,
                ),
                text=res_time["resolution_days"].apply(lambda v: f"{v:.1f}d"),
                textposition="outside",
                textfont=dict(size=11, color="#0f172a"),
            ))
            fig.update_layout(**B(300), xaxis_title="Days", yaxis_title=None, showlegend=False)
            fig.update_layout(margin=dict(t=20, b=30, l=155, r=60))
            fig.update_xaxes(range=[0, max_rt * 1.25])
            fig.update_yaxes(tickfont=dict(size=11, color="#1e293b"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No resolved issues with resolution dates.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # WEEKLY VELOCITY + MONTHLY TREND
    # ════════════════════════════════════════════════════════════════
    col_vel, col_trend = st.columns(2)
    with col_vel:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">📈 Weekly Issue Velocity (Last 12 Weeks)</p>', unsafe_allow_html=True)
        weekly = (data.groupby("week_period").size().reset_index(name="Count"))
        weekly["week_str"] = weekly["week_period"].astype(str)
        weekly = weekly.sort_values("week_str").tail(12)
        if not weekly.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=weekly["week_str"], y=weekly["Count"], mode="lines+markers",
                line=dict(color="#2563eb", width=2.5), marker=dict(size=8, color="#2563eb",
                line_color="#fff", line_width=2), fill="tozeroy",
                fillcolor="rgba(37,99,235,0.08)",
                hovertemplate="<b>Week %{x}</b><br>%{y} issues<extra></extra>",
            ))
            avg_v = weekly["Count"].mean()
            fig.add_hline(y=avg_v, line_dash="dash", line_color="#94a3b8", line_width=1,
                          annotation_text=f"Avg: {avg_v:.1f}", annotation_position="right")
            fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Issues", showlegend=False)
            fig.update_layout(margin=dict(t=30, b=40, l=50, r=60))
            fig.update_xaxes(tickangle=-30, tickfont=dict(size=10, color="#1e293b"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_trend:
        st.markdown('<div class="wcard">', unsafe_allow_html=True)
        st.markdown('<p class="stitle">📅 Monthly Trend — Top 5 Reporters</p>', unsafe_allow_html=True)
        top5  = r_df.head(5)["reporter"].tolist()
        trend = (data[data["reporter"].isin(top5)]
                 .groupby(["month_period","reporter"]).size().reset_index(name="Count"))
        trend["month_period"] = trend["month_period"].astype(str)
        trend = trend.sort_values("month_period")
        if not trend.empty:
            fig = px.line(trend, x="month_period", y="Count", color="reporter",
                          markers=True, line_shape="spline", color_discrete_sequence=AV)
            fig.update_traces(line_width=2.5, marker_size=7,
                              marker_line_color="#fff", marker_line_width=2)
            fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Issues", legend=LEG_H)
            fig.update_layout(margin=dict(t=55, b=50, l=50, r=20))
            fig.update_xaxes(tickangle=-25, tickfont=dict(size=10, color="#1e293b"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # RESOLUTION RATE RANKING
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Resolution Rate Ranking</p>', unsafe_allow_html=True)
    res_rank = r_df.sort_values("res_pct", ascending=True)
    fig = go.Figure(go.Bar(
        x=res_rank["res_pct"], y=res_rank["reporter"], orientation="h",
        marker=dict(
            color=res_rank["res_pct"],
            colorscale=[[0,"#fecaca"],[0.3,"#fde68a"],[1,"#86efac"]],
            line_color="#fff", line_width=1.5,
        ),
        text=res_rank.apply(lambda r: f"{r['res_pct']:.0f}%  ({int(r['resolved'])}/{int(r['total'])})", axis=1),
        textposition="outside",
        textfont=dict(size=11, color="#0f172a"),
    ))
    fig.update_layout(**B(max(340, n_r*44+80)), xaxis_title="Resolution %",
                      yaxis_title=None, showlegend=False)
    fig.update_layout(margin=dict(t=20, b=40, l=175, r=90))
    fig.update_xaxes(range=[0, 125], ticksuffix="%", tickfont=dict(size=11, color="#475569"))
    fig.update_yaxes(tickfont=dict(size=12, color="#1e293b"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # REPORTER SPOTLIGHT
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">🔎 Reporter Spotlight — Deep Dive</p>', unsafe_allow_html=True)
    chosen = st.selectbox("Pick reporter", r_df["reporter"].tolist(),
                          key=f"spotlight_{scope_label}", label_visibility="collapsed")
    rdf_s  = data[data["reporter"] == chosen]
    rs     = r_df[r_df["reporter"] == chosen].iloc[0]
    av_idx = list(r_df["reporter"]).index(chosen)
    av_c   = AV[av_idx % len(AV)]

    retest_badge = (
        f'<span style="background:#fef3c7;color:#92400e;border:1px solid #fde68a;'
        f'border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">'
        f'&#x1F501; {int(rs["retest_fail"])} Re-Test Fail</span>'
        if rs["retest_fail"] > 0 else ""
    )
    avg_res_str = f"{rs['avg_res_days']:.1f}d" if pd.notna(rs.get("avg_res_days")) else "—"
    spotlight_html = f"""
    <div style="font-family:Inter,sans-serif;display:flex;align-items:center;gap:16px;
         background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;
         padding:18px 22px;margin-bottom:4px;flex-wrap:wrap;">
      <div style="width:54px;height:54px;border-radius:50%;background:{av_c};flex-shrink:0;
           display:flex;align-items:center;justify-content:center;
           font-size:1.2rem;font-weight:900;color:#fff;">{initials(chosen)}</div>
      <div style="flex:1;min-width:200px;">
        <div style="font-size:1.1rem;font-weight:800;color:#0f172a;">{chosen}</div>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
          <span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;
               border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">&#x1F41B; {int(rs['bugs'])} Bugs</span>
          <span style="background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe;
               border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">&#x2B06;&#xFE0F; {int(rs['improv'])} Improvements</span>
          <span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;
               border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">&#x2705; {int(rs['resolved'])} Resolved ({rs['res_pct']:.0f}%)</span>
          <span style="background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;
               border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">&#x1F525; {int(rs['high_prio'])} High Prio</span>
          <span style="background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;
               border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">⏱️ Avg Res: {avg_res_str}</span>
          {retest_badge}
        </div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:2.4rem;font-weight:900;color:{av_c};">{int(rs['total'])}</div>
        <div style="font-size:.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;">Total Issues</div>
      </div>
    </div>
    """
    components.html(spotlight_html, height=120)

    sp1, sp2, sp3 = st.columns(3)
    with sp1:
        sc2 = rdf_s["status"].value_counts().reset_index()
        sc2.columns = ["Status","Count"]
        fig = go.Figure(go.Pie(
            labels=sc2["Status"], values=sc2["Count"], hole=0.52,
            marker=dict(colors=[SC.get(s,"#94a3b8") for s in sc2["Status"]],
                        line=dict(color="#fff", width=2)),
            textposition="inside", textinfo="percent",
            textfont=dict(size=11, color="#fff"),
            hovertemplate="<b>%{label}</b><br>%{value} issues (%{percent})<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG, height=320,
            margin=dict(t=20, b=10, l=10, r=130),
            showlegend=True, legend=LEG_V,
            font=dict(color=TXT, family="Inter,sans-serif", size=12),
            annotations=[dict(text=f"<b>{int(rs['total'])}</b>",
                              x=0.38, y=0.5, showarrow=False,
                              font=dict(size=16, color=TXT))],
        )
        st.markdown("**Status Breakdown**")
        st.plotly_chart(fig, use_container_width=True)

    with sp2:
        pc2 = rdf_s["priority"].value_counts().reset_index()
        pc2.columns = ["Priority","Count"]
        pc2["Priority"] = pd.Categorical(pc2["Priority"],
            categories=["Highest","High","Medium","Low","Lowest"], ordered=True)
        pc2 = pc2.sort_values("Priority").dropna(subset=["Priority"])
        mx  = int(pc2["Count"].max()) if len(pc2) else 10
        fig = go.Figure(go.Bar(
            x=pc2["Priority"], y=pc2["Count"],
            marker_color=[PC_COL.get(p,"#94a3b8") for p in pc2["Priority"]],
            marker_line_color="#fff", marker_line_width=1.5,
            text=pc2["Count"], textposition="outside",
            textfont=dict(size=12, color="#0f172a"),
        ))
        fig.update_layout(**B(320), xaxis_title=None, yaxis_title="Issues", showlegend=False, bargap=0.3)
        fig.update_layout(margin=dict(t=30, b=30, l=40, r=20))
        fig.update_yaxes(range=[0, mx*1.3])
        st.markdown("**Priority Breakdown**")
        st.plotly_chart(fig, use_container_width=True)

    with sp3:
        # Monthly trend for selected reporter
        rep_monthly = (rdf_s.groupby("month_period").size()
                            .reset_index(name="Count"))
        rep_monthly["month_str"] = rep_monthly["month_period"].astype(str)
        rep_monthly = rep_monthly.sort_values("month_str")
        fig = go.Figure(go.Scatter(
            x=rep_monthly["month_str"], y=rep_monthly["Count"],
            mode="lines+markers", line=dict(color=av_c, width=2.5),
            marker=dict(size=8, color=av_c, line_color="#fff", line_width=2),
            fill="tozeroy", fillcolor=f"rgba({int(av_c[1:3],16)},{int(av_c[3:5],16)},{int(av_c[5:7],16)},0.1)",
        ))
        fig.update_layout(**B(320), xaxis_title=None, yaxis_title="Issues", showlegend=False)
        fig.update_layout(margin=dict(t=30, b=50, l=40, r=20))
        fig.update_xaxes(tickangle=-30, tickfont=dict(size=9, color="#1e293b"))
        st.markdown("**Monthly Activity**")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # DATA TABLE
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Issue Data Explorer</p>', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([3,1,1,1])
    with fc1:
        srch = st.text_input("s","", placeholder="🔎  Search summary or issue key…",
                             label_visibility="collapsed", key=f"srch_{scope_label}")
    with fc2:
        tf = st.selectbox("tf",["All Types"]+sorted(data["issue_type"].dropna().unique().tolist()),
                          label_visibility="collapsed", key=f"tf_{scope_label}")
    with fc3:
        sf = st.selectbox("sf",["All Statuses"]+sorted(data["status"].dropna().unique().tolist()),
                          label_visibility="collapsed", key=f"sf_{scope_label}")
    with fc4:
        rf = st.selectbox("rf",["All Reporters"]+sorted(data["reporter"].dropna().unique().tolist()),
                          label_visibility="collapsed", key=f"rf_{scope_label}")

    cols_show = ["issue_key","project","reporter","issue_type","summary","status","priority","assignee","age_days","created"]
    tbl = data[cols_show].copy()
    if srch: tbl = tbl[tbl["summary"].fillna("").str.contains(srch,case=False) |
                       tbl["issue_key"].fillna("").str.contains(srch,case=False)]
    if tf != "All Types":     tbl = tbl[tbl["issue_type"]==tf]
    if sf != "All Statuses":  tbl = tbl[tbl["status"]==sf]
    if rf != "All Reporters": tbl = tbl[tbl["reporter"]==rf]
    tbl.columns = ["Key","Project","Reporter","Type","Summary","Status","Priority","Assignee","Age (days)","Created"]
    st.dataframe(tbl, use_container_width=True, height=380,
                 column_config={
                     "Key":       st.column_config.TextColumn(width="small"),
                     "Project":   st.column_config.TextColumn(width="small"),
                     "Reporter":  st.column_config.TextColumn(width="medium"),
                     "Type":      st.column_config.TextColumn(width="small"),
                     "Summary":   st.column_config.TextColumn(width="large"),
                     "Status":    st.column_config.TextColumn(width="medium"),
                     "Priority":  st.column_config.TextColumn(width="small"),
                     "Age (days)":st.column_config.NumberColumn(width="small"),
                 })
    st.caption(f"Showing {len(tbl):,} of {len(data):,} issues")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Render tabs ───────────────────────────────────────────────────────────────
with view_tabs[0]:
    render_dashboard(df, "combined")

for i, proj in enumerate(PROJECT_KEYS):
    with view_tabs[i + 1]:
        pf = filtered_frames.get(proj, pd.DataFrame())
        render_dashboard(pf, proj)
