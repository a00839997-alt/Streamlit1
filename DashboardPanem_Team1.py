import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import datetime
 
# PAGE CONFIG
st.set_page_config(
    page_title="Panem Bakery - Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# PALETTE
C_DARK  = "#3B2A1A"
C_BROWN = "#7B4F2E"
C_GOLD  = "#C8A97E"
C_CREAM = "#FAF6F1"
C_SAND  = "#D4B896"
C_LINE  = "#8B6914"
C_MUTED = "#9E8B78"
 
# GLOBAL CSS
st.markdown(f"""
<style>
  .stApp {{ background-color: {C_CREAM}; }}
 
  section[data-testid="stSidebar"] {{
      background-color: {C_DARK};
  }}
  section[data-testid="stSidebar"] * {{
      color: {C_CREAM} !important;
  }}
 
  /* all text in main content area stays dark */
  .main p, .main span, .main label,
  .main h1, .main h2, .main h3, .main h4, .main h5,
  .main .stMarkdown p, .main .stMarkdown span,
  .main .stCaption, .main [data-testid="stText"],
  .block-container p, .block-container span, .block-container label {{
      color: {C_DARK} !important;
  }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stFileUploader label,
  section[data-testid="stSidebar"] .stNumberInput label,
  section[data-testid="stSidebar"] .stTextInput label {{
      color: {C_GOLD} !important;
      font-size: 0.78rem;
      letter-spacing: 0.5px;
  }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
      background-color: white !important;
  }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
      color: {C_DARK} !important;
  }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] div {{
      color: {C_DARK} !important;
  }}
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
      fill: {C_BROWN} !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] span,
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] p {{
      color: {C_MUTED} !important;
  }}
  section[data-testid="stSidebar"] div[data-testid="stFileUploadDropzone"] button span {{
      color: {C_DARK} !important;
  }}
 
  .header-bar {{
      background-color: {C_DARK};
      color: {C_CREAM};
      padding: 16px 28px;
      border-radius: 10px;
      margin-bottom: 18px;
  }}
  .header-bar h2 {{ margin: 0; font-size: 1.4rem; letter-spacing: 0.3px; }}
  .header-bar p  {{ margin: 4px 0 0; font-size: 0.8rem; color: {C_GOLD}; }}
 
  .kpi-card {{
      background: white;
      border-radius: 10px;
      padding: 18px 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      border-left: 4px solid {C_GOLD};
      margin-bottom: 6px;
  }}
  .kpi-label {{ font-size: 0.70rem; color: {C_MUTED}; text-transform: uppercase; letter-spacing: 1px; }}
  .kpi-value {{ font-size: 1.9rem; color: {C_DARK}; font-weight: 700; line-height: 1.1; }}
  .kpi-sub   {{ font-size: 0.74rem; color: {C_MUTED}; margin-top: 2px; }}
 
  .section-title {{ font-size: 0.98rem; font-weight: 600; color: {C_DARK}; margin-bottom: 2px; }}
  .section-sub   {{ font-size: 0.76rem; color: {C_MUTED}; margin-bottom: 10px; }}
 
  .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
  .stTabs [data-baseweb="tab"] {{
      background: transparent;
      border-radius: 20px;
      padding: 6px 20px;
      color: {C_BROWN};
      font-weight: 500;
      font-size: 0.88rem;
  }}
  .stTabs [aria-selected="true"] {{
      background-color: {C_BROWN} !important;
      color: white !important;
  }}
 
  .entry-box {{
      background: white;
      border-radius: 10px;
      padding: 18px 22px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      margin-bottom: 14px;
      border-top: 3px solid {C_BROWN};
  }}
  .entry-title {{ font-size: 0.95rem; font-weight: 600; color: {C_DARK}; margin-bottom: 8px; }}
 
  div[data-testid="stFileUploadDropzone"] {{
      background-color: #fff8f2 !important;
      border: 1.5px dashed {C_GOLD} !important;
      border-radius: 8px !important;
  }}
 
  div[data-testid="stMetric"] {{
      background: white;
      border-radius: 10px;
      padding: 12px 16px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.06);
  }}
  div[data-testid="stMetricLabel"] {{ color: {C_MUTED}; font-size: 0.72rem; text-transform: uppercase; }}
  div[data-testid="stMetricValue"] {{ color: {C_DARK}; font-weight: 700; }}
 
  div[data-testid="stAlert"] {{ border-radius: 8px; }}
  hr {{ border-color: {C_SAND}; }}
  .stDataFrame {{ border-radius: 8px; overflow: hidden; }}
 
  /* labels in main content area (NOT sidebar) */
  .main div[data-testid="stNumberInput"] label,
  .main div[data-testid="stDateInput"] label,
  .main div[data-testid="stSelectbox"] label,
  .main div[data-testid="stTextInput"] label,
  .main .stForm label,
  section.main label {{
      color: {C_DARK} !important;
  }}
 
  /* number inputs & date inputs: dark text on white bg */
  div[data-testid="stNumberInput"] input,
  div[data-testid="stDateInput"] input,
  div[data-baseweb="input"] input {{
      color: {C_DARK} !important;
      background-color: white !important;
  }}
  div[data-testid="stNumberInput"] div[data-baseweb="input"],
  div[data-testid="stDateInput"] div[data-baseweb="input"] {{
      background-color: white !important;
      border-color: {C_SAND} !important;
  }}
  /* form submit button: Panem brown instead of red */
  div[data-testid="stForm"] button[kind="primaryFormSubmit"],
  div[data-testid="stForm"] button[data-testid="baseButton-primaryFormSubmit"] {{
      background-color: {C_BROWN} !important;
      border-color: {C_BROWN} !important;
      color: white !important;
  }}
  div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover {{
      background-color: {C_DARK} !important;
      border-color: {C_DARK} !important;
  }}
</style>
""", unsafe_allow_html=True)
 
 
# HELPER: matplotlib defaults
def fig_defaults(ax, fig):
    fig.patch.set_facecolor(C_CREAM)
    ax.set_facecolor(C_CREAM)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#DDD")
    ax.tick_params(colors=C_DARK, labelsize=8)
    ax.yaxis.label.set_color(C_DARK)
    ax.xaxis.label.set_color(C_DARK)
 
 
# SESSION STATE
if "manual_sales" not in st.session_state:
    st.session_state.manual_sales = {}
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "new_weekly" not in st.session_state:
    st.session_state.new_weekly = {}
 
 
# SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:16px 0 20px;'>
      <img src='data:image/png;base64,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'
           style='width:140px; height:auto; display:block; margin:0 auto 6px;'
           alt='Panem logo'>
      <div style='font-size:0.68rem; color:#9E8B78; letter-spacing:3px; margin-top:2px;'>BAKERY & BISTRO</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.72rem; color:{C_GOLD}; letter-spacing:1px; margin-bottom:6px;'>FILTERS</div>",
        unsafe_allow_html=True,
    )
 
    BRANCHES = ["Kavia", "Carreta", "Zambrano", "Credi-Club", "Nativa", "QIN", "Punto-Valle"]
    PRODUCTS = ["Vanilla concha", "Chocolate concha", "Chilaquiles Panem", "Oat cookie", "Glazed donut"]
 
    branch  = st.selectbox("Branch",       BRANCHES)
    product = st.selectbox("Star product", PRODUCTS)
    period  = st.selectbox("Period",       ["Last 90 days", "Last 30 days", "Last 6 months", "Full year"])
 
    period_days = {"Last 90 days": 90, "Last 30 days": 30, "Last 6 months": 182, "Full year": 365}[period]
 
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.72rem; color:{C_GOLD}; letter-spacing:1px; margin-bottom:6px;'>DATA MANAGEMENT</div>",
        unsafe_allow_html=True,
    )
 
    uploaded = st.file_uploader(
        "Upload sales CSV",
        type=["csv"],
        help="Expected columns: operating_date, item, quantity, sucursal",
    )
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded)
            df_up.columns = [c.strip().lower() for c in df_up.columns]
            rename_map = {
                "branch": "sucursal", "sucursal": "sucursal",
                "product": "item", "item": "item", "producto": "item",
                "date": "operating_date", "fecha": "operating_date", "operating_date": "operating_date",
                "qty": "quantity", "cantidad": "quantity", "quantity": "quantity", "units": "quantity",
            }
            df_up = df_up.rename(columns={c: rename_map[c] for c in df_up.columns if c in rename_map})
            if "operating_date" in df_up.columns:
                df_up["operating_date"] = pd.to_datetime(df_up["operating_date"], errors="coerce")
            st.session_state.uploaded_df = df_up
            st.success(f"OK - {len(df_up):,} rows loaded")
        except Exception as e:
            st.error(f"Error reading file: {e}")
 
    if st.session_state.uploaded_df is not None:
        if st.button("Clear uploaded data", use_container_width=True):
            st.session_state.uploaded_df = None
            st.rerun()
 
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.68rem; color:{C_MUTED};'>Dashboard v2.0 - May 2026</div>",
        unsafe_allow_html=True,
    )
 
 
