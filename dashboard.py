import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Issue Tracker", page_icon="🐛", layout="wide")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.main, [data-testid="stAppViewContainer"] { background: #0d1117; }
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; }
[data-testid="stSidebar"] { background: #161b27 !important; border-right: 1px solid #21262d; }
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem !important; }

/* ── KPI cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 12px; margin-bottom: 24px; }
.kpi-card {
    background: linear-gradient(145deg,#161b27,#1c2235);
    border: 1px solid #21262d;
    border-radius: 14px;
    padding: 18px 20px 14px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute; top:0; left:0; right:0; height:3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue::before   { background: linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.orange::before { background: linear-gradient(90deg,#f97316,#fb923c); }
.kpi-card.green::before  { background: linear-gradient(90deg,#22c55e,#4ade80); }
.kpi-card.red::before    { background: linear-gradient(90deg,#ef4444,#f87171); }
.kpi-card.purple::before { background: linear-gradient(90deg,#8b5cf6,#a78bfa); }
.kpi-card.yellow::before { background: linear-gradient(90deg,#eab308,#fbbf24); }
.kpi-icon { font-size: 1.4rem; margin-bottom: 6px; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #f0f6fc; line-height: 1; }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: .07em; margin-top: 4px; }
.kpi-sub { font-size: 0.75rem; color: #6e7681; margin-top: 2px; }

/* ── Section headers ── */
.sec-head {
    font-size: 0.85rem; font-weight: 700; color: #8b949e;
    text-transform: uppercase; letter-spacing: .1em;
    border-left: 3px solid #3b82f6; padding-left: 10px;
    margin: 0 0 14px 0;
}

/* ── Chart wrapper ── */
.chart-wrap {
    background: #161b27; border: 1px solid #21262d;
    border-radius: 14px; padding: 20px;
    margin-bottom: 18px;
}

/* ── Issue type badge row ── */
.badge-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px; }
.badge {
    display:flex; align-items:center; gap:8px;
    background:#161b27; border:1px solid #21262d;
    border-radius:10px; padding:10px 16px;
    font-size:0.85rem; font-weight:600; color:#c9d1d9;
}
.badge-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

/* ── Tabs ── */
[data-testid="stTabs"] button { font-size:0.82rem !important; font-weight:600 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] iframe { border-radius: 10px; }

/* ── Sidebar multiselect ── */
[data-testid="stMultiSelect"] { font-size: 0.82rem; }

/* ── Status pill in table ── */
.pill {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em;
}

