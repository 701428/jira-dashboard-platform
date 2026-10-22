import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF


def hex_to_rl(h):
    return colors.HexColor("#" + h.lstrip("#"))


def mini_bar_drawing(pct, color_hex, width=100, height=10):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#f1f5f9"), strokeColor=None))
    fill_w = max(0, min(width, width * pct / 100))
    if fill_w > 0:
        d.add(Rect(0, 0, fill_w, height, fillColor=colors.HexColor(color_hex), strokeColor=None))
    return d


# ── Case-insensitive field matchers (mirrors jira_reporter_dashboard.py) ──────
_RESOLVED_ST  = {"done", "accepted", "closed", "resolved", "fixed"}
_OPEN_ST      = {"new", "open", "to do", "todo"}
_BLOCKED_ST   = {"blocked"}
_RETEST_ST    = {"re-test fail", "retest fail"}
_BUG_T        = {"bug", "defect"}
_IMPROVEMENT_T= {"improvement", "enhancement", "new feature"}
_HIGH_P       = {"highest", "high", "critical", "blocker"}

def _is_resolved(s):    return str(s).strip().lower() in _RESOLVED_ST
def _is_open(s):        return str(s).strip().lower() in _OPEN_ST
def _is_blocked(s):     return str(s).strip().lower() in _BLOCKED_ST
def _is_bug(t):         return str(t).strip().lower() in _BUG_T
def _is_improvement(t): return str(t).strip().lower() in _IMPROVEMENT_T
def _is_high_prio(p):   return str(p).strip().lower() in _HIGH_P