# HEADER
st.markdown(f"""
<div class="header-bar">
  <h2>Panem Bakery - Management Dashboard</h2>
  <p>Branch: <strong style="color:white">{branch}</strong> &nbsp;|&nbsp;
     Product: <strong style="color:white">{product}</strong> &nbsp;|&nbsp;
     Period: {period} &nbsp;|&nbsp;
     Last update: {datetime.date.today().strftime("%b %d, %Y")}</p>
</div>
""", unsafe_allow_html=True)
 
 
# DEMO DATA
np.random.seed(hash(branch) % 9999)
 
dates_main  = pd.date_range(end="2026-02-12", periods=period_days)
daily_sales = np.random.normal(loc=23, scale=3, size=period_days).clip(13, 32)
moving_avg7 = pd.Series(daily_sales).rolling(7, min_periods=1).mean().values
 
days_labels  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
sales_by_day = np.array([14800, 14200, 13900, 15200, 17800, 21000, 12500]) * (0.8 + np.random.rand() * 0.4)
 
top_products = ["Vanilla concha", "Choco. concha", "Chilaquiles", "Oat cookie", "Glazed donut"]
share_vals   = [30, 22, 18, 16, 14]
donut_colors = [C_DARK, C_GOLD, "#8B6440", C_SAND, "#EDD9BE"]
 
