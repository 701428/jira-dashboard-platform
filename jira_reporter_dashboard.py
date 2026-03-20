import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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
.kpi-row{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px;}
.kpi{background:#fff;border-radius:16px;padding:20px 20px 16px;
  border:1px solid #e2e8f0;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.kpi-icon{font-size:1.5rem;margin-bottom:7px;}
.kpi-val{font-size:2rem;font-weight:900;color:#0f172a;line-height:1;}
.kpi-lbl{font-size:.7rem;font-weight:700;color:#94a3b8;text-transform:uppercase;
  letter-spacing:.09em;margin-top:5px;}
.kpi-note{font-size:.72rem;color:#64748b;margin-top:3px;}
.stitle{font-size:.77rem;font-weight:800;color:#64748b;text-transform:uppercase;
  letter-spacing:.1em;border-left:3px solid #2563eb;padding-left:9px;margin:0 0 14px;}
.wcard{background:#fff;border:1px solid #e2e8f0;border-radius:16px;
  padding:22px 22px 14px;margin-bottom:20px;box-shadow:0 1px 6px rgba(0,0,0,.05);}
.rep-row{background:#fff;border:1px solid #e2e8f0;border-radius:13px;
  padding:15px 18px;margin-bottom:9px;display:grid;
  grid-template-columns:200px 70px 150px 150px 90px 90px 90px 1fr;
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
      "Rejected":"#94a3b8","BLOCKED":"#dc2626"}
PC = {"Highest":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e","Lowest":"#3b82f6"}
TC = {"Bug":"#ef4444","Improvement":"#3b82f6","Task":"#8b5cf6","Epic":"#f97316",
      "Story":"#22c55e","New Feature":"#06b6d4","Sub-task":"#eab308","Initiative":"#ec4899"}
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

# ── Jira config (sidebar) ─────────────────────────────────────────────────────
_raw_secrets = st.secrets.get("jira", {})
_s = dict(_raw_secrets) if _raw_secrets else {}
with st.sidebar:
    st.markdown("## ⚙️ Jira Connection")
    JIRA_URL     = st.text_input("Jira URL",    value=_s.get("url",     "https://grampower.atlassian.net"), key="jurl")
    JIRA_EMAIL   = st.text_input("Email",       value=_s.get("email",   "lalit.tak@polarisgrids.com"),      key="jemail")
    JIRA_TOKEN   = st.text_input("API Token",   value=_s.get("token",   ""),                                type="password", key="jtoken")
    JIRA_PROJECT = st.text_input("Project Key", value=_s.get("project", "PC"),                              key="jproject")
    connect_btn  = st.button("🔗 Connect", use_container_width=True)
    st.markdown("---")

# ── Jira data loader ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Fetching issues from Jira…")
def load_jira_data(url, email, token, project):
    auth    = (email, token)
    headers = {"Accept": "application/json"}
    fields  = "summary,status,priority,assignee,reporter,issuetype,created"
    issues  = []
    next_token = None

    while True:
        reporter_filter = (
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
        payload = {
            "jql": f"project={project} AND {reporter_filter} ORDER BY created DESC",
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
                "issue_key":  issue["key"],
                "summary":    f.get("summary", ""),
                "issue_type": (f.get("issuetype") or {}).get("name", ""),
                "status":     (f.get("status")    or {}).get("name", ""),
                "priority":   (f.get("priority")  or {}).get("name", ""),
                "assignee":   (f.get("assignee")  or {}).get("displayName", "Unassigned"),
                "reporter":   (f.get("reporter")  or {}).get("displayName", "Unknown"),
                "created":    f.get("created", ""),
            })

        if data.get("isLast", True) or not data.get("nextPageToken"):
            break
        next_token = data["nextPageToken"]

    df = pd.DataFrame(issues)
    if df.empty:
        return df
    df["issue_type"]   = df["issue_type"].str.strip()
    df = df[df["reporter"].notna() & (df["reporter"].str.strip() != "")]
    df["created_dt"]   = pd.to_datetime(df["created"], errors="coerce", utc=True)
    df["created_dt"]   = df["created_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["month_period"] = df["created_dt"].dt.to_period("M")
    df.attrs["fetched_at"] = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    return df

# ── Load ──────────────────────────────────────────────────────────────────────
if not JIRA_TOKEN:
    st.info("Enter your Jira API Token in the sidebar and click **Connect**."); st.stop()

# Clear cache BEFORE calling load — triggered by Connect or Refresh on previous run
if connect_btn or st.session_state.pop("do_refresh", False):
    load_jira_data.clear()

try:
    raw = load_jira_data(JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, JIRA_PROJECT)
except Exception as e:
    st.error(f"Jira Error: {e}"); st.stop()

if raw.empty:
    st.warning("No issues found."); st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
all_rep  = sorted(raw["reporter"].dropna().unique())
all_type = sorted(raw["issue_type"].dropna().unique())
all_stat = sorted(raw["status"].dropna().unique())
all_prio = sorted(raw["priority"].dropna().unique())
sel_rep  = st.sidebar.multiselect("Reporter",   all_rep,  default=all_rep)
sel_type = st.sidebar.multiselect("Issue Type", all_type, default=all_type)
sel_stat = st.sidebar.multiselect("Status",     all_stat, default=all_stat)
sel_prio = st.sidebar.multiselect("Priority",   all_prio, default=all_prio)
if raw["created_dt"].notna().any():
    mn = raw["created_dt"].min().date(); mx = raw["created_dt"].max().date()
    dr = st.sidebar.date_input("Date Range", (mn, mx), min_value=mn, max_value=mx)
else:
    dr = None
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh"):
    st.session_state["do_refresh"] = True
    st.rerun()

df = raw.copy()
if sel_rep:  df = df[df["reporter"].isin(sel_rep)]
if sel_type: df = df[df["issue_type"].isin(sel_type)]
if sel_stat: df = df[df["status"].isin(sel_stat)]
if sel_prio: df = df[df["priority"].isin(sel_prio)]
if dr and len(dr)==2:
    df = df[(df["created_dt"].dt.date>=dr[0])&(df["created_dt"].dt.date<=dr[1])]

# ── Aggregate ─────────────────────────────────────────────────────────────────
rep_df = (
    df.groupby("reporter").agg(
        total      =("issue_key","count"),
        bugs       =("issue_type", lambda x: (x=="Bug").sum()),
        improv     =("issue_type", lambda x: (x=="Improvement").sum()),
        resolved   =("status",     lambda x: x.isin(["Done","ACCEPTED"]).sum()),
        new_open   =("status",     lambda x: (x=="NEW").sum()),
        retest_fail=("status",     lambda x: (x=="RE-TEST FAIL").sum()),
        blocked    =("status",     lambda x: (x=="BLOCKED").sum()),
        high_prio  =("priority",   lambda x: x.isin(["Highest","High"]).sum()),
    ).reset_index().sort_values("total", ascending=False)
)
rep_df["res_pct"]  = (rep_df["resolved"]/rep_df["total"]*100).round(1)
rep_df["open_pct"] = (rep_df["new_open"] /rep_df["total"]*100).round(1)
n_rep     = len(rep_df)
rep_order = rep_df["reporter"].tolist()
bar_h     = max(420, n_rep * 48 + 100)

total_all    = len(df)
resolved_all = int(df["status"].isin(["Done","ACCEPTED"]).sum())
res_rate     = round(resolved_all/total_all*100,1) if total_all else 0

# ════════════════════════════════════════════════════════════════
# BANNER
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="banner">
  <div class="banner-title">👤 Reporter Analytics Dashboard</div>
  <div class="banner-sub">
    {total_all:,} issues · {n_rep} reporters ·
    Project: <b>{JIRA_PROJECT.upper()}</b> ·
    Data fetched: {raw.attrs.get('fetched_at', 'unknown')}
  </div>
  <div style="margin-top:12px;">
    <span class="bstat">🐛 {int(df['issue_type'].eq('Bug').sum())} Bugs</span>
    <span class="bstat">⬆️ {int(df['issue_type'].eq('Improvement').sum())} Improvements</span>
    <span class="bstat">✅ {resolved_all} Resolved</span>
    <span class="bstat">📊 {res_rate}% Resolution Rate</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════════════════
bugs_all = int(df['issue_type'].eq('Bug').sum())
impr_all = int(df['issue_type'].eq('Improvement').sum())
open_all = int(df['status'].eq('NEW').sum())
high_all = int(df['priority'].isin(['Highest','High']).sum())

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
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 1 — Reporter Leaderboard
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Reporter Leaderboard</p>', unsafe_allow_html=True)
st.markdown("""
<div style="display:grid;grid-template-columns:200px 70px 150px 150px 90px 90px 90px 1fr;
     gap:10px;padding:0 18px 10px;border-bottom:2px solid #f1f5f9;margin-bottom:6px;">
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;">Reporter</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;text-align:center;">Total</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;">Bug vs Improvement</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;">Resolution</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;text-align:center;">High Prio</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;text-align:center;">Retest Fail</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;text-align:center;">Blocked</div>
  <div style="font-size:.68rem;font-weight:800;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;">Status</div>
</div>
""", unsafe_allow_html=True)

for i, (_, r) in enumerate(rep_df.iterrows()):
    av_c  = AV[i % len(AV)]
    bug_w = r["bugs"]   / r["total"] * 100 if r["total"] else 0
    imp_w = r["improv"] / r["total"] * 100 if r["total"] else 0
    res_w = r["res_pct"]
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
# SECTION 2 — Bug vs Improvement
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">🐛 Bug vs ⬆️ Improvement — Detailed Breakdown</p>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["  Grouped Bar  ", "  Per-Reporter Progress Bars  ", "  Status × Type Heatmap  "])

with t1:
    fig = go.Figure()
    max_y = max(int(rep_df["bugs"].max()), int(rep_df["improv"].max()))
    fig.add_trace(go.Bar(
        name="Bug", x=rep_df["reporter"], y=rep_df["bugs"],
        marker_color="#ef4444", marker_line_color="#fff", marker_line_width=1.5,
        text=rep_df["bugs"].astype(int), textposition="outside",
        textfont=dict(size=11, color="#0f172a"),
    ))
    fig.add_trace(go.Bar(
        name="Improvement", x=rep_df["reporter"], y=rep_df["improv"],
        marker_color="#3b82f6", marker_line_color="#fff", marker_line_width=1.5,
        text=rep_df["improv"].astype(int), textposition="outside",
        textfont=dict(size=11, color="#0f172a"),
    ))
    fig.update_layout(**B(420), barmode="group",
                      xaxis_title=None, yaxis_title="Number of Issues",
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
            total_t = int(rep_df[field].sum())
            max_v   = rep_df[field].max()
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;padding:18px;">
              <div style="font-size:.95rem;font-weight:800;color:{color};margin-bottom:16px;">
                {icon} {label}
                <span style="color:#94a3b8;font-size:.78rem;font-weight:500;margin-left:6px;">({total_t} total)</span>
              </div>
            """, unsafe_allow_html=True)
            for ii, (_, r) in enumerate(rep_df.sort_values(field, ascending=False).iterrows()):
                pct   = (r[field]/max_v*100) if max_v else 0
                share = round(r[field]/total_t*100, 1) if total_t else 0
                av_c  = AV[list(rep_df["reporter"]).index(r["reporter"]) % len(AV)]
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
    focus = df[df["issue_type"].isin(["Bug","Improvement"])]
    piv   = focus.groupby(["reporter","issue_type","status"]).size().reset_index(name="Count")
    piv2  = piv.pivot_table(index=["reporter","issue_type"], columns="status",
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

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 3 — Status Distribution
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Status Distribution per Reporter</p>', unsafe_allow_html=True)
sg  = df.groupby(["reporter","status"]).size().reset_index(name="Count")
fig = px.bar(sg, y="reporter", x="Count", color="status",
             color_discrete_map=SC, barmode="stack", orientation="h",
             category_orders={"reporter": rep_order})
fig.update_traces(marker_line_color="#fff", marker_line_width=0.6)
fig.update_layout(**B(bar_h), xaxis_title="Number of Issues", yaxis_title=None, legend=LEG_H)
fig.update_layout(margin=dict(t=60, b=40, l=175, r=30))
fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#1e293b"))
fig.update_xaxes(tickfont=dict(size=11, color="#475569"))
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 4 — Priority Distribution
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Priority Distribution per Reporter</p>', unsafe_allow_html=True)
pg       = df.groupby(["reporter","priority"]).size().reset_index(name="Count")
prio_ord = ["Highest","High","Medium","Low","Lowest"]
fig = px.bar(pg, y="reporter", x="Count", color="priority",
             color_discrete_map=PC, barmode="stack", orientation="h",
             category_orders={"reporter": rep_order, "priority": prio_ord})
fig.update_traces(marker_line_color="#fff", marker_line_width=0.6)
fig.update_layout(**B(bar_h), xaxis_title="Number of Issues", yaxis_title=None, legend=LEG_H)
fig.update_layout(margin=dict(t=60, b=40, l=175, r=30))
fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#1e293b"))
fig.update_xaxes(tickfont=dict(size=11, color="#475569"))
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 5 — Monthly Trend
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Monthly Trend — Issues Reported (Top 5 Reporters)</p>', unsafe_allow_html=True)
top5  = rep_df.head(5)["reporter"].tolist()
trend = (df[df["reporter"].isin(top5)]
         .groupby(["month_period","reporter"]).size()
         .reset_index(name="Count"))
trend["month_period"] = trend["month_period"].astype(str)
trend = trend.sort_values("month_period")
fig = px.line(trend, x="month_period", y="Count", color="reporter",
              markers=True, line_shape="spline", color_discrete_sequence=AV)
fig.update_traces(line_width=2.5, marker_size=8,
                  marker_line_color="#fff", marker_line_width=2)
fig.update_layout(**B(360), xaxis_title=None, yaxis_title="Issues Reported", legend=LEG_H)
fig.update_layout(margin=dict(t=55, b=60, l=60, r=20))
fig.update_xaxes(tickangle=-25, tickfont=dict(size=11, color="#1e293b"))
fig.update_yaxes(tickfont=dict(size=11, color="#475569"))
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 6 — Resolution Rate
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Resolution Rate Ranking</p>', unsafe_allow_html=True)
res_rank = rep_df.sort_values("res_pct", ascending=True)
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
fig.update_layout(**B(max(360, n_rep*44+80)), xaxis_title="Resolution %",
                  yaxis_title=None, showlegend=False)
fig.update_layout(margin=dict(t=20, b=40, l=175, r=80))
fig.update_xaxes(range=[0, 120], ticksuffix="%", tickfont=dict(size=11, color="#475569"))
fig.update_yaxes(tickfont=dict(size=12, color="#1e293b"))
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 7 — Reporter Spotlight
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">🔎 Reporter Spotlight — Deep Dive</p>', unsafe_allow_html=True)

chosen = st.selectbox("Pick reporter", rep_df["reporter"].tolist(), label_visibility="collapsed")
rdf_s  = df[df["reporter"] == chosen]
rs     = rep_df[rep_df["reporter"] == chosen].iloc[0]
av_idx = list(rep_df["reporter"]).index(chosen)
av_c   = AV[av_idx % len(AV)]

retest_badge = (
    f'<span style="background:#fef3c7;color:#92400e;border:1px solid #fde68a;'
    f'border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">'
    f'&#x1F501; {int(rs["retest_fail"])} Re-Test Fail</span>'
    if rs["retest_fail"] > 0 else ""
)
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
           border-radius:8px;padding:3px 11px;font-size:.73rem;font-weight:700;">&#x1F525; {int(rs['high_prio'])} High Priority</span>
      {retest_badge}
    </div>
  </div>
  <div style="text-align:center;">
    <div style="font-size:2.4rem;font-weight:900;color:{av_c};">{int(rs['total'])}</div>
    <div style="font-size:.7rem;color:#94a3b8;font-weight:700;text-transform:uppercase;">Total Issues</div>
  </div>
</div>
"""
components.html(spotlight_html, height=110)

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
        paper_bgcolor=BG, plot_bgcolor=BG, height=340,
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
        marker_color=[PC.get(p,"#94a3b8") for p in pc2["Priority"]],
        marker_line_color="#fff", marker_line_width=1.5,
        text=pc2["Count"], textposition="outside",
        textfont=dict(size=12, color="#0f172a"),
    ))
    fig.update_layout(**B(340), xaxis_title=None, yaxis_title="Issues", showlegend=False, bargap=0.3)
    fig.update_layout(margin=dict(t=40, b=30, l=50, r=20))
    fig.update_yaxes(range=[0, mx*1.3])
    fig.update_xaxes(tickfont=dict(size=11, color="#1e293b"))
    st.markdown("**Priority Breakdown**")
    st.plotly_chart(fig, use_container_width=True)

with sp3:
    tc2 = rdf_s["issue_type"].value_counts().reset_index()
    tc2.columns = ["Type","Count"]
    mx2 = int(tc2["Count"].max()) if len(tc2) else 10
    fig = go.Figure(go.Bar(
        y=tc2["Type"], x=tc2["Count"], orientation="h",
        marker_color=[TC.get(t,"#6366f1") for t in tc2["Type"]],
        marker_line_color="#fff", marker_line_width=1.5,
        text=tc2["Count"], textposition="outside",
        textfont=dict(size=12, color="#0f172a"),
    ))
    fig.update_layout(**B(340), xaxis_title="Issues", yaxis_title=None, showlegend=False)
    fig.update_layout(margin=dict(t=40, b=30, l=110, r=70))
    fig.update_xaxes(range=[0, mx2*1.28], tickfont=dict(size=11, color="#475569"))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color="#1e293b"))
    st.markdown("**Issue Type Breakdown**")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 8 — Data Table
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Issue Data Explorer</p>', unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns([3,1,1,1])
with fc1:
    srch = st.text_input("s","", placeholder="🔎  Search summary or issue key…", label_visibility="collapsed")
with fc2:
    tf = st.selectbox("tf",["All Types"]+sorted(df["issue_type"].dropna().unique().tolist()), label_visibility="collapsed")
with fc3:
    sf = st.selectbox("sf",["All Statuses"]+sorted(df["status"].dropna().unique().tolist()), label_visibility="collapsed")
with fc4:
    rf = st.selectbox("rf",["All Reporters"]+sorted(df["reporter"].dropna().unique().tolist()), label_visibility="collapsed")

tbl = df[["issue_key","reporter","issue_type","summary","status","priority","assignee","created"]].copy()
if srch: tbl = tbl[tbl["summary"].fillna("").str.contains(srch,case=False)|
                   tbl["issue_key"].fillna("").str.contains(srch,case=False)]
if tf!="All Types":     tbl = tbl[tbl["issue_type"]==tf]
if sf!="All Statuses":  tbl = tbl[tbl["status"]==sf]
if rf!="All Reporters": tbl = tbl[tbl["reporter"]==rf]
tbl.columns = ["Key","Reporter","Type","Summary","Status","Priority","Assignee","Created"]
st.dataframe(tbl, use_container_width=True, height=400,
             column_config={
                 "Key":      st.column_config.TextColumn(width="small"),
                 "Reporter": st.column_config.TextColumn(width="medium"),
                 "Type":     st.column_config.TextColumn(width="small"),
                 "Summary":  st.column_config.TextColumn(width="large"),
                 "Status":   st.column_config.TextColumn(width="medium"),
                 "Priority": st.column_config.TextColumn(width="small"),
             })
st.caption(f"Showing {len(tbl):,} of {len(df):,} issues")
st.markdown('</div>', unsafe_allow_html=True)
