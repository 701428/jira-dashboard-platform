import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Issue Tracker (Jira)", page_icon="🐛", layout="wide",
                   initial_sidebar_state="expanded")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif!important;box-sizing:border-box;}
.main,[data-testid="stAppViewContainer"]{background:#f0f4f8;}
.block-container{padding:1.5rem 2.2rem 3rem!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #e2e8f0;}
[data-testid="stSidebar"] .block-container{padding:1.4rem 1rem!important;}
.banner{background:linear-gradient(120deg,#1e40af,#2563eb 55%,#0ea5e9);
  border-radius:18px;padding:28px 36px;margin-bottom:26px;
  box-shadow:0 8px 32px rgba(37,99,235,.22);}
.banner-title{font-size:1.7rem;font-weight:900;color:#fff;letter-spacing:-.02em;}
.banner-sub{font-size:.84rem;color:rgba(255,255,255,.78);margin-top:4px;}
.bstat{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.28);
  border-radius:9px;padding:4px 13px;font-size:.79rem;font-weight:700;color:#fff;
  display:inline-block;margin:4px 4px 0 0;}

.kpi-row{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:24px;}
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

[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] strong{color:#0f172a!important;}
[data-testid="stSidebar"] label{color:#0f172a!important;}
[data-testid="stTextInput"] input{color:#0f172a!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#f1f5f9;}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:5px;}
</style>
""", unsafe_allow_html=True)

# ── Colour maps ───────────────────────────────────────────────────────────────
TYPE_COLORS = {
    "Bug":"#ef4444","Improvement":"#3b82f6","Task":"#8b5cf6",
    "Epic":"#f97316","Story":"#22c55e","New Feature":"#06b6d4",
    "Sub-task":"#eab308","Initiative":"#ec4899",
}
TYPE_ICONS = {
    "Bug":"🐛","Improvement":"⬆️","Task":"✅","Epic":"⚡",
    "Story":"📖","New Feature":"✨","Sub-task":"🔧","Initiative":"🚀",
}
STATUS_COLORS = {
    "NEW":"#3b82f6","To Do":"#8b5cf6","In Progress":"#f97316",
    "Assigned To Developer":"#06b6d4","IN TESTING":"#eab308",
    "RE-TEST FAIL":"#ef4444","ACCEPTED":"#22c55e","Done":"#10b981",
    "Rejected":"#94a3b8","BLOCKED":"#dc2626",
}
PRIORITY_COLORS = {
    "Highest":"#ef4444","High":"#f97316","Medium":"#eab308",
    "Low":"#22c55e","Lowest":"#3b82f6",
}
AV = ["#2563eb","#7c3aed","#db2777","#ea580c","#059669",
      "#0891b2","#d97706","#9333ea","#dc2626","#0284c7"]

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

# ── Jira config (sidebar) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Jira Connection")
    JIRA_URL     = st.text_input("Jira URL",    value="https://grampower.atlassian.net", key="jurl")
    JIRA_EMAIL   = st.text_input("Email",       value="lalit.tak@polarisgrids.com",      key="jemail")
    JIRA_TOKEN   = st.text_input("API Token",   value="ATATT3xFfGF0unybnSFO9V6JXhmn46bObBpg9IVgYs4QllwnygZk242_Y-pI-QxfoAiz2M4SIII3vOCTINDbPouHIOhxYp-vuHWqMA_PyoF77ZwOrWfkL2mz6r-LMlQmmzyKxo0f0LGqQre2CFRpQuuwylpBiREKeB4feofI7XyHxoF2zKs0NEo=271C6FB8", type="password", key="jtoken")
    JIRA_PROJECT = st.text_input("Project Key", value="PC", key="jproject")
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
    df["issue_type"] = df["issue_type"].str.strip()
    df["created_dt"] = pd.to_datetime(df["created"], errors="coerce", utc=True)
    df["created_dt"] = df["created_dt"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    df["month"]      = df["created_dt"].dt.strftime("%b %Y")
    df["month_sort"] = df["created_dt"].dt.to_period("M")
    return df

# ── Load ──────────────────────────────────────────────────────────────────────
try:
    raw = load_jira_data(JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, JIRA_PROJECT)
except Exception as e:
    st.error(f"Jira Error: {e}"); st.stop()

if raw.empty:
    st.warning("No issues found for this project."); st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filters")
types_all      = sorted(raw["issue_type"].dropna().unique())
statuses_all   = sorted(raw["status"].dropna().unique())
priorities_all = sorted(raw["priority"].dropna().unique())
assignees_all  = sorted(raw["assignee"].dropna().unique())

sel_type = st.sidebar.multiselect("Issue Type",  types_all,      default=types_all)
sel_stat = st.sidebar.multiselect("Status",      statuses_all,   default=statuses_all)
sel_prio = st.sidebar.multiselect("Priority",    priorities_all, default=priorities_all)
sel_asgn = st.sidebar.multiselect("Assignee",    assignees_all,  default=assignees_all)

if raw["created_dt"].notna().any():
    mn = raw["created_dt"].min().date()
    mx = raw["created_dt"].max().date()
    dr = st.sidebar.date_input("Date Range", (mn, mx), min_value=mn, max_value=mx)
else:
    dr = None

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear(); st.rerun()

df = raw.copy()
if sel_type: df = df[df["issue_type"].isin(sel_type)]
if sel_stat: df = df[df["status"].isin(sel_stat)]
if sel_prio: df = df[df["priority"].isin(sel_prio)]
if sel_asgn: df = df[df["assignee"].isin(sel_asgn)]
if dr and len(dr) == 2:
    df = df[(df["created_dt"].dt.date >= dr[0]) & (df["created_dt"].dt.date <= dr[1])]

# ── Derived counts ────────────────────────────────────────────────────────────
total   = len(df)
bugs    = len(df[df["issue_type"] == "Bug"])
impr    = len(df[df["issue_type"] == "Improvement"])
open_c  = len(df[df["status"] == "NEW"])
done_c  = len(df[df["status"].isin(["Done","ACCEPTED"])])
hi_prio = len(df[df["priority"].isin(["Highest","High"])])
blocked = len(df[df["status"] == "BLOCKED"])
res_rate = round(done_c/total*100, 1) if total else 0

# ════════════════════════════════════════════════════════════════
# BANNER
# ════════════════════════════════════════════════════════════════
type_badges = "".join(
    f'<span class="bstat">{TYPE_ICONS.get(t,"")} {t}: {len(df[df["issue_type"]==t])}</span>'
    for t in types_all if t in df["issue_type"].values
)
st.markdown(f"""
<div class="banner">
  <div class="banner-title">📋 Issue Tracker Dashboard</div>
  <div class="banner-sub">
    {total:,} issues · Project: <b>{JIRA_PROJECT.upper()}</b> ·
    Refreshed {datetime.now().strftime('%d %b %Y, %H:%M')}
  </div>
  <div style="margin-top:12px;">{type_badges}</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-icon">📋</div>
    <div class="kpi-val">{total:,}</div>
    <div class="kpi-lbl">Total Issues</div>
    <div class="kpi-note">{len(raw):,} in project</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">🐛</div>
    <div class="kpi-val">{bugs:,}</div>
    <div class="kpi-lbl">Bugs</div>
    <div class="kpi-note">{round(bugs/total*100,1) if total else 0}% of total</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">⬆️</div>
    <div class="kpi-val">{impr:,}</div>
    <div class="kpi-lbl">Improvements</div>
    <div class="kpi-note">{round(impr/total*100,1) if total else 0}% of total</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">🔴</div>
    <div class="kpi-val">{open_c:,}</div>
    <div class="kpi-lbl">New / Open</div>
    <div class="kpi-note">{round(open_c/total*100,1) if total else 0}% unresolved</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">✅</div>
    <div class="kpi-val">{done_c:,}</div>
    <div class="kpi-lbl">Done / Accepted</div>
    <div class="kpi-note">{res_rate}% resolved</div>
  </div>
  <div class="kpi">
    <div class="kpi-icon">⚡</div>
    <div class="kpi-val">{hi_prio:,}</div>
    <div class="kpi-lbl">High Priority</div>
    <div class="kpi-note">{blocked} blocked</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 1 — Bug vs Improvement by Status
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">🐛 Bug vs ⬆️ Improvement — Status Breakdown</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["  Grouped Bar  ", "  100% Stacked  ", "  Side-by-Side Progress  "])

focus_types  = ["Bug", "Improvement"]
df_focus     = df[df["issue_type"].isin(focus_types)].copy()
status_order = ["NEW","To Do","Assigned To Developer","In Progress","IN TESTING",
                "RE-TEST FAIL","ACCEPTED","Done","Rejected","BLOCKED"]
status_order = [s for s in status_order if s in df_focus["status"].values]

grp = (df_focus.groupby(["status","issue_type"])
       .size().reset_index(name="Count")
       .pivot(index="status", columns="issue_type", values="Count")
       .fillna(0).reindex(status_order).fillna(0).reset_index())

with tab1:
    fig = go.Figure()
    max_y = 0
    for itype in focus_types:
        if itype in grp.columns:
            max_y = max(max_y, int(grp[itype].max()))
            fig.add_trace(go.Bar(
                name=itype, x=grp["status"], y=grp[itype],
                marker_color=TYPE_COLORS[itype],
                marker_line_color="#fff", marker_line_width=1.5,
                text=grp[itype].astype(int), textposition="outside",
                textfont=dict(size=11, color=TXT),
            ))
    fig.update_layout(**B(380), barmode="group", xaxis_title=None, yaxis_title="Count",
                      bargap=0.25, bargroupgap=0.1, legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=80, l=40, r=20))
    fig.update_yaxes(range=[0, max_y * 1.25])
    fig.update_xaxes(tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    long   = df_focus[df_focus["status"].isin(status_order)].groupby(["status","issue_type"]).size().reset_index(name="Count")
    totals = long.groupby("status")["Count"].transform("sum")
    long["Pct"] = (long["Count"] / totals * 100).round(1)
    fig = px.bar(long, x="status", y="Pct", color="issue_type",
                 color_discrete_map=TYPE_COLORS,
                 category_orders={"status": status_order},
                 text=long["Pct"].map(lambda v: f"{v:.0f}%"),
                 barmode="stack")
    fig.update_traces(textposition="inside", textfont_size=11)
    fig.update_layout(**B(380), xaxis_title=None, yaxis_title="% Share", legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=80, l=40, r=20))
    fig.update_yaxes(range=[0, 105])
    fig.update_xaxes(tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    cols = st.columns(2)
    for idx, itype in enumerate(focus_types):
        with cols[idx]:
            color   = TYPE_COLORS[itype]
            icon    = TYPE_ICONS[itype]
            sub     = df_focus[df_focus["issue_type"] == itype]
            sub_grp = sub.groupby("status").size().reset_index(name="cnt").sort_values("cnt", ascending=False)
            total_t = sub_grp["cnt"].sum()
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;padding:18px;">
              <div style="font-size:.95rem;font-weight:800;color:{color};margin-bottom:16px;">
                {icon} {itype}
                <span style="color:#94a3b8;font-size:.78rem;font-weight:500;margin-left:6px;">({total_t:,} total)</span>
              </div>
            """, unsafe_allow_html=True)
            for _, row in sub_grp.iterrows():
                pct = row["cnt"] / total_t * 100 if total_t else 0
                sc  = STATUS_COLORS.get(row["status"], "#94a3b8")
                st.markdown(f"""
                <div class="pbar">
                  <div class="pbar-head">
                    <span class="pbar-name">{row['status']}</span>
                    <span class="pbar-val" style="color:{sc};">{row['cnt']:,}
                      <span style="color:#94a3b8;font-weight:500;font-size:.7rem;">({pct:.0f}%)</span>
                    </span>
                  </div>
                  <div class="pbar-track">
                    <div class="pbar-fill" style="width:{pct:.1f}%;background:{sc};opacity:.85;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 2 — Heatmap + Sunburst
# ════════════════════════════════════════════════════════════════
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">All Issue Types × Status Heatmap</p>', unsafe_allow_html=True)
    pivot = (df.groupby(["issue_type","status"]).size()
               .reset_index(name="Count")
               .pivot(index="issue_type", columns="status", values="Count")
               .fillna(0))
    fig = px.imshow(pivot.astype(int), text_auto=True, aspect="auto",
                    color_continuous_scale=[[0,"#f0f9ff"],[0.01,"#bfdbfe"],[1,"#1d4ed8"]], zmin=0)
    fig.update_traces(textfont=dict(size=11, color=TXT))
    fig.update_layout(**B(300), coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
    fig.update_layout(margin=dict(t=10, b=80, l=110, r=10))
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Type → Status Sunburst</p>', unsafe_allow_html=True)
    sun = df.groupby(["issue_type","status"]).size().reset_index(name="Count")
    fig = px.sunburst(sun, path=["issue_type","status"], values="Count",
                      color="issue_type", color_discrete_map=TYPE_COLORS)
    fig.update_traces(textinfo="label+percent entry",
                      marker=dict(line=dict(width=1.5, color="#fff")))
    fig.update_layout(**B(300), coloraxis_showscale=False)
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 3 — Priority analysis
# ════════════════════════════════════════════════════════════════
c3, c4 = st.columns(2)
prio_order = ["Highest","High","Medium","Low","Lowest"]

with c3:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Priority Distribution by Issue Type</p>', unsafe_allow_html=True)
    pg = df.groupby(["issue_type","priority"]).size().reset_index(name="Count")
    fig = px.bar(pg, x="issue_type", y="Count", color="priority",
                 color_discrete_map=PRIORITY_COLORS, barmode="stack",
                 category_orders={"priority": prio_order})
    fig.update_traces(marker_line_color="#fff", marker_line_width=0.8)
    fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Issues", legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=40, l=50, r=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Bug Priority — Current Status Mix</p>', unsafe_allow_html=True)
    bug_prio_stat = (df[df["issue_type"]=="Bug"]
                     .groupby(["priority","status"]).size().reset_index(name="Count"))
    fig = px.bar(bug_prio_stat, x="priority", y="Count", color="status",
                 color_discrete_map=STATUS_COLORS, barmode="stack",
                 category_orders={"priority": prio_order})
    fig.update_traces(marker_line_color="#fff", marker_line_width=0.8)
    fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Bugs", legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=40, l=50, r=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 4 — Trend over time
# ════════════════════════════════════════════════════════════════
if df["created_dt"].notna().any():
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Issues Created Over Time — Bug vs Improvement</p>', unsafe_allow_html=True)
    trend = (df[df["issue_type"].isin(focus_types)]
             .groupby(["month_sort","issue_type"]).size().reset_index(name="Count"))
    trend["month_sort"] = trend["month_sort"].astype(str)
    trend = trend.sort_values("month_sort")
    fig = px.line(trend, x="month_sort", y="Count", color="issue_type",
                  color_discrete_map=TYPE_COLORS, markers=True, line_shape="spline")
    fig.update_traces(line_width=2.5, marker_size=8,
                      marker_line_color="#fff", marker_line_width=2)
    fig.update_layout(**B(300), xaxis_title=None, yaxis_title="Issues", legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=60, l=60, r=20))
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 5 — Assignee workload
# ════════════════════════════════════════════════════════════════
c5, c6 = st.columns([3, 2])

with c5:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Top Reporters — Bug vs Improvement</p>', unsafe_allow_html=True)
    top_rep = df["reporter"].value_counts().head(12).index
    adf = (df[df["reporter"].isin(top_rep) & df["issue_type"].isin(focus_types)]
           .groupby(["reporter","issue_type"]).size().reset_index(name="Count"))
    n_rep = len(top_rep)
    fig = px.bar(adf, y="reporter", x="Count", color="issue_type",
                 color_discrete_map=TYPE_COLORS, barmode="group", orientation="h")
    fig.update_traces(marker_line_color="#fff", marker_line_width=0.8)
    fig.update_layout(**B(max(360, n_rep*48+100)),
                      xaxis_title="Issues", yaxis_title=None, legend=LEG_H)
    fig.update_layout(margin=dict(t=50, b=40, l=160, r=20))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color="#1e293b"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="wcard">', unsafe_allow_html=True)
    st.markdown('<p class="stitle">Overall Status Distribution</p>', unsafe_allow_html=True)
    sc = df["status"].value_counts().reset_index()
    sc.columns = ["Status","Count"]
    fig = go.Figure(go.Pie(
        labels=sc["Status"], values=sc["Count"], hole=0.55,
        marker=dict(colors=[STATUS_COLORS.get(s,"#94a3b8") for s in sc["Status"]],
                    line=dict(color="#fff", width=2)),
        textposition="outside", textinfo="percent+label",
        textfont=dict(size=11, color=TXT),
        hovertemplate="<b>%{label}</b><br>%{value} issues (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, height=380,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False,
        font=dict(color=TXT, family="Inter,sans-serif", size=12),
        annotations=[dict(text=f"<b>{total}</b><br><span style='font-size:11px'>issues</span>",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=18, color=TXT))],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 6 — Issue Type Deep Dive (per-type progress bars)
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Issue Type Breakdown — Progress Bars</p>', unsafe_allow_html=True)

type_counts = df["issue_type"].value_counts().reset_index()
type_counts.columns = ["Type","Count"]
max_v = int(type_counts["Count"].max()) if len(type_counts) else 1

cols_per_row = 3
rows = [type_counts.iloc[i:i+cols_per_row] for i in range(0, len(type_counts), cols_per_row)]
for row_df in rows:
    row_cols = st.columns(cols_per_row)
    for col_obj, (_, r) in zip(row_cols, row_df.iterrows()):
        with col_obj:
            color = TYPE_COLORS.get(r["Type"], "#6366f1")
            icon  = TYPE_ICONS.get(r["Type"], "📌")
            pct   = r["Count"] / max_v * 100
            share = round(r["Count"] / total * 100, 1) if total else 0
            # status breakdown for this type
            sub_stat = df[df["issue_type"]==r["Type"]]["status"].value_counts().head(4)
            status_html = "".join(
                f'<span style="background:{STATUS_COLORS.get(s,"#94a3b8")}18;'
                f'color:{STATUS_COLORS.get(s,"#94a3b8")};border:1px solid {STATUS_COLORS.get(s,"#94a3b8")}44;'
                f'border-radius:6px;padding:2px 8px;font-size:.65rem;font-weight:700;margin:2px 2px 0 0;display:inline-block;">'
                f'{s}: {c}</span>'
                for s, c in sub_stat.items()
            )
            st.markdown(f"""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:13px;padding:16px;margin-bottom:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <div style="font-size:.9rem;font-weight:800;color:{color};">{icon} {r['Type']}</div>
                <div style="font-size:1.5rem;font-weight:900;color:{color};">{int(r['Count'])}</div>
              </div>
              <div class="pbar-track" style="margin-bottom:8px;">
                <div class="pbar-fill" style="width:{pct:.1f}%;background:{color};opacity:.8;"></div>
              </div>
              <div style="font-size:.68rem;color:#94a3b8;margin-bottom:6px;">{share}% of all issues</div>
              <div>{status_html}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 7 — Data Table
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="wcard">', unsafe_allow_html=True)
st.markdown('<p class="stitle">Issue Data Explorer</p>', unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([3,1,1])
with fc1:
    search = st.text_input("search", "", label_visibility="collapsed",
                           placeholder="🔎  Search summary or issue key…")
with fc2:
    type_filter = st.selectbox("Type", ["All Types"] + types_all, label_visibility="collapsed")
with fc3:
    stat_filter = st.selectbox("Status", ["All Statuses"] + statuses_all, label_visibility="collapsed")

tbl = df[["issue_key","issue_type","summary","status","priority","assignee","reporter","created"]].copy()
if search:
    tbl = tbl[tbl["summary"].fillna("").str.contains(search, case=False) |
              tbl["issue_key"].fillna("").str.contains(search, case=False)]
if type_filter != "All Types":
    tbl = tbl[tbl["issue_type"] == type_filter]
if stat_filter != "All Statuses":
    tbl = tbl[tbl["status"] == stat_filter]

tbl.columns = ["Key","Type","Summary","Status","Priority","Assignee","Reporter","Created"]
st.dataframe(tbl, use_container_width=True, height=400,
             column_config={
                 "Key":      st.column_config.TextColumn(width="small"),
                 "Type":     st.column_config.TextColumn(width="small"),
                 "Summary":  st.column_config.TextColumn(width="large"),
                 "Status":   st.column_config.TextColumn(width="medium"),
                 "Priority": st.column_config.TextColumn(width="small"),
             })
st.caption(f"Showing {len(tbl):,} of {len(df):,} issues")
st.markdown('</div>', unsafe_allow_html=True)