dates_hist = pd.date_range(end="2026-05-12", periods=120)
hist_sales = np.random.normal(280, 35, 120).clip(180, 390)
 
weeks    = [f"W{i:02d}" for i in range(1, 53)]
weekly_v = np.random.normal(2100, 300, 52).clip(1200, 2800).astype(int)
 
forecast_days = ["Mon 13", "Tue 14", "Wed 15", "Thu 16", "Fri 17", "Sat 18", "Sun 19"]
forecast_vals = [280, 295, 270, 310, 318, 336, 253]
fc_colors     = [C_GOLD, C_GOLD, C_GOLD, C_BROWN, C_BROWN, C_DARK, C_SAND]
 
hw_products = ["VANILLA CONCHA", "CHOCOLATE CONCHA", "GLAZED DONUT", "BRIOCHE W/ NUTS", "PAN DE MUERTO", "CHILAQUILES"]
week_plus = {
    "Week +1": [284, 294, 267, 265, 265, 262],
    "Week +2": [283, 204, 267, 264, 264, 262],
    "Week +3": [283, 294, 266, 263, 263, 261],
    "Week +4": [283, 294, 266, 262, 262, 261],
}
 
branches_ml = ["Carreta", "Zambrano", "Credi-Club", "Kavia", "Nativa", "QIN", "Punto-Valle"]
mae_vals    = [2.1, 2.8, 2.5, 6.3, 3.1, 3.9, 2.7]
r2_vals     = [0.85, 0.84, 0.87, 0.89, 0.81, 0.78, 0.84]
 
kpi_data = {
    "Kavia":       {"sales": "$11.2M", "ticket": "$170", "star": "Vanilla concha", "daily": "$22.6k"},
    "Carreta":     {"sales": "$9.8M",  "ticket": "$155", "star": "Vanilla concha", "daily": "$19.4k"},
    "Zambrano":    {"sales": "$7.2M",  "ticket": "$140", "star": "Choco. concha",  "daily": "$14.8k"},
    "Credi-Club":  {"sales": "$8.4M",  "ticket": "$160", "star": "Vanilla concha", "daily": "$17.2k"},
    "Nativa":      {"sales": "$6.1M",  "ticket": "$132", "star": "Oat cookie",     "daily": "$12.5k"},
    "QIN":         {"sales": "$5.5M",  "ticket": "$128", "star": "Chilaquiles",    "daily": "$11.2k"},
    "Punto-Valle": {"sales": "$6.8M",  "ticket": "$145", "star": "Glazed donut",   "daily": "$13.9k"},
}
kpi = kpi_data[branch]
 
