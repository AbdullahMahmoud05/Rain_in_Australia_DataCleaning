"""
Australian Rainfall Analytics Dashboard
=========================================
A professional Streamlit + Plotly dashboard built on engineered features
from the Australian Rainfall dataset (Bureau of Meteorology, via Kaggle).

Data source expected: weathercleaned.csv (same folder as this file)
Run with: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Australian Rainfall Analytics",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# THEME (single, fixed dark-navy palette)
# ----------------------------------------------------------------------------
T = {
    "app_bg": "radial-gradient(circle at 10% 0%, #0f1b34 0%, #0b1120 45%, #060a15 100%)",
    "sidebar_bg": "linear-gradient(180deg, #0d1730 0%, #0a1226 100%)",
    "panel": "#111c33",
    "panel2": "#16223d",
    "accent": "#38bdf8",
    "accent2": "#22d3ee",
    "warm": "#f59e0b",
    "text_main": "#e5edf7",
    "text_dim": "#93a4c3",
    "border": "rgba(148, 163, 184, 0.15)",
    "paper_bg": "#0b1120",
    "plot_bg": "#0f1b34",
    "plotly_template": "plotly_dark",
    "rain_color": "#38bdf8",
    "norain_color": "#475569",
    "grid_color": "rgba(148,163,184,0.12)",
    "zeroline_color": "rgba(148,163,184,0.2)",
    "tab_selected_text": "#04121f",
    "hero_bg": "linear-gradient(120deg, #0e1b36 0%, #14284d 60%, #0e1b36 100%)",
    "corr_scale": ["#0f1b34", "#1e3a5f", "#38bdf8", "#22d3ee"],
}

# ----------------------------------------------------------------------------
# GLOBAL STYLING
# ----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
:root {{
    --navy-bg: {T['paper_bg']};
    --navy-panel: {T['panel']};
    --navy-panel-2: {T['panel2']};
    --accent: {T['accent']};
    --accent-2: {T['accent2']};
    --accent-warm: {T['warm']};
    --text-main: {T['text_main']};
    --text-dim: {T['text_dim']};
    --border-soft: {T['border']};
}}

.stApp {{
    background: {T['app_bg']};
    color: var(--text-main);
}}

section[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']};
    border-right: 1px solid var(--border-soft);
}}

section[data-testid="stSidebar"] * {{ color: var(--text-main) !important; }}

h1, h2, h3, h4 {{ color: var(--text-main) !important; font-weight: 700; letter-spacing: 0.3px; }}

p, span, label, .stMarkdown {{ color: var(--text-dim); }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
.stTabs [data-baseweb="tab"] {{
    background: var(--navy-panel);
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    color: var(--text-dim);
    border: 1px solid var(--border-soft);
    border-bottom: none;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
    color: {T['tab_selected_text']} !important;
    font-weight: 700;
}}

/* Metric cards */
div[data-testid="stMetric"] {{
    background: linear-gradient(160deg, var(--navy-panel) 0%, var(--navy-panel-2) 100%);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    padding: 18px 20px 14px 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}}
div[data-testid="stMetric"] label {{ color: var(--text-dim) !important; font-size: 0.85rem; }}
div[data-testid="stMetricValue"] {{ color: var(--accent-2) !important; font-size: 1.9rem; font-weight: 800; }}
div[data-testid="stMetricDelta"] {{ color: var(--accent-warm) !important; }}

/* Headers / dividers */
.section-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent-2);
    margin-top: 6px;
    margin-bottom: 10px;
    border-left: 4px solid var(--accent);
    padding-left: 10px;
}}

hr {{ border-color: var(--border-soft); }}

/* Multiselect / selectbox chips */
.stMultiSelect [data-baseweb="tag"] {{
    background-color: var(--accent) !important;
    color: #04121f !important;
}}

/* Dataframe */
div[data-testid="stDataFrame"] {{ border: 1px solid var(--border-soft); border-radius: 10px; }}

/* Hero header */
.hero {{
    padding: 22px 28px;
    border-radius: 18px;
    background: {T['hero_bg']};
    border: 1px solid var(--border-soft);
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}}
.hero h1 {{ margin-bottom: 4px; font-size: 2.1rem; }}
.hero p {{ margin: 0; color: var(--text-dim); }}

/* Callout box (used for the July outlook caveat) */
.callout {{
    padding: 18px 22px;
    border-radius: 14px;
    background: var(--navy-panel-2);
    border: 1px solid var(--border-soft);
    border-left: 5px solid var(--accent-warm);
    margin: 10px 0 16px 0;
}}
.callout b {{ color: var(--text-main); }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PLOTLY_TEMPLATE = T["plotly_template"]
COLOR_ACCENT = T["accent"]
COLOR_ACCENT2 = T["accent2"]
COLOR_WARM = T["warm"]
COLOR_RAIN = T["rain_color"]
COLOR_NORAIN = T["norain_color"]
PAPER_BG = T["paper_bg"]
PLOT_BG = T["plot_bg"]


def style_fig(fig, height=440, title=None):
    """Apply consistent dark-navy styling to a Plotly figure."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=T["text_main"], family="Segoe UI, Roboto, sans-serif"),
        title=dict(text=title, font=dict(size=17, color=T["text_main"])) if title else None,
        height=height,
        margin=dict(l=30, r=20, t=60 if title else 30, b=30),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=T["panel2"], font_size=13, font_color=T["text_main"]),
    )
    fig.update_xaxes(gridcolor=T["grid_color"], zerolinecolor=T["zeroline_color"])
    fig.update_yaxes(gridcolor=T["grid_color"], zerolinecolor=T["zeroline_color"])
    return fig


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading weather data...")
def load_data(path="weathercleaned.csv"):
    df = pd.read_csv(path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        if "Year" not in df.columns:
            df["Year"] = df["Date"].dt.year
        if "Month" not in df.columns:
            df["Month"] = df["Date"].dt.month
        if "Day" not in df.columns:
            df["Day"] = df["Date"].dt.day

    numeric_cols = [
        "Year", "Month", "Day", "AvgTemp", "TempRange", "MinTemp", "MaxTemp",
        "Temp9am", "Temp3pm", "AvgHum", "HumidityChange", "AvgPress",
        "PressureChange", "Humidity9am", "Humidity3pm", "Pressure9am",
        "Pressure3pm", "AvgWindSpeed", "WindChange", "AvgCloudy", "CloudChange",
        "Sunshine", "Evaporation", "Rainfall", "rt_num", "rto_num",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    season_map = {
        12: "Summer", 1: "Summer", 2: "Summer",
        3: "Autumn", 4: "Autumn", 5: "Autumn",
        6: "Winter", 7: "Winter", 8: "Winter",
        9: "Spring", 10: "Spring", 11: "Spring",
    }
    if "Month" in df.columns:
        df["Season"] = df["Month"].map(season_map)

    if "rt_num" not in df.columns and "RainToday" in df.columns:
        df["rt_num"] = df["RainToday"].map({"Yes": 1, "No": 0})
    if "rto_num" not in df.columns and "RainTomorrow" in df.columns:
        df["rto_num"] = df["RainTomorrow"].map({"Yes": 1, "No": 0})

    return df


try:
    df_raw = load_data()
except FileNotFoundError:
    st.error(
        "⚠️ Could not find **weathercleaned.csv**. Please place the file in the "
        "same directory as `app.py` and refresh the page."
    )
    st.stop()

DATA_MAX_DATE = df_raw["Date"].max()
DATA_MIN_DATE = df_raw["Date"].min()

# ----------------------------------------------------------------------------
# SIDEBAR — GLOBAL FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🌦️ Filter Controls")
st.sidebar.markdown("---")

# --- Location: dropdown, "All Locations" selected by default ---
all_locations = sorted(df_raw["Location"].dropna().unique().tolist())
location_options = ["All Locations"] + all_locations
location_pick = st.sidebar.multiselect(
    "📍 Location(s)",
    options=location_options,
    default=["All Locations"],
)
if not location_pick or (len(location_pick) == 1 and location_pick[0] == "All Locations"):
    selected_locations = all_locations
else:
    selected_locations = [loc for loc in location_pick if loc != "All Locations"]

# --- Year: dropdown, "All Years" selected by default ---
min_year = int(df_raw["Year"].min())
max_year = int(df_raw["Year"].max())
year_options = ["All Years"] + [str(y) for y in range(min_year, max_year + 1)]
year_pick = st.sidebar.selectbox("📅 Year", options=year_options, index=0)
if year_pick == "All Years":
    year_range = (min_year, max_year)
else:
    year_range = (int(year_pick), int(year_pick))

# --- Season: dropdown, "All Seasons" selected by default ---
season_options = ["All Seasons"] + sorted(df_raw["Season"].dropna().unique().tolist())
selected_season = st.sidebar.selectbox("🍂 Season", options=season_options, index=0)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Dataset span: **{DATA_MIN_DATE.date()} → {DATA_MAX_DATE.date()}**  \n"
    f"Total records loaded: **{len(df_raw):,}**  \n"
    f"Stations: **{len(all_locations)}**"
)

# Apply filters
mask = (
    df_raw["Location"].isin(selected_locations)
    & df_raw["Year"].between(year_range[0], year_range[1])
)
if selected_season != "All Seasons":
    mask &= df_raw["Season"] == selected_season

df = df_raw.loc[mask].copy()

if df.empty:
    st.warning("No records match the current filter selection. Please broaden your filters.")
    st.stop()

# ----------------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>🌧️ Australian Rainfall Analytics Dashboard</h1>
        <p>Executive insights &amp; atmospheric driver analysis across
        {len(selected_locations)} location(s), {year_range[0]}–{year_range[1]},
        season: <b>{selected_season}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Executive KPI & Trends", "🗺️ Location Deep-Dive",
     "🌡️ Atmospheric Drivers", "🔮 July 2017 Outlook"]
)