/* scrollbar */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#0d1117; }
::-webkit-scrollbar-thumb { background:#30363d; border-radius:6px; }
</style>
""", unsafe_allow_html=True)

# ── Colour maps ──────────────────────────────────────────────────────────────
TYPE_COLORS = {
    "Bug":         "#ef4444",
    "Improvement": "#3b82f6",
    "Task":        "#a78bfa",
    "Epic":        "#f97316",
    "Story":       "#22c55e",
    "New Feature": "#06b6d4",
    "Sub-task":    "#eab308",
    "Initiative":  "#ec4899",
}
TYPE_ICONS = {
    "Bug":"🐛","Improvement":"⬆️","Task":"✅","Epic":"⚡",
    "Story":"📖","New Feature":"✨","Sub-task":"🔧","Initiative":"🚀",
}
STATUS_COLORS = {
    "NEW":                   "#3b82f6",
    "To Do":                 "#8b5cf6",
    "In Progress":           "#f97316",
    "Assigned To Developer": "#06b6d4",
    "IN TESTING":            "#eab308",
    "RE-TEST FAIL":          "#ef4444",
    "ACCEPTED":              "#22c55e",
    "Done":                  "#10b981",
    "Rejected":              "#6b7280",
    "BLOCKED":               "#dc2626",
}
PRIORITY_COLORS = {
    "Highest":"#ef4444","High":"#f97316",
    "Medium":"#eab308","Low":"#22c55e","Lowest":"#3b82f6",
}
BG   = "#0d1117"
CARD = "#161b27"
GRID = "#21262d"
FONT = "#c9d1d9"

def plotly_base():
    return dict(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=FONT, family="Inter, sans-serif", size=12),
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
        hoverlabel=dict(bgcolor="#1c2235", bordercolor=GRID, font_color=FONT),
    )

LEGEND_H = dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID, font=dict(size=11),
                orientation="h", y=1.12, x=0)
LEGEND_V = dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID, font=dict(size=11),
                orientation="v", y=0.5, x=1.0)

# ── DB ───────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host="localhost", port="5432",
        database="issue_tracker", user="postgres", password="postgres"
    )

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_sql("SELECT * FROM public.issues", get_conn())
    df["issue_type"] = df["issue_type"].str.strip()
    # drop junk rows
    df = df[~df["issue_type"].str.startswith("Generated at", na=False)]
    df["created_dt"] = pd.to_datetime(df["created"], errors="coerce")
    df["month"]  = df["created_dt"].dt.strftime("%b %Y")
    df["month_sort"] = df["created_dt"].dt.to_period("M")
    return df

# ── Sidebar filters ──────────────────────────────────────────────────────────
try:
    raw = load_data()
except Exception as e:
    st.error(f"DB Error: {e}"); st.stop()

st.sidebar.markdown("### 🔍 Filters")

types_all      = sorted(raw["issue_type"].dropna().unique())
statuses_all   = sorted(raw["status"].dropna().unique())
priorities_all = sorted(raw["priority"].dropna().unique())
assignees_all  = sorted(raw["assignee"].dropna().unique())

sel_type  = st.sidebar.multiselect("Issue Type",  types_all,      default=types_all)
sel_stat  = st.sidebar.multiselect("Status",      statuses_all,   default=statuses_all)
sel_prio  = st.sidebar.multiselect("Priority",    priorities_all, default=priorities_all)
sel_asgn  = st.sidebar.multiselect("Assignee",    assignees_all,  default=assignees_all)

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

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#161b27,#1c2438);border:1px solid #21262d;
     border-radius:16px;padding:22px 28px;margin-bottom:24px;
     display:flex;justify-content:space-between;align-items:center;">
  <div>
    <div style="font-size:1.6rem;font-weight:800;color:#f0f6fc;">📋 Issue Tracker Dashboard</div>
    <div style="font-size:0.82rem;color:#6e7681;margin-top:4px;">
      {len(df):,} issues shown &nbsp;·&nbsp; {len(raw):,} total &nbsp;·&nbsp;
      Refreshed {datetime.now().strftime('%d %b %Y, %H:%M')}
    </div>
  </div>
  <div style="display:flex;gap:8px;">
    {''.join(f'<span style="background:{TYPE_COLORS.get(t,"#6366f1")}22;color:{TYPE_COLORS.get(t,"#6366f1")};border:1px solid {TYPE_COLORS.get(t,"#6366f1")}44;border-radius:8px;padding:4px 12px;font-size:0.78rem;font-weight:700;">{TYPE_ICONS.get(t,"")} {t}: {len(df[df["issue_type"]==t])}</span>' for t in types_all if t in df["issue_type"].values)}
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
total     = len(df)
bugs      = len(df[df["issue_type"] == "Bug"])
impr      = len(df[df["issue_type"] == "Improvement"])
open_c    = len(df[df["status"] == "NEW"])
in_prog   = len(df[df["status"] == "In Progress"])
done_c    = len(df[df["status"].isin(["Done", "ACCEPTED"])])
hi_prio   = len(df[df["priority"].isin(["Highest", "High"])])
blocked   = len(df[df["status"] == "BLOCKED"])

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-icon">📋</div>
    <div class="kpi-value">{total:,}</div>
    <div class="kpi-label">Total Issues</div>
  </div>
  <div class="kpi-card red">
    <div class="kpi-icon">🐛</div>
    <div class="kpi-value">{bugs:,}</div>
    <div class="kpi-label">Bugs</div>
    <div class="kpi-sub">{bugs/total*100:.0f}% of total</div>
  </div>
  <div class="kpi-card blue">
    <div class="kpi-icon">⬆️</div>
    <div class="kpi-value">{impr:,}</div>
    <div class="kpi-label">Improvements</div>
    <div class="kpi-sub">{impr/total*100:.0f}% of total</div>
  </div>
  <div class="kpi-card orange">
    <div class="kpi-icon">🔥</div>
    <div class="kpi-value">{open_c:,}</div>
    <div class="kpi-label">New / Open</div>
  </div>
  <div class="kpi-card green">
    <div class="kpi-icon">✅</div>
    <div class="kpi-value">{done_c:,}</div>
    <div class="kpi-label">Done / Accepted</div>
    <div class="kpi-sub">{done_c/total*100:.0f}% resolved</div>
  </div>
  <div class="kpi-card purple">
    <div class="kpi-icon">⚡</div>
    <div class="kpi-value">{hi_prio:,}</div>
    <div class="kpi-label">High Priority</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 1 — Bug vs Improvement by Status  (THE KEY CHART)
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
st.markdown('<p class="sec-head">🐛 Bug vs ⬆️ Improvement — Status Breakdown</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["  Grouped Bar  ", "  100% Stacked  ", "  Side-by-Side Progress  "])

focus_types = ["Bug", "Improvement"]
df_focus = df[df["issue_type"].isin(focus_types)].copy()
status_order = ["NEW","To Do","Assigned To Developer","In Progress","IN TESTING","RE-TEST FAIL","ACCEPTED","Done","Rejected","BLOCKED"]
status_order = [s for s in status_order if s in df_focus["status"].values]

grp = (df_focus.groupby(["status","issue_type"])
       .size().reset_index(name="Count")
       .pivot(index="status", columns="issue_type", values="Count")
       .fillna(0).reindex(status_order).fillna(0).reset_index())

with tab1:
    # Grouped bar – each status has Bug bar + Improvement bar side by side
    fig = go.Figure()
    for itype in focus_types:
        if itype in grp.columns:
            fig.add_trace(go.Bar(
                name=itype, x=grp["status"], y=grp[itype],
                marker_color=TYPE_COLORS[itype],
                marker_line_color=BG, marker_line_width=1.5,
                text=grp[itype].astype(int),
                textposition="outside",
                textfont=dict(size=11, color=FONT),
            ))
    fig.update_layout(**plotly_base(), barmode="group", height=360,
                      xaxis_title=None, yaxis_title="Count",
                      legend=LEGEND_H)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # 100% stacked — shows relative proportion per status
    long = df_focus[df_focus["status"].isin(status_order)].groupby(["status","issue_type"]).size().reset_index(name="Count")
    totals = long.groupby("status")["Count"].transform("sum")
    long["Pct"] = (long["Count"] / totals * 100).round(1)
    fig = px.bar(long, x="status", y="Pct", color="issue_type",
                 color_discrete_map=TYPE_COLORS,
                 category_orders={"status": status_order},
                 text=long["Pct"].map(lambda v: f"{v:.0f}%"),
                 barmode="stack")
    fig.update_traces(textposition="inside", textfont_size=11)
    fig.update_layout(**plotly_base(), height=360,
                      xaxis_title=None, yaxis_title="% Share")
    fig.update_yaxes(range=[0, 105])
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Horizontal progress-bar style per status
    cols = st.columns(2)
    for idx, itype in enumerate(focus_types):
        with cols[idx]:
            color = TYPE_COLORS[itype]
            icon  = TYPE_ICONS[itype]
            sub   = df_focus[df_focus["issue_type"] == itype]
            sub_grp = sub.groupby("status").size().reset_index(name="cnt")
            sub_grp = sub_grp.sort_values("cnt", ascending=False)
            total_t = sub_grp["cnt"].sum()
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid {color}44;border-radius:12px;
                 padding:18px;margin-bottom:8px;">
              <div style="font-size:1rem;font-weight:800;color:{color};margin-bottom:14px;">
                {icon} {itype} &nbsp;<span style="color:#6e7681;font-size:0.82rem;font-weight:500;">({total_t:,} total)</span>
              </div>
            """, unsafe_allow_html=True)
            for _, row in sub_grp.iterrows():
                pct = row["cnt"] / total_t * 100 if total_t else 0
                sc  = STATUS_COLORS.get(row["status"], "#6b7280")
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;
                       font-size:0.78rem;color:#c9d1d9;margin-bottom:4px;">
                    <span style="font-weight:600;">{row['status']}</span>
                    <span style="color:{sc};font-weight:700;">{row['cnt']:,} &nbsp;({pct:.0f}%)</span>
                  </div>
                  <div style="background:#21262d;border-radius:6px;height:8px;overflow:hidden;">
                    <div style="background:{sc};width:{pct}%;height:100%;border-radius:6px;
                         transition:width .4s;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 2 — All Issue Types by Status  (heatmap + sunburst)
# ════════════════════════════════════════════════════════════════
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">All Issue Types × Status Heatmap</p>', unsafe_allow_html=True)
    pivot = (df.groupby(["issue_type","status"]).size()
               .reset_index(name="Count")
               .pivot(index="issue_type", columns="status", values="Count")
               .fillna(0))
    fig = px.imshow(pivot.astype(int), text_auto=True, aspect="auto",
                    color_continuous_scale=[[0,"#161b27"],[0.01,"#1d3461"],[1,"#3b82f6"]],
                    zmin=0)
    fig.update_traces(textfont_size=12)
    fig.update_layout(**plotly_base(), height=300,
                      xaxis_title=None, yaxis_title=None,
                      coloraxis_showscale=False)
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Type → Status Sunburst</p>', unsafe_allow_html=True)
    sun = df.groupby(["issue_type","status"]).size().reset_index(name="Count")
    fig = px.sunburst(sun, path=["issue_type","status"], values="Count",
                      color="issue_type", color_discrete_map=TYPE_COLORS)
    fig.update_traces(textinfo="label+percent entry",
                      marker=dict(line=dict(width=1.5, color=BG)))
    fig.update_layout(**plotly_base(), height=300, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 3 — Priority analysis
# ════════════════════════════════════════════════════════════════
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Priority Distribution by Issue Type</p>', unsafe_allow_html=True)
    prio_order = ["Highest","High","Medium","Low","Lowest"]
    pg = df.groupby(["issue_type","priority"]).size().reset_index(name="Count")
    fig = px.bar(pg, x="issue_type", y="Count", color="priority",
                 color_discrete_map=PRIORITY_COLORS, barmode="stack",
                 category_orders={"priority": prio_order})
    fig.update_layout(**plotly_base(), height=300, xaxis_title=None, yaxis_title="Issues",
                      legend=LEGEND_H)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Bug Priority — Current Status Mix</p>', unsafe_allow_html=True)
    bug_prio_stat = (df[df["issue_type"]=="Bug"]
                     .groupby(["priority","status"]).size().reset_index(name="Count"))
    fig = px.bar(bug_prio_stat, x="priority", y="Count", color="status",
                 color_discrete_map=STATUS_COLORS, barmode="stack",
                 category_orders={"priority": prio_order})
    fig.update_layout(**plotly_base(), height=300, xaxis_title=None, yaxis_title="Bugs",
                      legend=LEGEND_H)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 4 — Trend over time
# ════════════════════════════════════════════════════════════════
if df["created_dt"].notna().any():
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Issues Created Over Time — Bug vs Improvement</p>', unsafe_allow_html=True)

    trend = (df[df["issue_type"].isin(focus_types)]
             .groupby(["month_sort","issue_type"]).size()
             .reset_index(name="Count"))
    trend["month_sort"] = trend["month_sort"].astype(str)
    trend = trend.sort_values("month_sort")

    fig = px.line(trend, x="month_sort", y="Count", color="issue_type",
                  color_discrete_map=TYPE_COLORS, markers=True, line_shape="spline")
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(**plotly_base(), height=280, xaxis_title=None, yaxis_title="Issues",
                      legend=LEGEND_H)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 5 — Assignee workload
# ════════════════════════════════════════════════════════════════
c5, c6 = st.columns([3, 2])

with c5:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Top Assignees — Bug vs Improvement</p>', unsafe_allow_html=True)
    top_asgn = df["assignee"].value_counts().head(12).index
    adf = (df[df["assignee"].isin(top_asgn) & df["issue_type"].isin(focus_types)]
           .groupby(["assignee","issue_type"]).size().reset_index(name="Count"))
    fig = px.bar(adf, y="assignee", x="Count", color="issue_type",
                 color_discrete_map=TYPE_COLORS, barmode="group", orientation="h")
    fig.update_layout(**plotly_base(), height=360,
                      xaxis_title="Issues", yaxis_title=None,
                      legend=LEGEND_H)
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="sec-head">Overall Status Distribution</p>', unsafe_allow_html=True)
    sc = df["status"].value_counts().reset_index()
    sc.columns = ["Status","Count"]
    fig = px.pie(sc, names="Status", values="Count",
                 color="Status", color_discrete_map=STATUS_COLORS, hole=0.58)
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color=BG, width=2)))
    fig.update_layout(**plotly_base(), height=360,
                      legend=LEGEND_V)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# SECTION 6 — Data table
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
st.markdown('<p class="sec-head">Issue Data Explorer</p>', unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([3,1,1])
with fc1:
    search = st.text_input("🔎 Search summary / key", "", label_visibility="collapsed",
                           placeholder="Search by summary or issue key...")
with fc2:
    type_filter = st.selectbox("Type", ["All"] + types_all, label_visibility="collapsed")
with fc3:
    stat_filter = st.selectbox("Status", ["All"] + statuses_all, label_visibility="collapsed")

tbl = df[["issue_key","issue_type","summary","status","priority","assignee","reporter","created"]].copy()
if search:
    tbl = tbl[tbl["summary"].fillna("").str.contains(search, case=False) |
              tbl["issue_key"].fillna("").str.contains(search, case=False)]
if type_filter != "All":
    tbl = tbl[tbl["issue_type"] == type_filter]
if stat_filter != "All":
    tbl = tbl[tbl["status"] == stat_filter]

tbl.columns = ["Key","Type","Summary","Status","Priority","Assignee","Reporter","Created"]
st.dataframe(tbl, use_container_width=True, height=380,
             column_config={
                 "Key":      st.column_config.TextColumn("Key", width="small"),
                 "Type":     st.column_config.TextColumn("Type", width="small"),
                 "Summary":  st.column_config.TextColumn("Summary", width="large"),
                 "Status":   st.column_config.TextColumn("Status", width="medium"),
                 "Priority": st.column_config.TextColumn("Priority", width="small"),
             })
st.caption(f"{len(tbl):,} rows matching filters")
st.markdown('</div>', unsafe_allow_html=True)