use_csv = (
    st.session_state.uploaded_df is not None
    and "operating_date" in st.session_state.uploaded_df.columns
    and "quantity" in st.session_state.uploaded_df.columns
)
 
 
# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "General Overview",
    "Sales History",
    "ML Forecast",
    "Model Metrics",
    "Data Entry",
])
 
 
# TAB 1 - GENERAL OVERVIEW
with tab1:
 
    st.markdown("#### Branch KPIs")
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, sub in [
        (k1, "Total Sales",     kpi["sales"],  "in the period"),
        (k2, "Avg. Ticket",     kpi["ticket"], "per transaction"),
        (k3, "Star Product",    kpi["star"],   "best seller"),
        (k4, "Avg. Daily Rev.", kpi["daily"],  "period average"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="font-size:{'1.3rem' if label == 'Star Product' else '1.9rem'}">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    if use_csv:
        df_branch = st.session_state.uploaded_df.copy()
        if "sucursal" in df_branch.columns:
            df_branch = df_branch[df_branch["sucursal"].str.lower() == branch.lower()]
        daily_agg = (
            df_branch.groupby("operating_date")["quantity"].sum()
            .reset_index().sort_values("operating_date")
        )
        dates_plot = daily_agg["operating_date"].values
        sales_plot = daily_agg["quantity"].values / 1000
        ma7_plot   = pd.Series(sales_plot).rolling(7, min_periods=1).mean().values
    else:
        dates_plot = dates_main
        sales_plot = daily_sales
        ma7_plot   = moving_avg7
 
    st.markdown('<div class="section-title">Daily Sales Evolution - units</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Total daily branch sales with 7-day moving average</div>', unsafe_allow_html=True)
 
    fig1, ax1 = plt.subplots(figsize=(14, 3.5))
    fig_defaults(ax1, fig1)
    ax1.bar(dates_plot, sales_plot, color=C_GOLD, width=0.8, label="Daily sales", alpha=0.85)
    ax1.plot(dates_plot, ma7_plot, color=C_LINE, lw=1.8, ls="--", label="7-day moving avg")
    if use_csv:
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    else:
        ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    ax1.tick_params(axis="x", rotation=30)
    ax1.set_ylabel("Units (k)" if not use_csv else "Units", fontsize=8, color=C_DARK)
    ax1.legend(fontsize=8, frameon=False, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig1)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2)
 
    with col_g1:
        st.markdown('<div class="section-title">Avg. Sales by Day of Week</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Average units sold per day of the week</div>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(6, 3.5))
        fig_defaults(ax2, fig2)
        bar_colors = [
            C_DARK if v == max(sales_by_day) else C_BROWN if v >= np.percentile(sales_by_day, 60) else C_GOLD
            for v in sales_by_day
        ]
        bars2 = ax2.bar(days_labels, sales_by_day, color=bar_colors, zorder=2)
        ax2.bar_label(bars2, labels=[f"{v/1000:.1f}k" for v in sales_by_day], padding=3, fontsize=7, color=C_DARK)
        ax2.set_ylim(0, max(sales_by_day) * 1.18)
        ax2.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax2.grid(axis="y", alpha=0.3, color="#DDD", zorder=0)
        plt.tight_layout()
        st.pyplot(fig2)
 
    with col_g2:
        st.markdown('<div class="section-title">Top 5 Products - Market Share</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Share of units sold by main product</div>', unsafe_allow_html=True)
        fig3, ax3 = plt.subplots(figsize=(5, 3.5))
        fig_defaults(ax3, fig3)
        wedges, _ = ax3.pie(
            share_vals, colors=donut_colors, startangle=90,
            wedgeprops={"width": 0.5, "edgecolor": "white", "linewidth": 2},
        )
        ax3.legend(
            wedges,
            [f"{p}  {v}%" for p, v in zip(top_products, share_vals)],
            loc="upper center", bbox_to_anchor=(0.5, -0.04),
            ncol=2, fontsize=7.5, frameon=False,
        )
        plt.tight_layout()
        st.pyplot(fig3)
 
 
# TAB 2 - SALES HISTORY
with tab2:
 
    st.markdown(f'<div class="section-title">Sales History - {product}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Daily units sold with +/-1 standard deviation band</div>', unsafe_allow_html=True)
 
    if use_csv and "item" in st.session_state.uploaded_df.columns:
        df_prod = st.session_state.uploaded_df.copy()
        df_prod = df_prod[df_prod["item"].str.lower().str.contains(product.split()[0].lower(), na=False)]
        if "sucursal" in df_prod.columns:
            df_prod = df_prod[df_prod["sucursal"].str.lower() == branch.lower()]
        agg_prod = df_prod.groupby("operating_date")["quantity"].sum().reset_index().sort_values("operating_date")
        if len(agg_prod) > 5:
            hist_x    = agg_prod["operating_date"].values
            hist_y    = agg_prod["quantity"].values.astype(float)
            std_band_ = float(np.std(hist_y))
        else:
            hist_x, hist_y, std_band_ = dates_hist, hist_sales, 25.0
    else:
        hist_x, hist_y, std_band_ = dates_hist, hist_sales, 25.0
 
    fig4, ax4 = plt.subplots(figsize=(14, 3.5))
    fig_defaults(ax4, fig4)
    ax4.fill_between(hist_x, hist_y - std_band_, hist_y + std_band_, color=C_GOLD, alpha=0.25, label="+/-1 std dev")
    ax4.plot(hist_x, hist_y, color=C_BROWN, lw=1.8, label=product)
    if use_csv:
        ax4.xaxis.set_major_locator(mdates.MonthLocator())
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    else:
        ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax4.xaxis.set_major_formatter(mdates.DateFormatter("%-d %b"))
    ax4.tick_params(axis="x", rotation=30)
    ax4.set_ylabel("Units", fontsize=8, color=C_DARK)
    ax4.legend(fontsize=8, frameon=False)
    plt.tight_layout()
    st.pyplot(fig4)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
 
    with col_h1:
        st.markdown('<div class="section-title">Temperature vs. Sales</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Sales vs average ambient temperature (C)</div>', unsafe_allow_html=True)
        temps_sc = np.random.uniform(12, 32, len(hist_y))
        fig5, ax5 = plt.subplots(figsize=(6, 3.5))
        fig_defaults(ax5, fig5)
        ax5.scatter(temps_sc, hist_y, color=C_GOLD, alpha=0.7, s=38, edgecolors=C_BROWN, lw=0.5)
        z = np.polyfit(temps_sc, hist_y, 1)
        xr = np.linspace(temps_sc.min(), temps_sc.max(), 100)
        ax5.plot(xr, np.poly1d(z)(xr), color=C_LINE, lw=1.5, ls="--", label="Trend")
        ax5.set_xlabel("Temperature (C)", fontsize=8, color=C_DARK)
        ax5.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax5.legend(fontsize=8, frameon=False)
        plt.tight_layout()
        st.pyplot(fig5)
 
    with col_h2:
        st.markdown('<div class="section-title">Sales by Week of Year</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Weekly seasonality of the product</div>', unsafe_allow_html=True)
        fig6, ax6 = plt.subplots(figsize=(6, 3.5))
        fig_defaults(ax6, fig6)
        wk_colors = [
            C_DARK if v > np.percentile(weekly_v, 80) else C_BROWN if v > np.percentile(weekly_v, 50) else C_GOLD
            for v in weekly_v
        ]
        ax6.bar(weeks, weekly_v, color=wk_colors, width=0.8)
        ax6.set_xticks(weeks[::4])
        ax6.set_xticklabels(weeks[::4], fontsize=7.5, color=C_DARK)
        ax6.set_ylabel("Units", fontsize=8, color=C_DARK)
        patches = [
            mpatches.Patch(color=C_DARK,  label="High demand"),
            mpatches.Patch(color=C_BROWN, label="Mid demand"),
            mpatches.Patch(color=C_GOLD,  label="Low demand"),
        ]
        ax6.legend(handles=patches, fontsize=7, frameon=False)
        plt.tight_layout()
        st.pyplot(fig6)
 
 
# TAB 3 - ML FORECAST
with tab3:
 
    st.markdown("**Production Forecast (XGBoost + Holt-Winters)**")
    st.caption(f"Branch: {branch} - Product: {product}")
 
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAE (CV 5-fold)",  "6.36 units")
    m2.metric("RMSE (CV 5-fold)", "8.03 units")
    m3.metric("Avg. R2",          "0.87")
    m4.metric("MAE Error %",      "46.7%")
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    new_w = st.session_state.new_weekly
    if new_w:
        st.success(f"Using manually entered weekly data ({len(new_w)} products) to adjust forecast.")
        scale = list(new_w.values())[0] / 280
        plot_fc_vals = [round(v * scale) for v in forecast_vals]
    else:
        plot_fc_vals = forecast_vals
 
    st.markdown('<div class="section-title">Daily Forecast - next 7 days (XGBoost)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Predicted units for {product} at {branch}</div>', unsafe_allow_html=True)
 
    fig7, ax7 = plt.subplots(figsize=(11, 3.8))
    fig_defaults(ax7, fig7)
    bar7 = ax7.bar(forecast_days, plot_fc_vals, color=fc_colors, zorder=2)
    ax7.bar_label(bar7, labels=[str(v) for v in plot_fc_vals], padding=4, fontsize=8.5, color=C_DARK, fontweight="bold")
    ax7.set_ylim(min(plot_fc_vals) * 0.88, max(plot_fc_vals) * 1.12)
    ax7.set_ylabel("Forecasted units", fontsize=8, color=C_DARK)
    ax7.grid(axis="y", alpha=0.25, color="#DDD", zorder=0)
    legend_patches = [
        mpatches.Patch(color=C_DARK,  label="Peak day"),
        mpatches.Patch(color=C_BROWN, label="High day"),
        mpatches.Patch(color=C_GOLD,  label="Normal day"),
    ]
    ax7.legend(handles=legend_patches, fontsize=7.5, frameon=False, loc="upper left")
    plt.tight_layout()
    st.pyplot(fig7)
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Weekly Forecast - next 4 weeks (Holt-Winters / ETS)</div>', unsafe_allow_html=True)
 
    df_hw = pd.DataFrame(week_plus, index=hw_products)
    df_hw.index.name = "Product"
    st.dataframe(
        df_hw.style
            .background_gradient(cmap="YlOrBr", axis=None)
            .format("{:.0f}"),
        use_container_width=True,
    )
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning(
        "Model limitation: Relative RMSE is 58.9% of the daily average. "
        "For peak days, holidays or special events the error may be higher. "
        "Adjust the forecast with manager judgment for events not in the historical data."
    )
    st.info(
        "Best modeled product: Vanilla concha (MAE error ~45.8%). "
        "Highest error: Chilaquiles Panem (~47.5%) - higher inherent variability."
    )
 
 
# TAB 4 - MODEL METRICS
with tab4:
 
    st.markdown('<div class="section-title">Training Metrics by Branch - XGBoost (CV 5-fold)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Time-series cross-validation. Each fold trains on past data and predicts future data.</div>', unsafe_allow_html=True)
 
    fig8, ax8 = plt.subplots(figsize=(12, 3.8))
    fig_defaults(ax8, fig8)
    x = np.arange(len(branches_ml))
    bars8 = ax8.bar(x - 0.2, mae_vals, width=0.35, color=C_GOLD, label="MAE (units)", zorder=2)
    ax8.bar_label(bars8, fmt="%.1f", padding=3, fontsize=7.5, color=C_DARK)
    ax8r = ax8.twinx()
    ax8r.plot(x, r2_vals, color=C_BROWN, marker="o", ms=7, lw=2, label="R2")
    ax8r.set_ylim(0.7, 1.0)
    ax8r.set_ylabel("R2", fontsize=8, color=C_BROWN)
    ax8r.tick_params(colors=C_BROWN, labelsize=8)
    ax8r.spines[["top", "right"]].set_color(C_SAND)
    ax8.set_xticks(x)
    ax8.set_xticklabels(branches_ml, fontsize=9, color=C_DARK)
    ax8.set_ylabel("MAE (units)", fontsize=8, color=C_DARK)
    ax8.grid(axis="y", alpha=0.25, color="#DDD", zorder=0)
    bars_leg = [mpatches.Patch(color=C_GOLD, label="MAE (units)")]
    lines8, labels8 = ax8r.get_legend_handles_labels()
    ax8.legend(handles=bars_leg + lines8, labels=["MAE (units)", "R2"], fontsize=8, frameon=False)
    plt.tight_layout()
    st.pyplot(fig8)
 
    st.markdown("<br>", unsafe_allow_html=True)
    col_m1, col_m2 = st.columns(2)
 
    with col_m1:
        st.markdown('<div class="section-title">Prediction vs Actual - test period</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-sub">Comparison for {branch} branch</div>', unsafe_allow_html=True)
        test_days_ = np.arange(1, 30)
        actual_    = np.random.normal(280, 25, 29).clip(210, 335)
        predicted_ = actual_ + np.random.normal(0, 18, 29)
        fig9, ax9 = plt.subplots(figsize=(7, 3.5))
        fig_defaults(ax9, fig9)
        ax9.plot(test_days_, actual_,    color=C_DARK, lw=2,   label="Actual")
        ax9.plot(test_days_, predicted_, color=C_GOLD, lw=1.8, ls="--", label="Predicted")
        ax9.fill_between(test_days_, actual_, predicted_, alpha=0.12, color=C_BROWN)
        ax9.set_xlabel("Day (test set)", fontsize=8, color=C_DARK)
        ax9.set_ylabel("Units", fontsize=8, color=C_DARK)
        ax9.legend(fontsize=8, frameon=False)
        plt.tight_layout()
        st.pyplot(fig9)
 
    with col_m2:
        st.markdown('<div class="section-title">Feature Importance</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Most influential variables in the XGBoost model</div>', unsafe_allow_html=True)
        features_    = ["lag_7", "avg_7d", "lag_14", "day_of_week", "week_of_year", "temperature", "is_holiday"]
        importances_ = [0.38, 0.31, 0.18, 0.08, 0.05, 0.04, 0.03]
        feat_colors  = [C_DARK, C_DARK, C_BROWN, C_BROWN, C_GOLD, C_GOLD, C_SAND]
        fig10, ax10 = plt.subplots(figsize=(6, 3.5))
        fig_defaults(ax10, fig10)
        bars10 = ax10.barh(features_[::-1], importances_[::-1], color=feat_colors[::-1], zorder=2)
        ax10.bar_label(bars10, fmt="%.2f", padding=3, fontsize=7.5, color=C_DARK)
        ax10.set_xlabel("Importance score", fontsize=8, color=C_DARK)
        ax10.grid(axis="x", alpha=0.25, color="#DDD", zorder=0)
        plt.tight_layout()
        st.pyplot(fig10)
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Full metrics summary</div>', unsafe_allow_html=True)
    df_metrics = pd.DataFrame({
        "Branch": branches_ml,
        "MAE":    mae_vals,
        "RMSE":   [3.5, 5.1, 4.4, 8.0, 5.8, 6.7, 4.9],
        "R2":     r2_vals,
        "MAE %":  ["38.2%", "44.1%", "41.0%", "46.7%", "45.3%", "48.5%", "42.8%"],
    })
    st.dataframe(
        df_metrics.style
            .background_gradient(subset=["MAE", "RMSE"], cmap="YlOrBr")
            .background_gradient(subset=["R2"], cmap="Greens")
            .format({"MAE": "{:.1f}", "RMSE": "{:.1f}", "R2": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
 
 
# TAB 5 - DATA ENTRY
with tab5:
 
    st.markdown("### Data Entry & Database Update")
    st.caption("Enter new sales records manually or upload a new CSV to update the dashboard.")
 
    # Section A: Manual weekly sales
    st.markdown(f"""
    <div class="entry-box">
      <div class="entry-title">Enter Weekly Sales - {branch}</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("Enter the **actual units sold** for each product this week. These values will adjust the ML forecast.")
 
    entry_products = [
        "Vanilla concha", "Chocolate concha", "Chilaquiles Panem",
        "Oat cookie", "Glazed donut", "Brioche w/ nuts", "Pan de muerto",
    ]
 
    week_start = st.date_input(
        "Week start date",
        value=datetime.date(2026, 5, 13),
        help="First day (Monday) of the week you are entering data for",
    )
 
    with st.form("weekly_sales_form"):
        st.markdown(f"**Branch:** {branch}  -  **Week of:** {week_start}")
        st.markdown("---")
        col_a, col_b = st.columns(2)
        entry_vals = {}
        for i, prod in enumerate(entry_products):
            col = col_a if i % 2 == 0 else col_b
            default_v = st.session_state.new_weekly.get(prod, 0)
            entry_vals[prod] = col.number_input(
                prod,
                min_value=0,
                max_value=5000,
                value=int(default_v),
                step=1,
                key=f"entry_{prod}",
            )
 
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Save weekly sales",
            use_container_width=True,
            type="primary",
        )
        if submitted:
            st.session_state.new_weekly = {k: v for k, v in entry_vals.items() if v > 0}
            st.success(f"Weekly sales saved for {branch} - week of {week_start}. Forecast tab updated.")
 
    if st.session_state.new_weekly:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Last saved weekly entry:**")
        df_saved = pd.DataFrame(
            list(st.session_state.new_weekly.items()),
            columns=["Product", "Units sold"],
        )
        df_saved["Branch"]  = branch
        df_saved["Week of"] = str(week_start)
        st.dataframe(df_saved[["Branch", "Week of", "Product", "Units sold"]], use_container_width=True, hide_index=True)
 
        csv_out = df_saved.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV",
            data=csv_out,
            file_name=f"panem_{branch}_{week_start}_sales.csv",
            mime="text/csv",
        )
 
        if st.button("Clear saved entries"):
            st.session_state.new_weekly = {}
            st.rerun()
 
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
 
    # Section B: Upload new full database
    st.markdown("""
    <div class="entry-box">
      <div class="entry-title">Upload New Database</div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown("""
    Upload a new full CSV export from the POS system. The dashboard will automatically update all charts.
 
    **Expected columns:**
    | Column | Description | Example |
    |--------|-------------|---------|
    | `operating_date` | Sale date | `2026-05-13` |
    | `sucursal` | Branch name | `Kavia` |
    | `item` | Product name | `Vanilla concha` |
    | `quantity` | Units sold | `12` |
    | `unit_price` | Price per unit | `45.00` |
    | `total_ticket` | Transaction total | `540.00` |
    """)
 
    uploaded2 = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="tab5_upload",
        help="The file will be processed and all charts will update automatically.",
    )
 
    if uploaded2:
        try:
            df_new = pd.read_csv(uploaded2)
            df_new.columns = [c.strip().lower() for c in df_new.columns]
            rename_map2 = {
                "branch": "sucursal", "sucursal": "sucursal",
                "product": "item", "item": "item", "producto": "item",
                "date": "operating_date", "fecha": "operating_date", "operating_date": "operating_date",
                "qty": "quantity", "cantidad": "quantity", "quantity": "quantity", "units": "quantity",
            }
            df_new = df_new.rename(columns={c: rename_map2[c] for c in df_new.columns if c in rename_map2})
            if "operating_date" in df_new.columns:
                df_new["operating_date"] = pd.to_datetime(df_new["operating_date"], errors="coerce")
 
            st.success(f"File validated - {len(df_new):,} rows, {df_new.shape[1]} columns")
 
            with st.expander("Preview data (first 20 rows)"):
                st.dataframe(df_new.head(20), use_container_width=True)
 
            with st.expander("Column summary"):
                st.dataframe(df_new.describe(include="all").T, use_container_width=True)
 
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("Apply to dashboard", use_container_width=True, type="primary"):
                st.session_state.uploaded_df = df_new
                st.success("Dashboard updated with new data. Switch to other tabs to see the changes.")
                st.rerun()
            if col_btn2.button("Discard", use_container_width=True):
                st.info("File discarded.")
 
        except Exception as e:
            st.error(f"Error processing file: {e}")
 
    # Section C: Add single transaction
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div class="entry-box">
      <div class="entry-title">Add Single Transaction</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Quickly register an individual sale not yet in the database.")
 
    with st.form("single_tx_form"):
        c1, c2, c3 = st.columns(3)
        tx_date    = c1.date_input("Date", value=datetime.date.today())
        tx_branch  = c2.selectbox("Branch", BRANCHES, index=BRANCHES.index(branch))
        tx_product = c3.selectbox("Product", entry_products)
        c4, c5, c6 = st.columns(3)
        tx_qty   = c4.number_input("Quantity (units)", min_value=1, max_value=1000, value=10)
        tx_price = c5.number_input("Unit price ($)", min_value=0.0, value=45.0, step=0.5)
        c6.number_input("Ticket total ($)", min_value=0.0, value=float(tx_qty * 45), step=1.0)
 
        if st.form_submit_button("Add transaction", use_container_width=True):
            key = (tx_branch, tx_product, str(tx_date))
            prev = st.session_state.manual_sales.get(key, 0)
            st.session_state.manual_sales[key] = prev + tx_qty
            st.success(f"Added {tx_qty} units of {tx_product} for {tx_branch} on {tx_date}")
 
    if st.session_state.manual_sales:
        st.markdown("<br>**Manually added transactions (this session):**")
        rows = [
            {"Branch": k[0], "Product": k[1], "Date": k[2], "Units": v}
            for k, v in st.session_state.manual_sales.items()
        ]
        df_manual = pd.DataFrame(rows)
        st.dataframe(df_manual, use_container_width=True, hide_index=True)
        csv_manual = df_manual.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download manual entries",
            data=csv_manual,
            file_name=f"panem_manual_entries_{datetime.date.today()}.csv",
            mime="text/csv",
        )
        if st.button("Clear all manual entries"):
            st.session_state.manual_sales = {}
            st.rerun()