# ============================================================================
# TAB 1 — EXECUTIVE KPI OVERVIEW & SEASONAL TRENDS
# ============================================================================
with tab1:
    st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

    total_rainfall = df["Rainfall"].sum()
    avg_daily_rain = df["Rainfall"].mean()
    rain_prob = df["rto_num"].mean() * 100 if "rto_num" in df.columns else np.nan

    yearly_rain = df.groupby("Year")["Rainfall"].sum()
    top_rain_year = yearly_rain.idxmax() if not yearly_rain.empty else "N/A"
    top_rain_year_val = yearly_rain.max() if not yearly_rain.empty else 0

    city_rain = df.groupby("Location")["Rainfall"].sum()
    wettest_city = city_rain.idxmax() if not city_rain.empty else "N/A"
    wettest_city_val = city_rain.max() if not city_rain.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Rainfall (mm)", f"{total_rainfall:,.0f}")
    k2.metric("Avg Daily Rain (mm)", f"{avg_daily_rain:,.2f}")
    k3.metric("Rain Probability", f"{rain_prob:,.1f}%" if pd.notna(rain_prob) else "N/A")
    k4.metric("Top Rain Year", f"{top_rain_year}", delta=f"{top_rain_year_val:,.0f} mm")
    k5.metric("Wettest City", f"{wettest_city}", delta=f"{wettest_city_val:,.0f} mm")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        trend_granularity = st.radio(
            "Granularity", ["Yearly", "Monthly (avg across years)"],
            horizontal=True, key="trend_granularity"
        )

        if trend_granularity == "Yearly":
            trend_df = df.groupby("Year", as_index=False)["Rainfall"].sum()
            fig_trend = px.line(
                trend_df, x="Year", y="Rainfall", markers=True,
                labels={"Rainfall": "Total Rainfall (mm)"},
            )
            fig_trend.update_traces(line=dict(color=COLOR_ACCENT, width=3), marker=dict(size=7, color=COLOR_ACCENT2))
            trend_title = "Total Rainfall by Year"
        else:
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            trend_df = df.groupby("Month", as_index=False)["Rainfall"].mean()
            trend_df["MonthName"] = trend_df["Month"].apply(lambda m: month_names[int(m) - 1])
            trend_df = trend_df.sort_values("Month")
            fig_trend = px.line(
                trend_df, x="MonthName", y="Rainfall", markers=True,
                labels={"Rainfall": "Avg Rainfall (mm)", "MonthName": "Month"},
            )
            fig_trend.update_traces(line=dict(color=COLOR_ACCENT, width=3), marker=dict(size=7, color=COLOR_ACCENT2))
            trend_title = "Average Daily Rainfall by Month (Averaged Across All Years)"

        fig_trend = style_fig(fig_trend, height=420, title=trend_title)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        prob_df = df.groupby("Month", as_index=False)["rto_num"].mean()
        prob_df["Probability"] = prob_df["rto_num"] * 100
        prob_df["MonthName"] = prob_df["Month"].apply(lambda m: month_names[int(m) - 1])
        prob_df = prob_df.sort_values("Month")

        colors = [COLOR_WARM if m in (6, 7) else COLOR_ACCENT for m in prob_df["Month"]]

        fig_prob = go.Figure(
            go.Bar(
                x=prob_df["MonthName"], y=prob_df["Probability"], marker_color=colors,
                text=prob_df["Probability"].round(1).astype(str) + "%",
                textposition="outside",
                hovertemplate="Month: %{x}<br>Rain Prob: %{y:.1f}%<extra></extra>",
            )
        )
        fig_prob.update_yaxes(title="Rain Tomorrow Probability (%)")
        fig_prob = style_fig(fig_prob, height=420, title="Probability of Rain the Following Day, by Month")
        st.plotly_chart(fig_prob, use_container_width=True)

