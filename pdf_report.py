import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
def hex_to_rl(h):
    h = h.lstrip("#")
    return colors.HexColor("#" + h)

def mini_bar_drawing(pct, color_hex, width=100, height=10):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#f1f5f9"), strokeColor=None))
    fill_w = max(0, min(width, width * pct / 100))
    if fill_w > 0:
        d.add(Rect(0, 0, fill_w, height, fillColor=colors.HexColor(color_hex), strokeColor=None))
    return d

def generate_pdf_report(df, rep_df, total_all, resolved_all, res_rate,
                         bugs_all, impr_all, open_all, n_rep,
                         fetched_at, project_keys):
    buf = io.BytesIO()

    # ── Colours ───────────────────────────────────────────────
    C_BLUE    = colors.HexColor("#2563eb")
    C_DARK    = colors.HexColor("#0f172a")
    C_SLATE   = colors.HexColor("#475569")
    C_LIGHT   = colors.HexColor("#f0f4f8")
    C_GREEN   = colors.HexColor("#10b981")
    C_RED     = colors.HexColor("#ef4444")
    C_ORANGE  = colors.HexColor("#f97316")
    C_PURPLE  = colors.HexColor("#8b5cf6")
    C_TEAL    = colors.HexColor("#06b6d4")
    C_YELLOW  = colors.HexColor("#eab308")
    C_WHITE   = colors.white
    C_BORDER  = colors.HexColor("#e2e8f0")
    C_HDR_BG  = colors.HexColor("#1e40af")

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

    # ── Styles ────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    def PS(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle     = PS("sTitle",     fontSize=26, textColor=C_WHITE,   fontName="Helvetica-Bold",  leading=32, alignment=TA_CENTER)
    sSub       = PS("sSub",       fontSize=11, textColor=colors.HexColor("#bfdbfe"), fontName="Helvetica", leading=16, alignment=TA_CENTER)
    sSectionH  = PS("sSectionH",  fontSize=13, textColor=C_BLUE,    fontName="Helvetica-Bold",  leading=18, spaceBefore=14, spaceAfter=6)
    sBody      = PS("sBody",      fontSize=9,  textColor=C_DARK,    fontName="Helvetica",       leading=13)
    sSmall     = PS("sSmall",     fontSize=8,  textColor=C_SLATE,   fontName="Helvetica",       leading=11)
    sBold      = PS("sBold",      fontSize=9,  textColor=C_DARK,    fontName="Helvetica-Bold",  leading=13)
    sCenter    = PS("sCenter",    fontSize=9,  textColor=C_DARK,    fontName="Helvetica",       leading=13, alignment=TA_CENTER)
    sCenterBold= PS("sCenterBold",fontSize=9,  textColor=C_DARK,    fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)
    sRight     = PS("sRight",     fontSize=9,  textColor=C_DARK,    fontName="Helvetica",       leading=13, alignment=TA_RIGHT)
    sWhite     = PS("sWhite",     fontSize=9,  textColor=C_WHITE,   fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)
    sGreen     = PS("sGreen",     fontSize=9,  textColor=C_GREEN,   fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)
    sRed       = PS("sRed",       fontSize=9,  textColor=C_RED,     fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)
    sOrange    = PS("sOrange",    fontSize=9,  textColor=C_ORANGE,  fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)
    sBlue      = PS("sBlue",      fontSize=9,  textColor=C_BLUE,    fontName="Helvetica-Bold",  leading=13, alignment=TA_CENTER)

    # ── Common table styles ───────────────────────────────────
    def hdr_style(bg=C_HDR_BG):
        return TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), bg),
            ("TEXTCOLOR",    (0,0), (-1,0), C_WHITE),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,0), 9),
            ("ALIGN",        (0,0), (-1,0), "CENTER"),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
            ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",     (0,1), (-1,-1), 8.5),
            ("GRID",         (0,0), (-1,-1), 0.4, C_BORDER),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("ROUNDEDCORNERS",(0,0),(-1,-1), 2),
        ])

    story = []
    pw = A4[0] - 3*cm   # usable page width

    # ════════════════════════════════════════════════════
    # COVER PAGE
    # ════════════════════════════════════════════════════
    # Blue header block
    cover_data = [[Paragraph("Reporter Analytics Report", sTitle)]]
    cover_tbl = Table(cover_data, colWidths=[pw])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), C_HDR_BG),
        ("TOPPADDING",  (0,0), (-1,-1), 28),
        ("BOTTOMPADDING",(0,0),(-1,-1), 28),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING",(0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 8),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.3*cm))

    meta = [
        [Paragraph(f"Projects: <b>{project_keys}</b>", sSmall),
         Paragraph(f"Generated: <b>{fetched_at}</b>", sSmall),
         Paragraph(f"Total Issues: <b>{total_all:,}</b>", sSmall),
         Paragraph(f"Reporters: <b>{n_rep}</b>", sSmall)],
    ]
    meta_tbl = Table(meta, colWidths=[pw/4]*4)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#eff6ff")),
        ("ALIGN",       (0,0),(-1,-1), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",  (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ════════════════════════════════════════════════════
    # SECTION 1 — EXECUTIVE SUMMARY KPIs
    # ════════════════════════════════════════════════════
    story.append(Paragraph("1. Executive Summary", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    kpi_data = [
        [Paragraph("METRIC", sWhite), Paragraph("VALUE", sWhite),
         Paragraph("METRIC", sWhite), Paragraph("VALUE", sWhite)],
        [Paragraph("Total Issues", sBold),       Paragraph(f"{total_all:,}", sBlue),
         Paragraph("Total Bugs", sBold),          Paragraph(f"{bugs_all:,}", sRed)],
        [Paragraph("Improvements", sBold),        Paragraph(f"{impr_all:,}", sBlue),
         Paragraph("Still Open (NEW)", sBold),    Paragraph(f"{open_all:,}", sOrange)],
        [Paragraph("Resolved Issues", sBold),     Paragraph(f"{resolved_all:,}", sGreen),
         Paragraph("Resolution Rate", sBold),     Paragraph(f"{res_rate}%", sGreen)],
        [Paragraph("Active Reporters", sBold),    Paragraph(f"{n_rep}", sBlue),
         Paragraph("Bug Rate", sBold),            Paragraph(f"{round(bugs_all/total_all*100,1) if total_all else 0}%", sRed)],
    ]
    kpi_tbl = Table(kpi_data, colWidths=[pw*0.28, pw*0.22, pw*0.28, pw*0.22])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0), (-1,0), C_WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("ALIGN",       (1,0), (1,-1), "CENTER"),
        ("ALIGN",       (3,0), (3,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("GRID",        (0,0), (-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
        ("LINEAFTER",   (1,1), (1,-1), 1.5, C_BORDER),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ════════════════════════════════════════════════════
    # SECTION 2 — REPORTER LEADERBOARD
    # ════════════════════════════════════════════════════
    story.append(Paragraph("2. Reporter Leaderboard", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    lb_hdr = [
        Paragraph("Reporter", sWhite),
        Paragraph("Total", sWhite),
        Paragraph("Bugs", sWhite),
        Paragraph("Improvements", sWhite),
        Paragraph("Resolved", sWhite),
        Paragraph("Res %", sWhite),
        Paragraph("High Prio", sWhite),
        Paragraph("Retest Fail", sWhite),
        Paragraph("Blocked", sWhite),
        Paragraph("Open (NEW)", sWhite),
    ]
    lb_rows = [lb_hdr]
    for _, r in rep_df.iterrows():
        badge = "✅ Good" if r["res_pct"] >= 40 else ("🚫 Blocked" if r["blocked"] > 0 else "🔄 Active")
        lb_rows.append([
            Paragraph(r["reporter"], sBold),
            Paragraph(str(int(r["total"])),       sBlue),
            Paragraph(str(int(r["bugs"])),         sRed),
            Paragraph(str(int(r["improv"])),       PS("c1", fontSize=9, textColor=C_BLUE, fontName="Helvetica", leading=13, alignment=TA_CENTER)),
            Paragraph(str(int(r["resolved"])),     sGreen),
            Paragraph(f"{r['res_pct']:.0f}%",     sGreen if r["res_pct"]>=40 else sOrange),
            Paragraph(str(int(r["high_prio"])),   sOrange),
            Paragraph(str(int(r["retest_fail"])), sRed if r["retest_fail"]>0 else sCenter),
            Paragraph(str(int(r["blocked"])),     sRed if r["blocked"]>0 else sCenter),
            Paragraph(str(int(r["new_open"])),    sOrange if r["new_open"]>0 else sCenter),
        ])

    cw = [pw*0.20, pw*0.07, pw*0.07, pw*0.11, pw*0.09, pw*0.07, pw*0.09, pw*0.10, pw*0.09, pw*0.11]
    lb_tbl = Table(lb_rows, colWidths=cw, repeatRows=1)
    lb_tbl.setStyle(hdr_style())
    lb_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0),(-1,0), C_WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 8),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1),(-1,-1), 8),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("LEFTPADDING", (0,0),(-1,-1), 5),
        ("RIGHTPADDING",(0,0),(-1,-1), 5),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    story.append(lb_tbl)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════
    # SECTION 3 — BUG vs IMPROVEMENT per REPORTER
    # ════════════════════════════════════════════════════
    story.append(Paragraph("3. Bug vs Improvement Breakdown per Reporter", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    bi_hdr = [
        Paragraph("Reporter", sWhite),
        Paragraph("Total Issues", sWhite),
        Paragraph("Bugs", sWhite),
        Paragraph("Bug %", sWhite),
        Paragraph("Improvements", sWhite),
        Paragraph("Improvement %", sWhite),
        Paragraph("Other Types", sWhite),
    ]
    bi_rows = [bi_hdr]
    for _, r in rep_df.sort_values("total", ascending=False).iterrows():
        other = int(r["total"]) - int(r["bugs"]) - int(r["improv"])
        bug_pct = round(r["bugs"]/r["total"]*100, 1) if r["total"] else 0
        imp_pct = round(r["improv"]/r["total"]*100, 1) if r["total"] else 0
        bi_rows.append([
            Paragraph(r["reporter"], sBold),
            Paragraph(str(int(r["total"])),  sCenter),
            Paragraph(str(int(r["bugs"])),   sRed),
            Paragraph(f"{bug_pct}%",         sRed),
            Paragraph(str(int(r["improv"])), sBlue),
            Paragraph(f"{imp_pct}%",         sBlue),
            Paragraph(str(other),            sCenter),
        ])
    bi_cw = [pw*0.24, pw*0.12, pw*0.10, pw*0.10, pw*0.14, pw*0.14, pw*0.12]
    bi_tbl = Table(bi_rows, colWidths=bi_cw, repeatRows=1)
    bi_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0),(-1,0), C_WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 8.5),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1),(-1,-1), 8.5),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0),(-1,-1), 7),
        ("RIGHTPADDING",(0,0),(-1,-1), 7),
    ]))
    story.append(bi_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ════════════════════════════════════════════════════
    # SECTION 4 — STATUS DISTRIBUTION
    # ════════════════════════════════════════════════════
    story.append(Paragraph("4. Status Distribution per Reporter", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    status_pivot = (df.groupby(["reporter","status"]).size()
                    .unstack(fill_value=0)
                    .reindex(index=rep_df["reporter"].tolist(), fill_value=0))
    stat_cols_list = list(status_pivot.columns)
    st_hdr = [Paragraph("Reporter", sWhite)] + [Paragraph(s, sWhite) for s in stat_cols_list]
    st_rows = [st_hdr]
    for rep_name, row_s in status_pivot.iterrows():
        row_cells = [Paragraph(rep_name, sBold)]
        for s in stat_cols_list:
            val = int(row_s.get(s, 0))
            c_hex = STATUS_COLORS.get(s, "#64748b")
            style = PS(f"st_{s}", fontSize=8.5, textColor=colors.HexColor(c_hex),
                       fontName="Helvetica-Bold" if val>0 else "Helvetica",
                       leading=13, alignment=TA_CENTER)
            row_cells.append(Paragraph(str(val) if val > 0 else "–", style))
        st_rows.append(row_cells)

    n_st_cols = len(stat_cols_list) + 1
    st_cw = [pw*0.22] + [(pw*0.78)/len(stat_cols_list)]*len(stat_cols_list)
    st_tbl = Table(st_rows, colWidths=st_cw, repeatRows=1)
    st_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0),(-1,0), C_WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 7.5),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1),(-1,-1), 8),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 4),
        ("RIGHTPADDING",(0,0),(-1,-1), 4),
    ]))
    story.append(st_tbl)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════
    # SECTION 5 — PRIORITY DISTRIBUTION
    # ════════════════════════════════════════════════════
    story.append(Paragraph("5. Priority Distribution per Reporter", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    prio_order_list = ["Highest","High","Medium","Low","Lowest"]
    prio_pivot = (df.groupby(["reporter","priority"]).size()
                  .unstack(fill_value=0)
                  .reindex(columns=prio_order_list, fill_value=0)
                  .reindex(index=rep_df["reporter"].tolist(), fill_value=0))
    pr_hdr = [Paragraph("Reporter", sWhite)] + [Paragraph(p, sWhite) for p in prio_order_list] + [Paragraph("Total", sWhite)]
    pr_rows = [pr_hdr]
    for rep_name, row_p in prio_pivot.iterrows():
        row_cells = [Paragraph(rep_name, sBold)]
        for p in prio_order_list:
            val = int(row_p.get(p, 0))
            c_hex = PRIORITY_COLORS.get(p, "#64748b")
            style = PS(f"pr_{p}", fontSize=8.5, textColor=colors.HexColor(c_hex),
                       fontName="Helvetica-Bold" if val>0 else "Helvetica",
                       leading=13, alignment=TA_CENTER)
            row_cells.append(Paragraph(str(val) if val > 0 else "–", style))
        row_cells.append(Paragraph(str(int(row_p.sum())), sCenterBold))
        pr_rows.append(row_cells)

    pr_cw = [pw*0.28, pw*0.12, pw*0.12, pw*0.12, pw*0.12, pw*0.12, pw*0.12]
    pr_tbl = Table(pr_rows, colWidths=pr_cw, repeatRows=1)
    pr_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0),(-1,0), C_WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 8.5),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1),(-1,-1), 8.5),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
        ("RIGHTPADDING",(0,0),(-1,-1), 6),
        ("LINEAFTER",   (-2,0),(-2,-1), 1.5, C_BORDER),
    ]))
    story.append(pr_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ════════════════════════════════════════════════════
    # SECTION 6 — RESOLUTION RATE RANKING
    # ════════════════════════════════════════════════════
    story.append(Paragraph("6. Resolution Rate Ranking", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=8))

    rr_hdr = [
        Paragraph("Rank", sWhite),
        Paragraph("Reporter", sWhite),
        Paragraph("Total Issues", sWhite),
        Paragraph("Resolved", sWhite),
        Paragraph("Resolution Rate", sWhite),
        Paragraph("Progress Bar", sWhite),
        Paragraph("Status", sWhite),
    ]
    rr_rows = [rr_hdr]
    res_sorted = rep_df.sort_values("res_pct", ascending=False).reset_index(drop=True)
    for i, (_, r) in enumerate(res_sorted.iterrows()):
        pct = r["res_pct"]
        bar_color = "#10b981" if pct >= 60 else ("#eab308" if pct >= 30 else "#ef4444")
        bar = mini_bar_drawing(pct, bar_color, width=100, height=8)
        if pct >= 60:
            status_txt = "🟢 Excellent"
            st_style = sGreen
        elif pct >= 40:
            status_txt = "🟡 Good"
            st_style = PS("syellow", fontSize=9, textColor=colors.HexColor("#b45309"), fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)
        elif pct >= 20:
            status_txt = "🟠 Moderate"
            st_style = sOrange
        else:
            status_txt = "🔴 Needs Work"
            st_style = sRed
        medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
        rr_rows.append([
            Paragraph(medal, sCenterBold),
            Paragraph(r["reporter"], sBold),
            Paragraph(str(int(r["total"])), sCenter),
            Paragraph(str(int(r["resolved"])), sGreen),
            Paragraph(f"{pct:.1f}%", PS("rpct", fontSize=10, textColor=colors.HexColor(bar_color), fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
            bar,
            Paragraph(status_txt, st_style),
        ])
    rr_cw = [pw*0.07, pw*0.24, pw*0.11, pw*0.10, pw*0.13, pw*0.19, pw*0.16]
    rr_tbl = Table(rr_rows, colWidths=rr_cw, repeatRows=1)
    rr_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), C_HDR_BG),
        ("TEXTCOLOR",   (0,0),(-1,0), C_WHITE),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,0), 8.5),
        ("ALIGN",       (0,0),(-1,0), "CENTER"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_LIGHT]),
        ("FONTNAME",    (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,1),(-1,-1), 8.5),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0),(-1,-1), 6),
        ("RIGHTPADDING",(0,0),(-1,-1), 6),
        ("BACKGROUND",  (0,1),(6,1), colors.HexColor("#fef9c3")),
        ("BACKGROUND",  (0,2),(6,2), colors.HexColor("#f0fdf4")),
        ("BACKGROUND",  (0,3),(6,3), colors.HexColor("#fff7ed")),
    ]))
    story.append(rr_tbl)
    story.append(PageBreak())

    # ════════════════════════════════════════════════════
    # SECTION 7 — PER-REPORTER DEEP DIVE
    # ════════════════════════════════════════════════════
    story.append(Paragraph("7. Per-Reporter Deep Dive", sSectionH))
    story.append(HRFlowable(width=pw, thickness=1.5, color=C_BLUE, spaceAfter=10))

    for idx, (_, r) in enumerate(rep_df.iterrows()):
        rep_name = r["reporter"]
        rdf_s    = df[df["reporter"] == rep_name]

        # Reporter header card
        badge_txt = ("✅ Good Resolver" if r["res_pct"]>=40
                     else ("🚫 Has Blocked" if r["blocked"]>0
                     else ("⚠️ High Open Rate" if r["open_pct"]>80 else "🔄 Active")))
        header_data = [[
            Paragraph(f"<b>{rep_name}</b>", PS("rh", fontSize=11, textColor=C_WHITE, fontName="Helvetica-Bold", leading=15)),
            Paragraph(f"Total: <b>{int(r['total'])}</b>  |  {badge_txt}",
                      PS("rhs", fontSize=9, textColor=colors.HexColor("#bfdbfe"), fontName="Helvetica", leading=13)),
        ]]
        hdr_tbl = Table(header_data, colWidths=[pw*0.45, pw*0.55])
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#1e3a8a")),
            ("TOPPADDING",  (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING", (0,0),(-1,-1), 12),
            ("RIGHTPADDING",(0,0),(-1,-1), 12),
            ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
            ("ROUNDEDCORNERS",(0,0),(-1,-1), 4),
        ]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 0.2*cm))

        # Stats row
        stats_data = [[
            Paragraph(f"🐛 Bugs\n<b>{int(r['bugs'])}</b>",       PS("sb", fontSize=9, textColor=colors.HexColor("#dc2626"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"⬆ Improvements\n<b>{int(r['improv'])}</b>", PS("si", fontSize=9, textColor=colors.HexColor("#2563eb"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"✅ Resolved\n<b>{int(r['resolved'])} ({r['res_pct']:.0f}%)</b>", PS("sr", fontSize=9, textColor=colors.HexColor("#16a34a"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🔥 High Priority\n<b>{int(r['high_prio'])}</b>", PS("shp", fontSize=9, textColor=colors.HexColor("#c2410c"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🔁 Retest Fail\n<b>{int(r['retest_fail'])}</b>", PS("srf", fontSize=9, textColor=colors.HexColor("#be185d"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
            Paragraph(f"🚫 Blocked\n<b>{int(r['blocked'])}</b>",   PS("sbl", fontSize=9, textColor=colors.HexColor("#dc2626") if r['blocked']>0 else colors.HexColor("#94a3b8"), fontName="Helvetica", leading=14, alignment=TA_CENTER)),
        ]]
        stats_tbl = Table(stats_data, colWidths=[pw/6]*6)
        stats_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#f8fafc")),
            ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
            ("TOPPADDING",  (0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("ALIGN",       (0,0),(-1,-1), "CENTER"),
            ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ]))
        story.append(stats_tbl)
        story.append(Spacer(1, 0.2*cm))

        # Status & Priority side by side
        sc = rdf_s["status"].value_counts()
        pc_r = rdf_s["priority"].value_counts()

        left_rows  = [[Paragraph("Status", PS("ls", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                       Paragraph("Count", PS("lc", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                       Paragraph("%", PS("lp", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER))]]
        for s_name, cnt in sc.items():
            c_hex = STATUS_COLORS.get(s_name, "#64748b")
            pct_v = round(cnt/len(rdf_s)*100, 1) if len(rdf_s) else 0
            left_rows.append([
                Paragraph(s_name, PS(f"sn{s_name}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11)),
                Paragraph(str(cnt), PS(f"sc{s_name}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                Paragraph(f"{pct_v}%", sSmall),
            ])

        right_rows = [[Paragraph("Priority", PS("rp", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                       Paragraph("Count", PS("rc", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                       Paragraph("%", PS("rpp", fontSize=8, textColor=C_WHITE, fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER))]]
        for p_name in prio_order_list:
            cnt = int(pc_r.get(p_name, 0))
            if cnt == 0:
                continue
            c_hex = PRIORITY_COLORS.get(p_name, "#64748b")
            pct_v = round(cnt/len(rdf_s)*100, 1) if len(rdf_s) else 0
            right_rows.append([
                Paragraph(p_name, PS(f"pn{p_name}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11)),
                Paragraph(str(cnt), PS(f"pc{p_name}", fontSize=8, textColor=colors.HexColor(c_hex), fontName="Helvetica-Bold", leading=11, alignment=TA_CENTER)),
                Paragraph(f"{pct_v}%", sSmall),
            ])

        max_r = max(len(left_rows), len(right_rows))
        empty = [Paragraph("", sSmall), Paragraph("", sSmall), Paragraph("", sSmall)]
        while len(left_rows)  < max_r: left_rows.append(empty)
        while len(right_rows) < max_r: right_rows.append(empty)

        side_cw = [pw*0.22, pw*0.08, pw*0.08, pw*0.02, pw*0.22, pw*0.08, pw*0.08]

        def make_side_tbl(left_data, right_data, lw, rw):
            rows = []
            for i in range(max_r):
                lr = left_data[i] if i < len(left_data) else empty
                rr = right_data[i] if i < len(right_data) else empty
                rows.append(lr + [Paragraph("", sSmall)] + rr)
            tbl = Table(rows, colWidths=side_cw)
            tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0),(2,0), colors.HexColor("#1e40af")),
                ("BACKGROUND",  (4,0),(6,0), colors.HexColor("#1e40af")),
                ("TEXTCOLOR",   (0,0),(2,0), C_WHITE),
                ("TEXTCOLOR",   (4,0),(6,0), C_WHITE),
                ("ROWBACKGROUNDS",(0,1),(2,-1), [C_WHITE, C_LIGHT]),
                ("ROWBACKGROUNDS",(4,1),(6,-1), [C_WHITE, C_LIGHT]),
                ("GRID",        (0,0),(2,-1), 0.4, C_BORDER),
                ("GRID",        (4,0),(6,-1), 0.4, C_BORDER),
                ("TOPPADDING",  (0,0),(-1,-1), 4),
                ("BOTTOMPADDING",(0,0),(-1,-1), 4),
                ("LEFTPADDING", (0,0),(-1,-1), 5),
                ("RIGHTPADDING",(0,0),(-1,-1), 5),
                ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
            ]))
            return tbl

        story.append(make_side_tbl(left_rows, right_rows, pw*0.38, pw*0.38))
        story.append(Spacer(1, 0.3*cm))

        if idx < len(rep_df) - 1:
            story.append(HRFlowable(width=pw, thickness=0.5, color=C_BORDER, spaceAfter=10))

    # ════════════════════════════════════════════════════
    # FOOTER NOTE
    # ════════════════════════════════════════════════════
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
        ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#f0f4f8")),
        ("GRID",        (0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0),(-1,-1), 20),
        ("BOTTOMPADDING",(0,0),(-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
    ]))
    story.append(footer_tbl)

    # ── Build ─────────────────────────────────────────
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(C_SLATE)
        canvas.drawString(1.5*cm, 1*cm, f"Jira Reporter Dashboard  |  {fetched_at}")
        canvas.drawRightString(A4[0]-1.5*cm, 1*cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.8*cm)
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf
