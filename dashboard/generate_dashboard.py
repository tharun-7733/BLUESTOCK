"""
Bluestock Mutual Fund Dashboard Generator
==========================================
Generates 4 Power BI-style dashboard pages as high-resolution PNGs
and exports them as a combined PDF report.

Deliverables:
  - dashboard/page1_industry_overview.png
  - dashboard/page2_fund_performance.png
  - dashboard/page3_investor_analytics.png
  - dashboard/page4_sip_market_trends.png
  - dashboard/Dashboard.pdf
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime

warnings.filterwarnings("ignore")
matplotlib.rcParams["font.family"] = "DejaVu Sans"

# ─── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
DASH_DIR = os.path.join(BASE_DIR, "dashboard")
os.makedirs(DASH_DIR, exist_ok=True)

# ─── BLUESTOCK COLOUR THEME ───────────────────────────────────────────────────
THEME = {
    "bg":           "#0A0F1E",
    "card_bg":      "#111827",
    "panel_bg":     "#141D2E",
    "accent1":      "#1E6FD9",
    "accent2":      "#00C2FF",
    "accent3":      "#F59E0B",
    "accent4":      "#10B981",
    "accent5":      "#EF4444",
    "text_primary": "#F1F5F9",
    "text_muted":   "#94A3B8",
    "grid":         "#1E293B",
    "border":       "#1E3A5F",
}

PALETTE = [THEME["accent1"], THEME["accent2"], THEME["accent3"],
           THEME["accent4"], THEME["accent5"], "#A78BFA", "#FB923C", "#34D399"]

DPI = 180
FIG_W, FIG_H = 22, 13.5

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
def load_data():
    print("Loading datasets...")
    fund  = pd.read_csv(os.path.join(DATA_DIR, "01_fund_master.csv"))
    nav   = pd.read_csv(os.path.join(DATA_DIR, "02_nav_history.csv"), parse_dates=["date"])
    aum   = pd.read_csv(os.path.join(DATA_DIR, "03_aum_by_fund_house.csv"), parse_dates=["date"])
    sip   = pd.read_csv(os.path.join(DATA_DIR, "04_monthly_sip_inflows.csv"))
    cat   = pd.read_csv(os.path.join(DATA_DIR, "05_category_inflows.csv"))
    folio = pd.read_csv(os.path.join(DATA_DIR, "06_industry_folio_count.csv"))
    perf  = pd.read_csv(os.path.join(DATA_DIR, "07_scheme_performance.csv"))
    txn   = pd.read_csv(os.path.join(DATA_DIR, "08_investor_transactions.csv"), parse_dates=["transaction_date"])
    bench = pd.read_csv(os.path.join(DATA_DIR, "10_benchmark_indices.csv"), parse_dates=["date"])

    sip["date"]   = pd.to_datetime(sip["month"], format="%Y-%m", errors="coerce")
    cat["date"]   = pd.to_datetime(cat["month"], format="%Y-%m", errors="coerce")
    month_col = "month" if "month" in folio.columns else folio.columns[0]
    folio["date"] = pd.to_datetime(folio[month_col], format="%Y-%m", errors="coerce")

    print(f"  fund_master: {len(fund):,}  nav: {len(nav):,}  aum: {len(aum):,}")
    print(f"  sip: {len(sip):,}  cat: {len(cat):,}  folio: {len(folio):,}")
    print(f"  performance: {len(perf):,}  transactions: {len(txn):,}  benchmark: {len(bench):,}")
    return fund, nav, aum, sip, cat, folio, perf, txn, bench


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def styled_fig(title: str):
    fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=THEME["bg"])
    ax_hdr = fig.add_axes([0, 0.94, 1, 0.06], facecolor=THEME["accent1"])
    ax_hdr.set_xlim(0, 1); ax_hdr.set_ylim(0, 1); ax_hdr.axis("off")
    ax_hdr.text(0.02, 0.5, "BLUESTOCK", fontsize=22, fontweight="bold",
                color="white", va="center", ha="left")
    ax_hdr.text(0.98, 0.5, title, fontsize=16, fontweight="bold",
                color="white", va="center", ha="right")
    ax_ftr = fig.add_axes([0, 0, 1, 0.03], facecolor=THEME["card_bg"])
    ax_ftr.axis("off")
    ax_ftr.text(0.5, 0.5,
                f"Bluestock Mutual Fund Analytics  |  FY2024-25  |  Generated {datetime.now().strftime('%d %b %Y')}",
                fontsize=8, color=THEME["text_muted"], ha="center", va="center")
    return fig


def kpi_card(fig, rect, label, value, sub="", colour=None):
    colour = colour or THEME["accent1"]
    ax = fig.add_axes(rect, facecolor=THEME["card_bg"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), 0.04, 1, linewidth=0,
                                boxstyle="square,pad=0", facecolor=colour))
    ax.text(0.12, 0.72, value, fontsize=24, fontweight="bold", color=colour, va="center")
    ax.text(0.12, 0.42, label, fontsize=10, color=THEME["text_primary"], va="center")
    if sub:
        ax.text(0.12, 0.18, sub, fontsize=8, color=THEME["text_muted"], va="center")


def style_ax(ax, xlabel="", ylabel="", title=""):
    ax.set_facecolor(THEME["panel_bg"])
    ax.tick_params(colors=THEME["text_muted"], labelsize=8)
    ax.set_xlabel(xlabel, fontsize=9, color=THEME["text_muted"], labelpad=4)
    ax.set_ylabel(ylabel, fontsize=9, color=THEME["text_muted"], labelpad=4)
    ax.set_title(title, fontsize=11, fontweight="bold",
                 color=THEME["text_primary"], pad=10, loc="left")
    for spine in ax.spines.values():
        spine.set_edgecolor(THEME["grid"])
    ax.grid(True, color=THEME["grid"], linewidth=0.5, alpha=0.6)
    ax.tick_params(axis="both", length=0)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1
# ══════════════════════════════════════════════════════════════════════════════
def page1_industry_overview(aum, sip, folio, fund, txn):
    print("\nGenerating Page 1 - Industry Overview...")
    fig = styled_fig("Page 1  |  Industry Overview")

    kpis = [
        ("₹81 L Cr",    "Total AUM",           "Assets Under Management",      THEME["accent1"]),
        ("₹31,000 Cr",  "SIP Monthly Inflow",  "FY2024-25 Average",            THEME["accent2"]),
        ("26.12 Cr",    "Total Folios",         "Active Investor Accounts",     THEME["accent4"]),
        ("1,908",       "Active Schemes",       "Across all AMCs & categories", THEME["accent3"]),
    ]
    for i, (val, lbl, sub, col) in enumerate(kpis):
        kpi_card(fig, [0.03 + i * 0.235, 0.77, 0.215, 0.145], lbl, val, sub, col)

    # AUM Trend Line
    ax1 = fig.add_axes([0.03, 0.37, 0.56, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax1, title="Industry AUM Trend  (Rs Lakh Crore)  2022-2025")
    aum_monthly = aum.groupby("date")["aum_lakh_crore"].sum().reset_index().sort_values("date")
    aum_monthly = aum_monthly[aum_monthly["date"] >= "2022-01-01"]
    ax1.fill_between(aum_monthly["date"], aum_monthly["aum_lakh_crore"], alpha=0.25, color=THEME["accent1"])
    ax1.plot(aum_monthly["date"], aum_monthly["aum_lakh_crore"],
             color=THEME["accent2"], linewidth=2.5, marker="o", markersize=2)
    ax1.set_ylabel("AUM (Rs L Cr)", fontsize=9, color=THEME["text_muted"])
    ax1.tick_params(axis="x", rotation=30)

    # AUM by AMC Bar
    ax2 = fig.add_axes([0.63, 0.37, 0.34, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax2, title="AUM by AMC  (Rs Crore)")
    latest_date = aum["date"].max()
    amc_aum = aum[aum["date"] == latest_date].sort_values("aum_crore", ascending=True).tail(12)
    ax2.barh(amc_aum["fund_house"], amc_aum["aum_crore"] / 100000,
             color=PALETTE[:len(amc_aum)], height=0.65)
    ax2.set_xlabel("AUM (Rs L Cr)", fontsize=8, color=THEME["text_muted"])
    ax2.tick_params(axis="y", labelsize=7)

    # SIP Monthly
    ax3 = fig.add_axes([0.03, 0.05, 0.56, 0.28], facecolor=THEME["panel_bg"])
    style_ax(ax3, title="Monthly SIP Inflows  (Rs Crore)  2022-2025")
    sip_clean = sip.dropna(subset=["date"]).sort_values("date")
    ax3.bar(sip_clean["date"], sip_clean["sip_inflow_crore"], color=THEME["accent1"], width=20, alpha=0.85)
    ax3.plot(sip_clean["date"], sip_clean["sip_inflow_crore"].rolling(3).mean(),
             color=THEME["accent3"], linewidth=2, label="3M Moving Avg")
    ax3.legend(fontsize=8, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"])
    ax3.tick_params(axis="x", rotation=30)

    # Folio Growth
    ax4 = fig.add_axes([0.63, 0.05, 0.34, 0.28], facecolor=THEME["panel_bg"])
    style_ax(ax4, title="Industry Folio Growth  (Crore)")
    folio_clean = folio.dropna(subset=["date"]).sort_values("date")
    if "total_folios_crore" in folio_clean.columns:
        ax4.fill_between(folio_clean["date"], folio_clean["total_folios_crore"],
                         alpha=0.3, color=THEME["accent4"])
        ax4.plot(folio_clean["date"], folio_clean["total_folios_crore"],
                 color=THEME["accent4"], linewidth=2.5)
    ax4.tick_params(axis="x", rotation=30)

    out = os.path.join(DASH_DIR, "page1_industry_overview.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=THEME["bg"])
    plt.close(fig)
    print(f"  Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2
# ══════════════════════════════════════════════════════════════════════════════
def page2_fund_performance(perf, nav, bench, fund):
    print("\nGenerating Page 2 - Fund Performance...")
    fig = styled_fig("Page 2  |  Fund Performance")

    perf_clean = perf.dropna(subset=["return_3yr_pct", "std_dev_ann_pct", "aum_crore"])
    perf_clean = perf_clean[perf_clean["aum_crore"] > 0]

    # Scatter: Risk vs Return
    ax1 = fig.add_axes([0.03, 0.45, 0.40, 0.44], facecolor=THEME["panel_bg"])
    style_ax(ax1, "3Y Return (%)", "Std Dev Ann (%)", "Risk vs Return  (bubble = AUM)")
    cat_list = perf_clean["category"].unique()
    cat_colors = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cat_list)}
    for cat_name, grp in perf_clean.groupby("category"):
        sizes = (grp["aum_crore"] / grp["aum_crore"].max() * 400).clip(20, 400)
        ax1.scatter(grp["return_3yr_pct"], grp["std_dev_ann_pct"],
                    s=sizes, alpha=0.65, color=cat_colors[cat_name],
                    label=cat_name, edgecolors="white", linewidth=0.3)
    ax1.axvline(perf_clean["return_3yr_pct"].median(), color=THEME["text_muted"],
                linestyle="--", linewidth=0.8, alpha=0.7)
    ax1.axhline(perf_clean["std_dev_ann_pct"].median(), color=THEME["text_muted"],
                linestyle="--", linewidth=0.8, alpha=0.7)
    ax1.legend(fontsize=6.5, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"],
               loc="upper right", framealpha=0.8, ncol=2)

    # Fund Scorecard Table
    ax2 = fig.add_axes([0.47, 0.45, 0.50, 0.44], facecolor=THEME["panel_bg"])
    ax2.axis("off")
    ax2.set_title("Fund Scorecard  (Top 15 by 3Y Return)", fontsize=11,
                  fontweight="bold", color=THEME["text_primary"], pad=10, loc="left")
    top15 = perf_clean.nlargest(15, "return_3yr_pct")[
        ["scheme_name", "category", "return_3yr_pct", "return_1yr_pct",
         "sharpe_ratio", "aum_crore", "morningstar_rating"]].copy()
    top15["scheme_name"] = top15["scheme_name"].str[:30]
    top15["morningstar_rating"] = top15["morningstar_rating"].apply(
        lambda x: "★" * int(x) if pd.notna(x) else "")
    top15.columns = ["Fund Name", "Category", "3Y Ret%", "1Y Ret%", "Sharpe", "AUM Cr", "Rating"]
    for col in ["3Y Ret%", "1Y Ret%", "Sharpe"]:
        top15[col] = top15[col].round(2)
    top15["AUM Cr"] = top15["AUM Cr"].apply(lambda x: f"{x:,.0f}")
    tbl = ax2.table(cellText=top15.values.tolist(), colLabels=list(top15.columns),
                    cellLoc="center", loc="center", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_facecolor(THEME["card_bg"] if r % 2 == 0 else THEME["panel_bg"])
        cell.set_edgecolor(THEME["grid"])
        cell.set_text_props(
            color=THEME["accent2"] if r == 0 else THEME["text_primary"],
            fontweight="bold" if r == 0 else "normal")

    # NAV vs Benchmark
    ax3 = fig.add_axes([0.03, 0.05, 0.60, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax3, title="NAV vs Benchmark  -  SBI Bluechip Fund  (Indexed to 100)")
    sbi_nav = nav[nav["amfi_code"] == 119551].sort_values("date")
    nifty   = bench[bench["index_name"] == "NIFTY50"].sort_values("date")
    if len(sbi_nav) > 0:
        base_nav = sbi_nav["nav"].iloc[0]
        ax3.plot(sbi_nav["date"], sbi_nav["nav"] / base_nav * 100,
                 color=THEME["accent1"], linewidth=2, label="SBI Bluechip NAV")
    if len(nifty) > 0:
        base_nifty = nifty["close_value"].iloc[0]
        nifty_trim = nifty[nifty["date"] >= sbi_nav["date"].min()] if len(sbi_nav) > 0 else nifty
        ax3.plot(nifty_trim["date"], nifty_trim["close_value"] / base_nifty * 100,
                 color=THEME["accent3"], linewidth=1.5, linestyle="--", label="NIFTY 50")
    ax3.legend(fontsize=9, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"])
    ax3.set_ylabel("Indexed Value (Base=100)", fontsize=9, color=THEME["text_muted"])
    ax3.tick_params(axis="x", rotation=30)

    # Sharpe Distribution
    ax4 = fig.add_axes([0.67, 0.05, 0.30, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax4, title="Sharpe Ratio Distribution")
    sharpe_data = perf_clean["sharpe_ratio"].dropna()
    ax4.hist(sharpe_data, bins=25, color=THEME["accent1"], alpha=0.8, edgecolor=THEME["bg"])
    ax4.axvline(sharpe_data.mean(), color=THEME["accent3"], linestyle="--",
                linewidth=1.5, label=f"Mean: {sharpe_data.mean():.2f}")
    ax4.legend(fontsize=9, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"])
    ax4.set_xlabel("Sharpe Ratio", fontsize=9, color=THEME["text_muted"])

    out = os.path.join(DASH_DIR, "page2_fund_performance.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=THEME["bg"])
    plt.close(fig)
    print(f"  Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3
# ══════════════════════════════════════════════════════════════════════════════
def page3_investor_analytics(txn):
    print("\nGenerating Page 3 - Investor Analytics...")
    fig = styled_fig("Page 3  |  Investor Analytics")
    donut_colors = [THEME["accent1"], THEME["accent3"], THEME["accent5"]]

    # Bar: State
    ax1 = fig.add_axes([0.03, 0.45, 0.38, 0.44], facecolor=THEME["panel_bg"])
    style_ax(ax1, title="Transaction Amount by State  (Rs Crore)")
    state_txn = txn.groupby("state")["amount_inr"].sum().sort_values(ascending=True).tail(15) / 1e7
    ax1.barh(state_txn.index, state_txn.values,
             color=[PALETTE[i % len(PALETTE)] for i in range(len(state_txn))], height=0.7)
    ax1.set_xlabel("Amount (Rs Crore)", fontsize=9, color=THEME["text_muted"])
    ax1.tick_params(axis="y", labelsize=7.5)

    # Donut: Transaction type split
    ax2 = fig.add_axes([0.44, 0.50, 0.26, 0.38], facecolor=THEME["bg"])
    ax2.set_facecolor(THEME["bg"])
    ax2.set_title("Transaction Mix", fontsize=11, fontweight="bold",
                  color=THEME["text_primary"], pad=10, loc="left")
    txn_split = txn.groupby("transaction_type")["amount_inr"].sum()
    wedges, texts, autotexts = ax2.pie(
        txn_split.values, labels=txn_split.index,
        autopct="%1.1f%%", startangle=90,
        colors=donut_colors, pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor=THEME["bg"], linewidth=2))
    for t in texts:
        t.set_color(THEME["text_primary"]); t.set_fontsize(9)
    for at in autotexts:
        at.set_color("white"); at.set_fontsize(8); at.set_fontweight("bold")
    ax2.axis("equal")

    # Bar: Age group vs avg SIP
    ax3 = fig.add_axes([0.72, 0.45, 0.25, 0.44], facecolor=THEME["panel_bg"])
    style_ax(ax3, title="Avg SIP Amount by Age Group  (Rs)")
    sip_age = (txn[txn["transaction_type"] == "SIP"]
               .groupby("age_group")["amount_inr"].mean().sort_index())
    bars = ax3.bar(range(len(sip_age)), sip_age.values,
                   color=PALETTE[:len(sip_age)], width=0.6)
    ax3.set_xticks(range(len(sip_age)))
    ax3.set_xticklabels(sip_age.index, rotation=30, fontsize=8)
    for bar in bars:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2, h + 50,
                 f"Rs{h:,.0f}", ha="center", va="bottom", fontsize=7, color=THEME["text_muted"])

    # Monthly Txn Volume Line
    ax4 = fig.add_axes([0.03, 0.05, 0.46, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax4, title="Monthly Transaction Volume  (Count)")
    txn["month"] = txn["transaction_date"].dt.to_period("M").dt.to_timestamp()
    monthly_vol = txn.groupby(["month", "transaction_type"]).size().reset_index(name="count")
    for i, ttype in enumerate(["SIP", "Lumpsum", "Redemption"]):
        sub = monthly_vol[monthly_vol["transaction_type"] == ttype].sort_values("month")
        ax4.plot(sub["month"], sub["count"], label=ttype, color=donut_colors[i], linewidth=2)
    ax4.legend(fontsize=9, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"])
    ax4.tick_params(axis="x", rotation=30)

    # City Tier Breakdown
    ax5 = fig.add_axes([0.53, 0.05, 0.44, 0.34], facecolor=THEME["panel_bg"])
    style_ax(ax5, title="Transaction Amount by City Tier & Type  (Rs Crore)")
    tier_txn = (txn.groupby(["city_tier", "transaction_type"])["amount_inr"]
                .sum().unstack(fill_value=0) / 1e7)
    x = np.arange(len(tier_txn))
    width = 0.25
    for i, col in enumerate(tier_txn.columns):
        ax5.bar(x + i * width, tier_txn[col], width=width,
                label=col, color=donut_colors[i % 3], alpha=0.85)
    ax5.set_xticks(x + width)
    ax5.set_xticklabels(tier_txn.index, fontsize=9)
    ax5.legend(fontsize=9, facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"])
    ax5.set_ylabel("Amount (Rs Crore)", fontsize=9, color=THEME["text_muted"])

    out = os.path.join(DASH_DIR, "page3_investor_analytics.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=THEME["bg"])
    plt.close(fig)
    print(f"  Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4
# ══════════════════════════════════════════════════════════════════════════════
def page4_sip_market_trends(sip, cat, bench):
    print("\nGenerating Page 4 - SIP & Market Trends...")
    fig = styled_fig("Page 4  |  SIP & Market Trends")

    sip_clean = sip.dropna(subset=["date"]).sort_values("date")
    nifty     = bench[bench["index_name"] == "NIFTY50"].sort_values("date")
    cat_clean = cat.dropna(subset=["date"])

    # Dual-Axis: SIP + Nifty
    ax1 = fig.add_axes([0.03, 0.50, 0.60, 0.40], facecolor=THEME["panel_bg"])
    style_ax(ax1, title="SIP Monthly Inflows  vs  NIFTY 50  (2022-2025)")
    ax1.bar(sip_clean["date"], sip_clean["sip_inflow_crore"],
            width=20, color=THEME["accent1"], alpha=0.75, label="SIP Inflow (Rs Cr)")
    ax1.set_ylabel("SIP Inflow (Rs Crore)", fontsize=9, color=THEME["accent1"])
    ax1.yaxis.label.set_color(THEME["accent1"])
    ax1.tick_params(axis="x", rotation=30)

    ax1b = ax1.twinx()
    ax1b.set_facecolor("none")
    nifty_monthly = nifty.set_index("date")["close_value"].resample("ME").last().reset_index()
    ax1b.plot(nifty_monthly["date"], nifty_monthly["close_value"],
              color=THEME["accent3"], linewidth=2.5, label="NIFTY 50", zorder=5)
    ax1b.set_ylabel("NIFTY 50 Level", fontsize=9, color=THEME["accent3"])
    ax1b.tick_params(colors=THEME["accent3"])
    ax1b.yaxis.label.set_color(THEME["accent3"])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9,
               facecolor=THEME["card_bg"], labelcolor=THEME["text_muted"], loc="upper left")

    # Top 5 Categories FY25
    ax2 = fig.add_axes([0.67, 0.50, 0.30, 0.40], facecolor=THEME["panel_bg"])
    style_ax(ax2, title="Top 5 Categories  -  Net Inflow FY25  (Rs Cr)")
    fy25 = cat_clean[cat_clean["date"] >= "2024-04-01"]
    top5 = (fy25.groupby("category")["net_inflow_crore"]
            .sum().sort_values(ascending=False).head(5))
    ax2.barh(top5.index[::-1], top5.values[::-1], color=PALETTE[:5], height=0.6)
    for i, (idx, val) in enumerate(zip(top5.index[::-1], top5.values[::-1])):
        ax2.text(val + 50, i, f"Rs{val:,.0f}", va="center", fontsize=8, color=THEME["text_muted"])
    ax2.set_xlabel("Net Inflow (Rs Crore)", fontsize=9, color=THEME["text_muted"])
    ax2.tick_params(axis="y", labelsize=8.5)

    # Category Heatmap
    cat_clean2 = cat_clean.copy()
    cat_clean2["ym"] = cat_clean2["date"].dt.to_period("M")
    pivot = (cat_clean2.groupby(["category", "ym"])["net_inflow_crore"]
             .sum().unstack(fill_value=0))
    pivot.columns = [str(c) for c in pivot.columns]
    pivot = pivot.iloc[:, -18:]

    cmap = LinearSegmentedColormap.from_list(
        "bluestock", [THEME["accent5"], THEME["bg"], THEME["accent4"]], N=256)

    ax3 = fig.add_axes([0.03, 0.06, 0.92, 0.37], facecolor=THEME["panel_bg"])
    ax3.set_title("Category Inflow Heatmap  (Rs Crore Monthly  -  Last 18 Months)",
                  fontsize=11, fontweight="bold", color=THEME["text_primary"], pad=10, loc="left")
    im = ax3.imshow(pivot.values, aspect="auto", cmap=cmap,
                    vmin=pivot.values.min(), vmax=pivot.values.max())
    ax3.set_yticks(range(len(pivot.index)))
    ax3.set_yticklabels(pivot.index, fontsize=8.5, color=THEME["text_primary"])
    ax3.set_xticks(range(len(pivot.columns)))
    ax3.set_xticklabels(pivot.columns, rotation=60, fontsize=7.5,
                        color=THEME["text_muted"], ha="right")
    ax3.tick_params(length=0)
    for spine in ax3.spines.values():
        spine.set_visible(False)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = pivot.values[i, j]
            ax3.text(j, i, f"{v:,.0f}", ha="center", va="center",
                     fontsize=5.5, color="white" if abs(v) > 1500 else THEME["text_muted"])
    fig.colorbar(im, ax=ax3, orientation="vertical", fraction=0.01, pad=0.01)

    out = os.path.join(DASH_DIR, "page4_sip_market_trends.png")
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=THEME["bg"])
    plt.close(fig)
    print(f"  Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# PDF EXPORT
# ══════════════════════════════════════════════════════════════════════════════
def export_pdf(page_paths):
    print("\nExporting Dashboard.pdf...")
    pdf_path = os.path.join(DASH_DIR, "Dashboard.pdf")
    with PdfPages(pdf_path) as pdf:
        for path in page_paths:
            img = plt.imread(path)
            fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=THEME["bg"])
            ax  = fig.add_axes([0, 0, 1, 1])
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, dpi=DPI, bbox_inches="tight", facecolor=THEME["bg"])
            plt.close(fig)
        d = pdf.infodict()
        d["Title"]        = "Bluestock Mutual Fund Dashboard"
        d["Author"]       = "Bluestock Analytics"
        d["Subject"]      = "Mutual Fund Industry Analysis FY2024-25"
        d["CreationDate"] = datetime.now()
    print(f"  Saved: {pdf_path}")
    return pdf_path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Bluestock Mutual Fund Dashboard Generator")
    print("=" * 60)

    fund, nav, aum, sip, cat, folio, perf, txn, bench = load_data()

    pages = []
    pages.append(page1_industry_overview(aum, sip, folio, fund, txn))
    pages.append(page2_fund_performance(perf, nav, bench, fund))
    pages.append(page3_investor_analytics(txn))
    pages.append(page4_sip_market_trends(sip, cat, bench))
    export_pdf(pages)

    print("\n" + "=" * 60)
    print("  All deliverables generated in dashboard/")
    print("=" * 60)
    print("  page1_industry_overview.png")
    print("  page2_fund_performance.png")
    print("  page3_investor_analytics.png")
    print("  page4_sip_market_trends.png")
    print("  Dashboard.pdf")
    print("=" * 60)