# ============================================================================
# TAB 2 — LOCATION & GEOGRAPHICAL DEEP-DIVE
# ============================================================================
with tab2:
    col_a, col_b = st.columns([1.3, 1])

    with col_a:
        top_n = st.slider("Number of cities to display", min_value=5, max_value=15, value=15, key="top_n_cities")
        rain_metric = st.selectbox(
            "Ranking Metric", ["Total Rainfall", "Average Daily Rainfall", "Rain Probability %"],
            key="rank_metric"
        )

        city_stats = df.groupby("Location").agg(
            TotalRainfall=("Rainfall", "sum"),
            AvgRainfall=("Rainfall", "mean"),
            RainProb=("rto_num", "mean"),
        ).reset_index()
        city_stats["RainProb"] = city_stats["RainProb"] * 100

        metric_map = {
            "Total Rainfall": "TotalRainfall",
            "Average Daily Rainfall": "AvgRainfall",
            "Rain Probability %": "RainProb",
        }
        sort_col = metric_map[rain_metric]
        city_top = city_stats.sort_values(sort_col, ascending=False).head(top_n)

        fig_city = px.bar(
            city_top.sort_values(sort_col),
            x=sort_col, y="Location", orientation="h",
            color=sort_col, color_continuous_scale=[T["panel"], COLOR_ACCENT, COLOR_ACCENT2],
            labels={sort_col: rain_metric, "Location": "City"},
        )
        fig_city.update_layout(coloraxis_showscale=False)
        fig_city = style_fig(fig_city, height=520, title=f"Top {top_n} Cities Ranked by {rain_metric}")
        st.plotly_chart(fig_city, use_container_width=True)

    with col_b:
        box_locations = st.multiselect(
            "Cities to compare (box plot)",
            options=sorted(df["Location"].unique().tolist()),
            default=sorted(df["Location"].unique().tolist())[:6],
            key="box_locations",
        )

        rainy_df = df[(df["rt_num"] == 1) & (df["Location"].isin(box_locations))]

        if rainy_df.empty:
            st.info("No rainy-day records for the selected cities/filters.")
        else:
            fig_box = px.box(
                rainy_df, x="Location", y="Rainfall", color="Location",
                points="outliers",
                labels={"Rainfall": "Rainfall (mm)"},
            )
            fig_box.update_layout(showlegend=False)
            fig_box.update_yaxes(type="log")
            fig_box = style_fig(fig_box, height=460, title="Rainfall on Rainy Days, by City (Log Scale)")
            st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">City-Level Summary Table</div>', unsafe_allow_html=True)
    st.dataframe(
        city_stats.sort_values("TotalRainfall", ascending=False)
        .rename(columns={
            "TotalRainfall": "Total Rainfall (mm)",
            "AvgRainfall": "Avg Daily Rainfall (mm)",
            "RainProb": "Rain Probability (%)",
        })
        .style.format({
            "Total Rainfall (mm)": "{:,.0f}",
            "Avg Daily Rainfall (mm)": "{:.2f}",
            "Rain Probability (%)": "{:.1f}",
        }),
        use_container_width=True,
        height=320,
    )

# ============================================================================
# TAB 3 — ATMOSPHERIC DRIVERS (ENGINEERED FEATURES IMPACT)
# ============================================================================
with tab3:
    col_x, col_y = st.columns([1.2, 1])

    with col_x:
        sample_size = st.slider(
            "Sample size (for rendering performance)",
            min_value=500, max_value=min(20000, len(df)),
            value=min(5000, len(df)), step=500, key="scatter_sample"
        )
        scatter_df = df.dropna(subset=["PressureChange", "HumidityChange", "RainTomorrow"])
        if len(scatter_df) > sample_size:
            scatter_df = scatter_df.sample(sample_size, random_state=42)

        fig_scatter = px.scatter(
            scatter_df, x="PressureChange", y="HumidityChange",
            color="RainTomorrow",
            color_discrete_map={"Yes": COLOR_RAIN, "No": COLOR_NORAIN},
            opacity=0.6,
            labels={"PressureChange": "Pressure Change (hPa)", "HumidityChange": "Humidity Change (%)"},
            hover_data=["Location", "Year", "Month"] if "Location" in scatter_df.columns else None,
        )
        fig_scatter.update_traces(marker=dict(size=6, line=dict(width=0)))
        fig_scatter.add_hline(y=0, line_dash="dot", line_color=T["zeroline_color"])
        fig_scatter.add_vline(x=0, line_dash="dot", line_color=T["zeroline_color"])
        fig_scatter = style_fig(fig_scatter, height=480, title="Pressure Change vs Humidity Change (3pm − 9am)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_y:
        drivers = ["AvgTemp", "AvgHum", "AvgPress", "AvgCloudy"]
        driver_labels = {
            "AvgTemp": "Avg Temperature (°C)",
            "AvgHum": "Avg Humidity (%)",
            "AvgPress": "Avg Pressure (hPa)",
            "AvgCloudy": "Avg Cloud Cover (oktas)",
        }
        available_drivers = [d for d in drivers if d in df.columns]

        driver_summary = df.dropna(subset=["RainTomorrow"]).groupby("RainTomorrow")[available_drivers].mean().reset_index()

        fig_driver = make_subplots(
            rows=2, cols=2,
            subplot_titles=[driver_labels.get(d, d) for d in available_drivers],
        )
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        legend_shown = set()
        for d, (r, c) in zip(available_drivers, positions):
            for label, color in [("No", COLOR_NORAIN), ("Yes", COLOR_RAIN)]:
                row = driver_summary.loc[driver_summary["RainTomorrow"] == label, d]
                if row.empty:
                    continue
                fig_driver.add_trace(
                    go.Bar(
                        x=[f"Rain Tomorrow: {label}"], y=[row.values[0]],
                        marker_color=color, name=f"Rain Tomorrow: {label}",
                        showlegend=label not in legend_shown,
                        text=[f"{row.values[0]:.1f}"], textposition="outside",
                        hovertemplate=f"{driver_labels.get(d, d)}<br>Rain Tomorrow: {label}: %{{y:.2f}}<extra></extra>",
                    ),
                    row=r, col=c,
                )
                legend_shown.add(label)

        fig_driver.update_layout(
            template=PLOTLY_TEMPLATE, paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font=dict(color=T["text_main"], family="Segoe UI, Roboto, sans-serif"),
            title=dict(text="Temp / Humidity / Pressure / Cloud: Rain vs No Rain",
                       font=dict(size=17, color=T["text_main"])),
            height=520, margin=dict(l=30, r=20, t=90, b=30), showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.08, x=0.5, xanchor="center"),
            hoverlabel=dict(bgcolor=T["panel2"], font_size=13, font_color=T["text_main"]),
        )
        fig_driver.update_xaxes(gridcolor=T["grid_color"], zerolinecolor=T["zeroline_color"])
        fig_driver.update_yaxes(gridcolor=T["grid_color"], zerolinecolor=T["zeroline_color"])
        for ann in fig_driver.layout.annotations:
            ann.font.color = T["text_main"]
            ann.font.size = 12

        st.plotly_chart(fig_driver, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Feature Correlation Snapshot</div>', unsafe_allow_html=True)
    corr_features = [c for c in [
        "AvgTemp", "TempRange", "AvgHum", "HumidityChange", "AvgPress",
        "PressureChange", "AvgWindSpeed", "AvgCloudy", "Sunshine", "Rainfall"
    ] if c in df.columns]
    corr_matrix = df[corr_features].corr()
    fig_corr = px.imshow(
        corr_matrix, text_auto=".2f", aspect="auto",
        color_continuous_scale=T["corr_scale"],
        labels=dict(color="Correlation"),
    )
    fig_corr = style_fig(fig_corr, height=520, title="Correlation Between Engineered Weather Features")
    st.plotly_chart(fig_corr, use_container_width=True)

# ============================================================================
# TAB 4 — JULY 2017 RAIN OUTLOOK (HISTORICAL BASE-RATE ESTIMATE)
# ============================================================================
with tab4:
    st.markdown('<div class="section-title">Rain Outlook — July 2017</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="callout">
        <b>Note on method:</b> the dataset only runs from <b>{DATA_MIN_DATE.date()}</b> to
        <b>{DATA_MAX_DATE.date()}</b> — it stops in June 2017, so <b>no actual observations exist
        for July 2017</b>. No predictive model is used here. Instead, this tab reports a
        <b>historical base-rate estimate</b>: the share of July days that recorded rain across all
        the Julys that <i>are</i> in the data (2008–2016), used as the best available estimate for
        "how likely is rain in July 2017."
        </div>
        """,
        unsafe_allow_html=True,
    )

    july_all = df_raw[df_raw["Month"] == 7].copy()
    july_years = sorted(july_all["Year"].dropna().unique().tolist())

    if july_all.empty:
        st.warning("No historical July records found in the dataset.")
    else:
        overall_rain_rate = july_all["rt_num"].mean() * 100
        overall_days = len(july_all)

        c1, c2, c3 = st.columns(3)
        c1.metric("Historical July Rain Probability", f"{overall_rain_rate:.1f}%")
        c2.metric("Julys in Dataset", f"{july_years[0]}–{july_years[-1]}" if july_years else "N/A")
        c3.metric("July Station-Days Observed", f"{overall_days:,}")

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1.3, 1])

        with col_l:
            july_city = july_all.groupby("Location").agg(
                RainProb=("rt_num", "mean"),
                AvgRainfall=("Rainfall", "mean"),
                DaysObserved=("rt_num", "count"),
            ).reset_index()
            july_city["RainProb"] = july_city["RainProb"] * 100
            july_city = july_city.sort_values("RainProb", ascending=False)

            fig_july = px.bar(
                july_city, x="RainProb", y="Location", orientation="h",
                color="RainProb", color_continuous_scale=[T["panel"], COLOR_ACCENT, COLOR_WARM],
                labels={"RainProb": "Est. Rain Probability, July 2017 (%)", "Location": "City"},
            )
            fig_july.update_layout(coloraxis_showscale=False, yaxis=dict(categoryorder="total ascending"))
            fig_july = style_fig(fig_july, height=650, title="Est. July 2017 Rain Probability by City (Historical Base Rate)")
            st.plotly_chart(fig_july, use_container_width=True)

        with col_r:
            july_by_year = july_all.groupby("Year", as_index=False)["rt_num"].mean()
            july_by_year["Probability"] = july_by_year["rt_num"] * 100

            fig_yearly_july = px.line(
                july_by_year, x="Year", y="Probability", markers=True,
                labels={"Probability": "July Rain Probability (%)"},
            )
            fig_yearly_july.update_traces(line=dict(color=COLOR_ACCENT, width=3), marker=dict(size=8, color=COLOR_WARM))
            fig_yearly_july.add_hline(
                y=overall_rain_rate, line_dash="dash", line_color=COLOR_ACCENT2,
                annotation_text=f"Avg: {overall_rain_rate:.1f}%", annotation_position="top left",
            )
            fig_yearly_july = style_fig(fig_yearly_july, height=650, title="July Rain-Day Rate, Year by Year (2008–2016)")
            st.plotly_chart(fig_yearly_july, use_container_width=True)

        st.markdown("---")
        st.markdown('<div class="section-title">Detailed City Table — Historical July Statistics</div>', unsafe_allow_html=True)
        st.dataframe(
            july_city.rename(columns={
                "RainProb": "Est. Rain Probability, July 2017 (%)",
                "AvgRainfall": "Avg Daily Rainfall in July (mm)",
                "DaysObserved": "July Station-Days Observed (2008–2016)",
            }).style.format({
                "Est. Rain Probability, July 2017 (%)": "{:.1f}",
                "Avg Daily Rainfall in July (mm)": "{:.2f}",
            }),
            use_container_width=True,
            height=340,
        )

# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Built with Streamlit & Plotly · Data: Australian Rainfall (Bureau of Meteorology, via Kaggle)"
)