def generate_pdf_report(df, rep_df, total_all, resolved_all, res_rate,
                         bugs_all, impr_all, open_all, n_rep,
                         fetched_at, project_keys,
                         filtered_frames=None):
    """
    filtered_frames: dict[str, DataFrame] — per-project filtered data.
                     Optional; if supplied, adds a per-project breakdown section.
    """
    buf = io.BytesIO()

    # ── Colours ───────────────────────────────────────────────
    C_BLUE   = colors.HexColor("#2563eb")
    C_DARK   = colors.HexColor("#0f172a")
    C_SLATE  = colors.HexColor("#475569")
    C_LIGHT  = colors.HexColor("#f0f4f8")
    C_GREEN  = colors.HexColor("#10b981")
    C_RED    = colors.HexColor("#ef4444")
    C_ORANGE = colors.HexColor("#f97316")
    C_PURPLE = colors.HexColor("#8b5cf6")
    C_TEAL   = colors.HexColor("#06b6d4")
    C_YELLOW = colors.HexColor("#eab308")
    C_WHITE  = colors.white
    C_BORDER = colors.HexColor("#e2e8f0")
    C_HDR_BG = colors.HexColor("#1e40af")

    PROJ_COLORS = ["#2563eb","#7c3aed","#059669","#ea580c","#0891b2","#db2777"]
    PRIORITY_COLORS = {
        "Highest": "#ef4444", "High": "#f97316",
        "Medium":  "#eab308", "Low":  "#22c55e", "Lowest": "#3b82f6",
    }
    STATUS_COLORS = {
        "NEW": "#3b82f6", "To Do": "#8b5cf6", "In Progress": "#f97316",
        "Assigned To Developer": "#06b6d4", "IN TESTING": "#eab308",
        "RE-TEST FAIL": "#ef4444", "ACCEPTED": "#10b981", "Done": "#22c55e",
        "Rejected": "#94a3b8", "BLOCKED": "#dc2626",
    }
    AGE_COLORS = {
        "0–7 days": "#22c55e", "8–30 days": "#84cc16",
        "31–90 days": "#eab308", "91–180 days": "#f97316", "180+ days": "#ef4444",
    }

    # ── Styles ────────────────────────────────────────────────
    def PS(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle      = PS("sTitle",     fontSize=26, textColor=C_WHITE,  fontName="Helvetica-Bold", leading=32, alignment=TA_CENTER)
    sSub        = PS("sSub",       fontSize=11, textColor=colors.HexColor("#bfdbfe"), fontName="Helvetica", leading=16, alignment=TA_CENTER)
    sSectionH   = PS("sSectionH",  fontSize=13, textColor=C_BLUE,   fontName="Helvetica-Bold", leading=18, spaceBefore=14, spaceAfter=6)
    sBody       = PS("sBody",      fontSize=9,  textColor=C_DARK,   fontName="Helvetica",      leading=13)
    sSmall      = PS("sSmall",     fontSize=8,  textColor=C_SLATE,  fontName="Helvetica",      leading=11)
    sBold       = PS("sBold",      fontSize=9,  textColor=C_DARK,   fontName="Helvetica-Bold", leading=13)
    sCenter     = PS("sCenter",    fontSize=9,  textColor=C_DARK,   fontName="Helvetica",      leading=13, alignment=TA_CENTER)
    sCenterBold = PS("sCenterBold",fontSize=9,  textColor=C_DARK,   fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
    sRight      = PS("sRight",     fontSize=9,  textColor=C_DARK,   fontName="Helvetica",      leading=13, alignment=TA_RIGHT)
    sWhite      = PS("sWhite",     fontSize=9,  textColor=C_WHITE,  fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
    sGreen      = PS("sGreen",     fontSize=9,  textColor=C_GREEN,  fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
    sRed        = PS("sRed",       fontSize=9,  textColor=C_RED,    fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
    sOrange     = PS("sOrange",    fontSize=9,  textColor=C_ORANGE, fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
    sBlue       = PS("sBlue",      fontSize=9,  textColor=C_BLUE,   fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)

    def hdr_style(bg=C_HDR_BG):
        return TableStyle([
            ("BACKGROUND",    (0,0), (-1,0),  bg),
            ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
            ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0),  9),
            ("ALIGN",         (0,0), (-1,0),  "CENTER"),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [C_WHITE, C_LIGHT]),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,1), (-1,-1), 8.5),
            ("GRID",          (0,0), (-1,-1), 0.4, C_BORDER),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ])

    story = []
    pw = A4[0] - 3*cm

    # ────────────────────────────────────────────────────────
    # COVER PAGE
    # ────────────────────────────────────────────────────────
    cover_data = [[Paragraph("Reporter Analytics Report", sTitle)]]
    cover_tbl  = Table(cover_data, colWidths=[pw])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), C_HDR_BG),
        ("TOPPADDING",   (0,0),(-1,-1), 28),
        ("BOTTOMPADDING",(0,0),(-1,-1), 28),
        ("LEFTPADDING",  (0,0),(-1,-1), 20),
        ("RIGHTPADDING", (0,0),(-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 8),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.3*cm))

    meta = [[
        Paragraph(f"Projects: <b>{project_keys}</b>",   sSmall),
        Paragraph(f"Generated: <b>{fetched_at}</b>",    sSmall),
        Paragraph(f"Total Issues: <b>{total_all:,}</b>",sSmall),
        Paragraph(f"Reporters: <b>{n_rep}</b>",         sSmall),
    ]]
    meta_tbl = Table(meta, colWidths=[pw/4]*4)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#eff6ff")),
        ("ALIGN",        (0,0),(-1,-1), "CENTER"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("GRID",         (0,0),(-1,-1), 0.4, C_BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ────────────────────────────────────────────────────────
    # SECTION 1 — EXECUTIVE SUMMARY KPIs
    # ────────────────────────────────────────────────────────
    blocked_all  = int(df["status"].apply(_is_blocked).sum())
    avg_res_s    = df["resolution_days"].dropna() if "resolution_days" in df.columns else pd.Series([], dtype=float)
    avg_res_days = round(avg_res_s.mean(), 1) if len(avg_res_s) > 0 else None
    avg_age      = round(df["age_days"].mean(), 1) if "age_days" in df.columns and len(df) > 0 else None

    story.append(Paragraph("1. Executive Summary", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    kpi_data = [
        [Paragraph("METRIC", sWhite), Paragraph("VALUE", sWhite),
         Paragraph("METRIC", sWhite), Paragraph("VALUE", sWhite)],
        [Paragraph("Total Issues",      sBold), Paragraph(f"{total_all:,}",     sBlue),
         Paragraph("Total Bugs",        sBold), Paragraph(f"{bugs_all:,}",      sRed)],
        [Paragraph("Improvements",      sBold), Paragraph(f"{impr_all:,}",      sBlue),
         Paragraph("Still Open (NEW)",  sBold), Paragraph(f"{open_all:,}",      sOrange)],
        [Paragraph("Resolved Issues",   sBold), Paragraph(f"{resolved_all:,}",  sGreen),
         Paragraph("Resolution Rate",   sBold), Paragraph(f"{res_rate}%",       sGreen)],
        [Paragraph("Blocked Issues",    sBold), Paragraph(f"{blocked_all}",     sRed if blocked_all>0 else sCenter),
         Paragraph("Avg Resolution",    sBold), Paragraph(f"{avg_res_days}d" if avg_res_days else "N/A", sOrange)],
        [Paragraph("Active Reporters",  sBold), Paragraph(f"{n_rep}",           sBlue),
         Paragraph("Avg Issue Age",     sBold), Paragraph(f"{avg_age}d" if avg_age else "N/A", sOrange)],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[pw*0.28, pw*0.22, pw*0.28, pw*0.22])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",    (0,0),(-1,0), C_WHITE),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("ALIGN",        (0,0),(-1,-1), "LEFT"),
        ("ALIGN",        (1,0),(1,-1), "CENTER"),
        ("ALIGN",        (3,0),(3,-1), "CENTER"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("GRID",         (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 10),
        ("LINEAFTER",    (1,1),(1,-1), 1.5, C_BORDER),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ────────────────────────────────────────────────────────
    # SECTION 2 — PROJECT-WISE BREAKDOWN (only if multi-project)
    # ────────────────────────────────────────────────────────
    section_num = 2
    if filtered_frames and len(filtered_frames) > 1:
        story.append(Paragraph(f"{section_num}. Project-wise Breakdown", sSectionH))
        story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

        proj_list = list(filtered_frames.keys())
        pj_hdr = [Paragraph("Project", sWhite),
                  Paragraph("Total", sWhite), Paragraph("Bugs", sWhite),
                  Paragraph("Improvements", sWhite), Paragraph("Resolved", sWhite),
                  Paragraph("Res %", sWhite), Paragraph("Open", sWhite),
                  Paragraph("Blocked", sWhite), Paragraph("Avg Res (d)", sWhite)]
        pj_rows = [pj_hdr]
        for i, proj in enumerate(proj_list):
            pf  = filtered_frames[proj]
            pt  = len(pf)
            pb  = int(pf["issue_type"].apply(_is_bug).sum()) if pt else 0
            pim = int(pf["issue_type"].apply(_is_improvement).sum()) if pt else 0
            pr  = int(pf["status"].apply(_is_resolved).sum()) if pt else 0
            prr = round(pr/pt*100, 1) if pt else 0
            po  = int(pf["status"].apply(_is_open).sum()) if pt else 0
            pbl = int(pf["status"].apply(_is_blocked).sum()) if pt else 0
            prd = pf["resolution_days"].dropna() if "resolution_days" in pf.columns else pd.Series([], dtype=float)
            prd_avg = f"{prd.mean():.1f}" if len(prd) > 0 else "—"
            pc_hex  = PROJ_COLORS[i % len(PROJ_COLORS)]
            pj_rows.append([
                Paragraph(f"<b>{proj}</b>", PS(f"pn{i}", fontSize=9, textColor=hex_to_rl(pc_hex), fontName="Helvetica-Bold", leading=13)),
                Paragraph(str(pt),    sCenter),
                Paragraph(str(pb),    sRed if pb>0 else sCenter),
                Paragraph(str(pim),   sBlue),
                Paragraph(str(pr),    sGreen),
                Paragraph(f"{prr}%",  sGreen if prr>=40 else sOrange),
                Paragraph(str(po),    sOrange if po>0 else sCenter),
                Paragraph(str(pbl),   sRed if pbl>0 else sCenter),
                Paragraph(prd_avg,    sCenter),
            ])
        pj_cw = [pw*0.14, pw*0.09, pw*0.09, pw*0.13, pw*0.10, pw*0.09, pw*0.09, pw*0.10, pw*0.12]
        pj_tbl = Table(pj_rows, colWidths=pj_cw, repeatRows=1)
        pj_tbl.setStyle(hdr_style())
        story.append(pj_tbl)
        story.append(Spacer(1, 0.6*cm))
        section_num += 1

    # ────────────────────────────────────────────────────────
    # SECTION — REPORTER LEADERBOARD
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Reporter Leaderboard", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
    section_num += 1

    lb_hdr = [
        Paragraph("Reporter",    sWhite), Paragraph("Total",      sWhite),
        Paragraph("Bugs",        sWhite), Paragraph("Improvements",sWhite),
        Paragraph("Resolved",    sWhite), Paragraph("Res %",       sWhite),
        Paragraph("Avg Age (d)", sWhite), Paragraph("High Prio",   sWhite),
        Paragraph("Retest Fail", sWhite), Paragraph("Blocked",     sWhite),
        Paragraph("Open",        sWhite),
    ]
    lb_rows = [lb_hdr]
    for _, r in rep_df.iterrows():
        avg_a     = f"{r['avg_age']:.0f}" if "avg_age" in r and pd.notna(r.get("avg_age")) else "—"
        age_color = "#ef4444" if avg_a != "—" and float(avg_a) > 90 else \
                    "#f97316" if avg_a != "—" and float(avg_a) > 30 else "#22c55e"
        lb_rows.append([
            Paragraph(r["reporter"],           sBold),
            Paragraph(str(int(r["total"])),    sBlue),
            Paragraph(str(int(r["bugs"])),     sRed),
            Paragraph(str(int(r["improv"])),   sBlue),
            Paragraph(str(int(r["resolved"])), sGreen),
            Paragraph(f"{r['res_pct']:.0f}%",  sGreen if r["res_pct"]>=40 else sOrange),
            Paragraph(avg_a, PS(f"aa_{r['reporter']}", fontSize=9,
                                textColor=hex_to_rl(age_color),
                                fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
            Paragraph(str(int(r["high_prio"])),   sOrange),
            Paragraph(str(int(r["retest_fail"])), sRed if r["retest_fail"]>0 else sCenter),
            Paragraph(str(int(r["blocked"])),     sRed if r["blocked"]>0 else sCenter),
            Paragraph(str(int(r["new_open"])),    sOrange if r["new_open"]>0 else sCenter),
        ])

    cw = [pw*0.17, pw*0.06, pw*0.06, pw*0.10, pw*0.08, pw*0.06,
          pw*0.08, pw*0.08, pw*0.09, pw*0.08, pw*0.08]
    lb_tbl = Table(lb_rows, colWidths=cw, repeatRows=1)
    lb_tbl.setStyle(hdr_style())
    story.append(lb_tbl)
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────
    # SECTION — BUG vs IMPROVEMENT
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Bug vs Improvement Breakdown", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
    section_num += 1

    bi_hdr = [
        Paragraph("Reporter",       sWhite), Paragraph("Total",        sWhite),
        Paragraph("Bugs",           sWhite), Paragraph("Bug %",        sWhite),
        Paragraph("Improvements",   sWhite), Paragraph("Impr %",       sWhite),
        Paragraph("Other Types",    sWhite),
    ]
    bi_rows = [bi_hdr]
    for _, r in rep_df.sort_values("total", ascending=False).iterrows():
        other   = int(r["total"]) - int(r["bugs"]) - int(r["improv"])
        bug_pct = round(r["bugs"]/r["total"]*100, 1) if r["total"] else 0
        imp_pct = round(r["improv"]/r["total"]*100, 1) if r["total"] else 0
        bi_rows.append([
            Paragraph(r["reporter"],          sBold),
            Paragraph(str(int(r["total"])),   sCenter),
            Paragraph(str(int(r["bugs"])),    sRed),
            Paragraph(f"{bug_pct}%",          sRed),
            Paragraph(str(int(r["improv"])), sBlue),
            Paragraph(f"{imp_pct}%",          sBlue),
            Paragraph(str(other),             sCenter),
        ])
    bi_cw = [pw*0.24, pw*0.12, pw*0.10, pw*0.10, pw*0.14, pw*0.14, pw*0.12]
    bi_tbl = Table(bi_rows, colWidths=bi_cw, repeatRows=1)
    bi_tbl.setStyle(hdr_style())
    story.append(bi_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ────────────────────────────────────────────────────────
    # SECTION — STATUS DISTRIBUTION
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Status Distribution per Reporter", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
    section_num += 1

    status_pivot = (df.groupby(["reporter","status"]).size()
                    .unstack(fill_value=0)
                    .reindex(index=rep_df["reporter"].tolist(), fill_value=0))
    stat_cols_list = list(status_pivot.columns)
    st_hdr  = [Paragraph("Reporter", sWhite)] + [Paragraph(s, sWhite) for s in stat_cols_list]
    st_rows = [st_hdr]
    for rep_name, row_s in status_pivot.iterrows():
        row_cells = [Paragraph(rep_name, sBold)]
        for s in stat_cols_list:
            val   = int(row_s.get(s, 0))
            c_hex = STATUS_COLORS.get(s, "#64748b")
            style = PS(f"st_{s}_{rep_name[:4]}", fontSize=8.5,
                       textColor=colors.HexColor(c_hex),
                       fontName="Helvetica-Bold" if val>0 else "Helvetica",
                       leading=13, alignment=TA_CENTER)
            row_cells.append(Paragraph(str(val) if val > 0 else "–", style))
        st_rows.append(row_cells)

    st_cw = [pw*0.22] + [(pw*0.78)/max(1, len(stat_cols_list))]*len(stat_cols_list)
    st_tbl = Table(st_rows, colWidths=st_cw, repeatRows=1)
    st_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C_HDR_BG),
        ("TEXTCOLOR",     (0,0),(-1,0),  C_WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  7.5),
        ("ALIGN",         (0,0),(-1,0),  "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTSIZE",      (0,1),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    story.append(st_tbl)
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────
    # SECTION — PRIORITY DISTRIBUTION
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Priority Distribution per Reporter", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
    section_num += 1

    prio_order_list = ["Highest","High","Medium","Low","Lowest"]
    prio_pivot = (df.groupby(["reporter","priority"]).size()
                  .unstack(fill_value=0)
                  .reindex(columns=prio_order_list, fill_value=0)
                  .reindex(index=rep_df["reporter"].tolist(), fill_value=0))
    pr_hdr  = [Paragraph("Reporter", sWhite)] + \
              [Paragraph(p, sWhite) for p in prio_order_list] + \
              [Paragraph("Total", sWhite)]
    pr_rows = [pr_hdr]
    for rep_name, row_p in prio_pivot.iterrows():
        row_cells = [Paragraph(rep_name, sBold)]
        for p in prio_order_list:
            val   = int(row_p.get(p, 0))
            c_hex = PRIORITY_COLORS.get(p, "#64748b")
            style = PS(f"pr_{p}_{rep_name[:4]}", fontSize=8.5,
                       textColor=colors.HexColor(c_hex),
                       fontName="Helvetica-Bold" if val>0 else "Helvetica",
                       leading=13, alignment=TA_CENTER)
            row_cells.append(Paragraph(str(val) if val > 0 else "–", style))
        row_cells.append(Paragraph(str(int(row_p.sum())), sCenterBold))
        pr_rows.append(row_cells)

    pr_cw = [pw*0.28, pw*0.12, pw*0.12, pw*0.12, pw*0.12, pw*0.12, pw*0.12]
    pr_tbl = Table(pr_rows, colWidths=pr_cw, repeatRows=1)
    pr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C_HDR_BG),
        ("TEXTCOLOR",     (0,0),(-1,0),  C_WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8.5),
        ("ALIGN",         (0,0),(-1,0),  "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("GRID",          (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("LINEAFTER",     (-2,0),(-2,-1), 1.5, C_BORDER),
    ]))
    story.append(pr_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ────────────────────────────────────────────────────────
    # SECTION — ISSUE AGE BUCKETS
    # ────────────────────────────────────────────────────────
    if "age_bucket" in df.columns:
        story.append(Paragraph(f"{section_num}. Issue Age Buckets (Open Issues)", sSectionH))
        story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
        section_num += 1

        open_issues = df[~df["status"].apply(_is_resolved)]
        if not open_issues.empty:
            age_grp = open_issues.groupby("age_bucket").size().reset_index(name="Count")
            age_grp["age_bucket"] = age_grp["age_bucket"].astype(str)
            age_hdr  = [Paragraph("Age Bucket", sWhite), Paragraph("Open Issues", sWhite),
                        Paragraph("% of Open", sWhite), Paragraph("Severity", sWhite)]
            age_rows = [age_hdr]
            tot_open = len(open_issues)
            for _, ar in age_grp.iterrows():
                bkt   = str(ar["age_bucket"])
                cnt   = int(ar["Count"])
                pct_v = round(cnt/tot_open*100, 1) if tot_open else 0
                c_hex = AGE_COLORS.get(bkt, "#64748b")
                sev   = ("🔴 Critical" if bkt == "180+ days" else
                         "🟠 High"    if bkt == "91–180 days" else
                         "🟡 Medium"  if bkt == "31–90 days" else
                         "🟢 Low")
                style = PS(f"ab_{bkt}", fontSize=9, textColor=hex_to_rl(c_hex),
                           fontName="Helvetica-Bold", leading=13)
                age_rows.append([
                    Paragraph(bkt,         style),
                    Paragraph(str(cnt),    sCenter),
                    Paragraph(f"{pct_v}%", sCenter),
                    Paragraph(sev,         PS(f"sv_{bkt}", fontSize=9, textColor=hex_to_rl(c_hex),
                                              fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
                ])
            age_cw = [pw*0.35, pw*0.20, pw*0.20, pw*0.25]
            age_tbl = Table(age_rows, colWidths=age_cw, repeatRows=1)
            age_tbl.setStyle(hdr_style())
            story.append(age_tbl)
            story.append(Spacer(1, 0.6*cm))

    # ────────────────────────────────────────────────────────
    # SECTION — AVG RESOLUTION TIME PER REPORTER
    # ────────────────────────────────────────────────────────
    if "resolution_days" in df.columns:
        res_time = (df.dropna(subset=["resolution_days"])
                      .groupby("reporter")["resolution_days"]
                      .mean().round(1).reset_index()
                      .sort_values("resolution_days"))
        if not res_time.empty:
            story.append(Paragraph(f"{section_num}. Avg Resolution Time per Reporter", sSectionH))
            story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
            section_num += 1

            rt_hdr  = [Paragraph("Reporter", sWhite), Paragraph("Avg Resolution (days)", sWhite),
                       Paragraph("Progress Bar", sWhite), Paragraph("Rating", sWhite)]
            rt_rows = [rt_hdr]
            max_rt  = res_time["resolution_days"].max()
            for _, row in res_time.iterrows():
                val   = row["resolution_days"]
                pct   = (val / max_rt * 100) if max_rt else 0
                c_hex = "#ef4444" if val > 14 else ("#eab308" if val > 7 else "#22c55e")
                rating = ("🔴 Slow" if val > 14 else ("🟡 Moderate" if val > 7 else "🟢 Fast"))
                rt_rows.append([
                    Paragraph(row["reporter"], sBold),
                    Paragraph(f"{val:.1f}d", PS(f"rt_{row['reporter'][:4]}", fontSize=9,
                                                textColor=hex_to_rl(c_hex), fontName="Helvetica-Bold",
                                                leading=13, alignment=TA_CENTER)),
                    mini_bar_drawing(pct, c_hex, width=160, height=9),
                    Paragraph(rating, PS(f"rtr_{row['reporter'][:4]}", fontSize=9,
                                         textColor=hex_to_rl(c_hex), fontName="Helvetica-Bold",
                                         leading=13, alignment=TA_CENTER)),
                ])
            rt_cw = [pw*0.30, pw*0.18, pw*0.32, pw*0.20]
            rt_tbl = Table(rt_rows, colWidths=rt_cw, repeatRows=1)
            rt_tbl.setStyle(hdr_style())
            story.append(rt_tbl)
            story.append(PageBreak())

    # ────────────────────────────────────────────────────────
    # SECTION — RESOLUTION RATE RANKING
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Resolution Rate Ranking", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))
    section_num += 1

    rr_hdr = [
        Paragraph("Rank",           sWhite), Paragraph("Reporter",       sWhite),
        Paragraph("Total Issues",   sWhite), Paragraph("Resolved",       sWhite),
        Paragraph("Resolution Rate",sWhite), Paragraph("Progress Bar",   sWhite),
        Paragraph("Status",         sWhite),
    ]
    rr_rows     = [rr_hdr]
    res_sorted  = rep_df.sort_values("res_pct", ascending=False).reset_index(drop=True)
    for i, (_, r) in enumerate(res_sorted.iterrows()):
        pct       = r["res_pct"]
        bar_color = "#10b981" if pct >= 60 else ("#eab308" if pct >= 30 else "#ef4444")
        bar       = mini_bar_drawing(pct, bar_color, width=100, height=8)
        if pct >= 60:
            status_txt = "🟢 Excellent"; st_style = sGreen
        elif pct >= 40:
            status_txt = "🟡 Good"
            st_style = PS("syellow", fontSize=9, textColor=colors.HexColor("#b45309"),
                          fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
        elif pct >= 20:
            status_txt = "🟠 Moderate"; st_style = sOrange
        else:
            status_txt = "🔴 Needs Work"; st_style = sRed
        medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
        rr_rows.append([
            Paragraph(medal, sCenterBold),
            Paragraph(r["reporter"], sBold),
            Paragraph(str(int(r["total"])), sCenter),
            Paragraph(str(int(r["resolved"])), sGreen),
            Paragraph(f"{pct:.1f}%", PS("rpct", fontSize=10,
                                         textColor=colors.HexColor(bar_color),
                                         fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
            bar,
            Paragraph(status_txt, st_style),
        ])
    rr_cw = [pw*0.07, pw*0.24, pw*0.11, pw*0.10, pw*0.13, pw*0.19, pw*0.16]
    rr_tbl = Table(rr_rows, colWidths=rr_cw, repeatRows=1)
    rr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C_HDR_BG),
        ("TEXTCOLOR",     (0,0),(-1,0),  C_WHITE),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0),  8.5),
        ("ALIGN",         (0,0),(-1,0),  "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 8.5),
        ("GRID",          (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("BACKGROUND",    (0,1),(6,1), colors.HexColor("#fef9c3")),
        ("BACKGROUND",    (0,2),(6,2), colors.HexColor("#f0fdf4")),
        ("BACKGROUND",    (0,3),(6,3), colors.HexColor("#fff7ed")),
    ]))
    story.append(rr_tbl)
    story.append(PageBreak())

    # ────────────────────────────────────────────────────────
    # SECTION — PER-REPORTER DEEP DIVE
    # ────────────────────────────────────────────────────────
    story.append(Paragraph(f"{section_num}. Per-Reporter Deep Dive", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=10))

    for idx, (_, r) in enumerate(rep_df.iterrows()):
        rep_name = r["reporter"]
        rdf_s    = df[df["reporter"] == rep_name]

        badge_txt = ("✅ Good Resolver" if r["res_pct"] >= 40 else
                     ("🚫 Has Blocked" if r["blocked"] > 0 else
                      ("⚠️ High Open Rate" if r["open_pct"] > 80 else "🔄 Active")))
        avg_a = f"{r['avg_age']:.0f}d" if "avg_age" in r and pd.notna(r.get("avg_age")) else "—"
        avg_rd = f"{r['avg_res_days']:.1f}d" if "avg_res_days" in r and pd.notna(r.get("avg_res_days")) else "—"

        header_data = [[
            Paragraph(f"<b>{rep_name}</b>",
                      PS("rh", fontSize=11, textColor=C_WHITE, fontName="Helvetica-Bold", leading=15)),
            Paragraph(f"Total: <b>{int(r['total'])}</b>  |  {badge_txt}  |  Avg Age: {avg_a}  |  Avg Res: {avg_rd}",
                      PS("rhs", fontSize=9, textColor=colors.HexColor("#bfdbfe"), fontName="Helvetica", leading=13)),
        ]]
        hdr_tbl = Table(header_data, colWidths=[pw*0.32, pw*0.68])
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#1e3a8a")),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",  (0,0),(-1,-1), 12),
            ("RIGHTPADDING", (0,0),(-1,-1), 12),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ("ROUNDEDCORNERS",(0,0),(-1,-1), 4),
        ]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 0.2*cm))

        stats_data = [[
            Paragraph(f"🐛 Bugs\n<b>{int(r['bugs'])}</b>",
                      PS(f"sb{idx}", fontSize=9, textColor=colors.HexColor("#dc2626"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"⬆ Improvements\n<b>{int(r['improv'])}</b>",
                      PS(f"si{idx}", fontSize=9, textColor=colors.HexColor("#2563eb"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"✅ Resolved\n<b>{int(r['resolved'])} ({r['res_pct']:.0f}%)</b>",
                      PS(f"sr{idx}", fontSize=9, textColor=colors.HexColor("#16a34a"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🔥 High Priority\n<b>{int(r['high_prio'])}</b>",
                      PS(f"shp{idx}", fontSize=9, textColor=colors.HexColor("#c2410c"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🔁 Retest Fail\n<b>{int(r['retest_fail'])}</b>",
                      PS(f"srf{idx}", fontSize=9, textColor=colors.HexColor("#be185d"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🚫 Blocked\n<b>{int(r['blocked'])}</b>",
                      PS(f"sbl{idx}", fontSize=9,
                         textColor=colors.HexColor("#dc2626") if r["blocked"]>0 else colors.HexColor("#94a3b8"),
                         fontName="Helvetica", leading=14, alignment=TA_CENTER)),
        ]]
        stats_tbl = Table(stats_data, colWidths=[pw/6]*6)
        stats_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#f8fafc")),
            ("GRID",         (0,0),(-1,-1), 0.4, C_BORDER),
            ("TOPPADDING",   (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("ALIGN",        (0,0),(-1,-1), "CENTER"),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(stats_tbl)
        story.append(Spacer(1, 0.2*cm))

        # Status & Priority side by side
        sc    = rdf_s["status"].value_counts()
        pc_r  = rdf_s["priority"].value_counts()
        empty = [Paragraph("", sSmall), Paragraph("", sSmall), Paragraph("", sSmall)]

        left_rows = [[
            Paragraph("Status",  PS("ls", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
            Paragraph("Count",   PS("lc", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
            Paragraph("%",       PS("lp", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
        ]]
        for s_name, cnt in sc.items():
            c_hex = STATUS_COLORS.get(s_name, "#64748b")
            pct_v = round(cnt/len(rdf_s)*100, 1) if len(rdf_s) else 0
            left_rows.append([
                Paragraph(s_name, PS(f"sn{idx}{s_name[:3]}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11)),
                Paragraph(str(cnt), PS(f"sc{idx}{s_name[:3]}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                Paragraph(f"{pct_v}%", sSmall),
            ])

        right_rows = [[
            Paragraph("Priority", PS("rp", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
            Paragraph("Count",    PS("rc", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
            Paragraph("%",        PS("rpp",fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
        ]]
        for p_name in prio_order_list:
            cnt = int(pc_r.get(p_name, 0))
            if cnt == 0:
                continue
            c_hex = PRIORITY_COLORS.get(p_name, "#64748b")
            pct_v = round(cnt/len(rdf_s)*100, 1) if len(rdf_s) else 0
            right_rows.append([
                Paragraph(p_name, PS(f"pn{idx}{p_name[:3]}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11)),
                Paragraph(str(cnt), PS(f"pc{idx}{p_name[:3]}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                Paragraph(f"{pct_v}%", sSmall),
            ])

        max_r = max(len(left_rows), len(right_rows))
        while len(left_rows)  < max_r: left_rows.append(empty[:])
        while len(right_rows) < max_r: right_rows.append(empty[:])

        side_cw = [pw*0.22, pw*0.08, pw*0.08, pw*0.02, pw*0.22, pw*0.08, pw*0.08]
        side_rows = []
        for i in range(max_r):
            lr = left_rows[i]  if i < len(left_rows)  else empty
            rr = right_rows[i] if i < len(right_rows) else empty
            side_rows.append(lr + [Paragraph("", sSmall)] + rr)

        side_tbl = Table(side_rows, colWidths=side_cw)
        side_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(2,0),  colors.HexColor("#1e40af")),
            ("BACKGROUND",    (4,0),(6,0),  colors.HexColor("#1e40af")),
            ("TEXTCOLOR",     (0,0),(2,0),  C_WHITE),
            ("TEXTCOLOR",     (4,0),(6,0),  C_WHITE),
            ("ROWBACKGROUNDS",(0,1),(2,-1), [C_WHITE, C_LIGHT]),
            ("ROWBACKGROUNDS",(4,1),(6,-1), [C_WHITE, C_LIGHT]),
            ("GRID",          (0,0),(2,-1), 0.4, C_BORDER),
            ("GRID",          (4,0),(6,-1), 0.4, C_BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 5),
            ("RIGHTPADDING",  (0,0),(-1,-1), 5),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(side_tbl)
        story.append(Spacer(1, 0.3*cm))

        if idx < len(rep_df) - 1:
            story.append(HRFlowable(width=pw, thickness=0.5, color=C_BORDER, spaceAfter=10))

    # ────────────────────────────────────────────────────────
    # FOOTER PAGE
    # ────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 1*cm))
    footer_data = [[Paragraph(
        f"<b>Jira Reporter Analytics Report</b><br/>"
        f"Projects: {project_keys}<br/>"
        f"Generated on: {fetched_at}<br/>"
        f"Total Issues Analysed: {total_all:,} across {n_rep} reporters",
        PS("footer", fontSize=9, textColor=C_SLATE, fontName="Helvetica", leading=14, alignment=TA_CENTER)
    )]]
    footer_tbl = Table(footer_data, colWidths=[pw])
    footer_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#f0f4f8")),
        ("GRID",         (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",   (0,0),(-1,-1), 20),
        ("BOTTOMPADDING",(0,0),(-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
    ]))
    story.append(footer_tbl)

    # ── Build ──────────────────────────────────────────────
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_SLATE)
        canvas.drawString(1.5*cm, 1*cm, f"Jira Reporter Dashboard  |  Projects: {project_keys}  |  {fetched_at}")
        canvas.drawRightString(A4[0]-1.5*cm, 1*cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.8*cm)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf
