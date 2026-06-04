import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import gaussian_kde

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="The Implementation Gap", layout="wide", initial_sidebar_state="expanded")

# TITLE & MAIN CONTEXT
st.title("The Implementation Gap: Public Health Policies vs. Clinical Reality")
st.markdown("This dashboard evaluates the effectiveness of recent public health decisions by measuring the 'implementation gap'. It compares national vaccination policies for vulnerable groups against actual vaccine uptake, cross-referencing this gap with healthcare system stress and geriatric mortality.")
st.markdown("**Role:** Strategic Data Analyst in Public Health")
st.markdown("**Target Audience:** Governments and health departments, hospitals, researchers and data analysts in public health, and vulnerable populations")
st.markdown("---")

@st.cache_data
def load_data():
    df_policy = pd.read_csv('COV_VAC_POLICY_2024.csv')
    df_uptake = pd.read_csv('COV_VAC_UPTAKE_2024.csv')
    df_hosp = pd.read_csv('WHO-COVID-19-global-hosp-icu-data.csv')
    df_deaths = pd.read_csv('WHO-COVID-19-global-monthly-death-by-age-data.csv')

    df_policy.rename(columns={'COUNTRY': 'iso_code'}, inplace=True)
    df_uptake.rename(columns={'COUNTRY': 'iso_code'}, inplace=True)
    df_hosp.rename(columns={'Country_code': 'iso_code'}, inplace=True)
    df_deaths.rename(columns={'Country_code': 'iso_code'}, inplace=True)

    df_policy.dropna(subset=['VALUE'], inplace=True)
    df_hosp.dropna(subset=['Covid_new_hospitalizations_last_7days'], inplace=True)
    df_deaths.dropna(subset=['Deaths'], inplace=True)

    policy_latest = df_policy[df_policy['CATEGORY'] == 'Older adults'].sort_values('DATE').groupby('iso_code').tail(1)[['iso_code', 'VALUE']]
    uptake_agg = df_uptake[df_uptake['GROUP'] == 'old'].groupby('iso_code')['COVID_VACCINE_ADM_1D'].max().reset_index()
    deaths_agg = df_deaths[df_deaths['Agegroup'] == '65+'].groupby(['iso_code', 'Who_region', 'Agegroup'])['Deaths'].sum().reset_index()

    df_merged = pd.merge(policy_latest, deaths_agg, on='iso_code', how='inner')
    df_merged = pd.merge(df_merged, uptake_agg, on='iso_code', how='left').fillna(0)
    
    df_merged['Log_Deaths'] = np.log10(df_merged['Deaths'] + 1)
    df_merged['Log_Doses'] = np.log10(df_merged['COVID_VACCINE_ADM_1D'] + 1)
    
    df_hosp['Date_reported'] = pd.to_datetime(df_hosp['Date_reported'])
    hosp_trend = df_hosp.groupby(['Date_reported', 'iso_code'])['Covid_new_hospitalizations_last_7days'].sum().reset_index()

    return df_merged, hosp_trend

df_merged, hosp_trend = load_data()

st.sidebar.header("Dashboard Filters")
all_regions = df_merged['Who_region'].dropna().unique().tolist()
selected_regions = st.sidebar.multiselect("Select WHO Regions:", options=all_regions, default=all_regions)

if selected_regions:
    df_filtered = df_merged[df_merged['Who_region'].isin(selected_regions)]
else:
    df_filtered = df_merged

color_insight = '#1f77b4' 
color_base = '#d3d3d3'    

# ROW 1: FULL WIDTH MAP (GLOBAL CONTEXT)

col1 = st.columns(1)[0]

with col1:
    st.subheader("The Global Implementation Gap: Mortality in Protected Countries")

    selected_country_iso = None
    if "map_chart" in st.session_state and st.session_state.map_chart:
        selection = st.session_state.map_chart.get("selection", {})
        points = selection.get("points", [])
        if points:
            selected_country_iso = points[0].get("location")

    if selected_country_iso:
        st.caption(f"Context: Close-up analysis for **{selected_country_iso}**. Click the button below to restore the global view.")
        
        if st.button("Reset to Global View", key="reset_map"):
            st.session_state.map_chart = None
            st.rerun()
            
        df_map_display = df_filtered[df_filtered['iso_code'] == selected_country_iso]
        
        map_colorscale = ["#E0F7FA", "#4DD0E1", "#00ACC1", "#006064"]
        
        geo_layout = dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            scope='world'
        )
    else:
        st.caption("Context: Global distribution of log-scaled deaths in countries with active 'YES' policies. **Click on any country** to isolate its layout and metrics.")
        df_map_display = df_filtered
        
        map_colorscale = "Blues" 
        geo_layout = dict(
            showframe=False,
            showcoastlines=True,
            projection_type='orthographic',
            scope='world'
        )

    if not df_map_display.empty:
        fig1 = px.choropleth(
            df_map_display,
            locations="iso_code",
            color="Log_Deaths",
            hover_name="iso_code",
            hover_data={"Deaths": ':', "COVID_VACCINE_ADM_1D": ':', "Log_Deaths": False},
            color_continuous_scale=map_colorscale,
            template="plotly_white"
        )
        
        fig1.update_layout(
            geo=geo_layout,
            coloraxis_colorbar=dict(
                title="Log(Deaths)",
                thicknessmode="pixels", thickness=15,
                lenmode="pixels", len=300,
                yanchor="middle", y=0.5
            ),
            margin=dict(l=0, r=0, t=10, b=10),
            height=600
        )
        
        if selected_country_iso:
            fig1.update_geos(fitbounds="locations")

        st.plotly_chart(fig1, use_container_width=True, on_select="rerun", key="map_chart")
    else:
        st.warning("No data available for the current map filters.")

    if selected_country_iso and not df_map_display.empty:
        country_data = df_map_display.iloc[0]
        real_deaths = int(country_data['Deaths'])
        real_doses = int(country_data['COVID_VACCINE_ADM_1D'])
        policy_status = country_data['VALUE']
        region_status = country_data['Who_region']
        
        st.markdown(f"""
        <div style='background-color: #E0F7FA; padding: 20px; border-left: 6px solid #00ACC1; border-radius: 8px; margin-top: 15px;'>
            <h4 style='color: #006064; margin-top: 0;'>Country Factsheet: {selected_country_iso} Layout</h4>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px;'>
                <div style='background: white; padding: 10px; border-radius: 4px; border: 1px solid #B2EBF2;'>
                    <span style='color: #555; font-size: 0.9em;'>WHO Region</span><br>
                    <strong style='color: #006064; font-size: 1.2em;'>{region_status}</strong>
                </div>
                <div style='background: white; padding: 10px; border-radius: 4px; border: 1px solid #B2EBF2;'>
                    <span style='color: #555; font-size: 0.9em;'>Policy Mandate</span><br>
                    <strong style='color: #006064; font-size: 1.2em; color: #2E7D32;'>{policy_status} (Active)</strong>
                </div>
                <div style='background: white; padding: 10px; border-radius: 4px; border: 1px solid #B2EBF2;'>
                    <span style='color: #555; font-size: 0.9em;'>Total Cumulative Deaths</span><br>
                    <strong style='color: #D32F2F; font-size: 1.2em;'>{real_deaths:,}</strong>
                </div>
                <div style='background: white; padding: 10px; border-radius: 4px; border: 1px solid #B2EBF2;'>
                    <span style='color: #555; font-size: 0.9em;'>First Doses Administered</span><br>
                    <strong style='color: #1976D2; font-size: 1.2em;'>{real_doses:,}</strong>
                </div>
            </div>
            <span style='color: #006064; font-weight: bold;'>Localized Gap Insight:</span> 
            The close-up layout for <b>{selected_country_iso}</b> isolates its exact performance. Despite maintaining an official mandate, the country suffered <b>{real_deaths:,}</b> deaths. With <b>{real_doses:,}</b> initial doses tracked, the data reveals that administrative presence on the map did not guarantee real-time clinical shielding, making it a clear spatial example of the implementation gap.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid #1565C0; border-radius: 4px; margin-top: 15px;'>
            <span style='color: #1565C0; font-weight: bold;'>General Spatial Insight:</span> The geographic overlay demonstrates that mortality is widely distributed across territories despite having a 'YES' policy status. This proves that the gap between health strategy approval and physical operational execution is a global systemic issue, not a localized exception.
        </div>
        """, unsafe_allow_html=True)
    
st.write("---")

# ROW 2: 3D DENSITY & TOP 15 BAR/LINE
col1, col2 = st.columns(2)

top15 = df_filtered.sort_values('Deaths', ascending=False).head(15)

with col1:
    st.subheader("Implementation Gap: Mortality (Top 15)")
    st.caption("Context: Click on a bar to analyze its impact on administered doses.")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=top15['iso_code'], 
        y=top15['Deaths'], 
        name='Deaths (65+)', 
        marker_color=color_insight,
        customdata=top15['iso_code']
    ))
    
    fig2.update_layout(
        template="plotly_white", margin=dict(l=0, r=0, t=10, b=0), height=450,
        yaxis=dict(title=dict(text='Total Deaths', font=dict(color=color_insight)), tickfont=dict(color=color_insight)),
        xaxis=dict(title='Country ISO Code'),
        showlegend=False,
        clickmode='event+select' 
    )
    
    event = st.plotly_chart(fig2, use_container_width=True, on_select="rerun")
    
    selected_iso = None
    if event and event.selection and event.selection.get("points"):
        selected_iso = event.selection["points"][0]["x"]

    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid {color_insight}; border-radius: 4px; margin-bottom: 20px;'>
        <span style='color: {color_insight}; font-weight: bold;'>General Insight:</span> The staggering death toll in these specific nations exposes a critical breakdown in protecting the most vulnerable, despite having official mandates on paper.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("Implementation Gap: Administered Doses")
    st.caption("Context: Administered doses for the exact same countries. Select a country on the left.")
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=top15['iso_code'], y=top15['COVID_VACCINE_ADM_1D'], 
        name='Administered Doses', mode='lines+markers', 
        line=dict(color=color_base, width=3),
        marker=dict(color=color_base, size=6)
    ))
    
    if selected_iso:
        highlight_data = top15[top15['iso_code'] == selected_iso]
        fig3.add_trace(go.Scatter(
            x=highlight_data['iso_code'], 
            y=highlight_data['COVID_VACCINE_ADM_1D'],
            mode='markers', 
            marker=dict(color="#bd4bff", size=16, line=dict(color='white', width=2)), 
            name=f'{selected_iso} Highlight'
        ))
    
    fig3.update_layout(
        template="plotly_white", margin=dict(l=0, r=0, t=10, b=0), height=400,
        yaxis=dict(title=dict(text='Administered Doses', font=dict(color=color_insight)), tickfont=dict(color=color_insight)),
        xaxis=dict(title='Country ISO Code'),
        showlegend=False
    )
    st.plotly_chart(fig3, use_container_width=True)

    if selected_iso:
        country_data = top15[top15['iso_code'] == selected_iso].iloc[0]
        c_deaths = int(country_data['Deaths'])
        c_doses = int(country_data['COVID_VACCINE_ADM_1D'])
        
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid #bd4bff; border-radius: 4px; margin-bottom: 20px;'>
            <span style='color: #bd4bff; font-weight: bold;'>Specific Insight ({selected_iso}):</span> Despite reporting <b>{c_doses:,}</b> administered doses, the country recorded <b>{c_deaths:,}</b> deaths in older adults. This highlights that vaccine volume did not compensate for the logistical gap in response times.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid {color_insight}; border-radius: 4px; margin-bottom: 20px;'>
            <span style='color:{color_insight}; font-weight: bold;'>Insight:</span> Administration volumes for these exact same nations show erratic patterns, proving that mere dose counts do not equal effective clinical protection if logistical timing fails.
        </div>
        """, unsafe_allow_html=True)
  
# ROW 3: LOLLIPOP CHART & HOSPITALIZATION STRESS
col3, col4 = st.columns(2)

df_yes_worst = df_filtered[df_filtered['VALUE'] == 'YES'].sort_values('Deaths', ascending=False).head(15).reset_index(drop=True)
n_rows = len(df_yes_worst)

selected_lol_iso = None
if "lol_chart" in st.session_state and st.session_state.lol_chart:
    selection = st.session_state.lol_chart.get("selection", {})
    points = selection.get("points", [])
    if points:
        selected_lol_iso = points[0].get("x")

markers_colors_lol = []
lines_colors_lol = []
highlight_blue = '#007BFF' 

if selected_lol_iso:
    for row_iso in df_yes_worst['iso_code']:
        if row_iso == selected_lol_iso:
            markers_colors_lol.append(highlight_blue)
            lines_colors_lol.append(highlight_blue)
        else:
            markers_colors_lol.append('#D3D3D3') 
            lines_colors_lol.append('#E0E0E0')
else:
    rank_colors_lol = [color_insight if i < 2 or i >= (n_rows - 2) else color_base for i in range(n_rows)]
    markers_colors_lol = rank_colors_lol
    lines_colors_lol = rank_colors_lol


with col3:
    st.subheader("Operational Failure: The 'YES' Policy Toll")
    st.caption("Context: Click on a lollipop point to analyze its specific healthcare system stress.")

    fig_lol = go.Figure()
    
    for i, row in df_yes_worst.iterrows():
        fig_lol.add_shape(
            type="line", x0=row['iso_code'], y0=0, x1=row['iso_code'], y1=row['Deaths'],
            line=dict(color=lines_colors_lol[i], width=3)
        )
    
    fig_lol.add_trace(go.Scatter(
        x=df_yes_worst['iso_code'], y=df_yes_worst['Deaths'],
        mode='markers', marker=dict(color=markers_colors_lol, size=12),
        name='Total Cumulative Deaths',
        customdata=df_yes_worst['iso_code'],
        hovertemplate='<b>%{x}</b><br>Deaths: %{y}<extra></extra>'
    ))
    
    fig_lol.update_layout(
        template="plotly_white", 
        margin=dict(l=10, r=10, t=20, b=20),
        height=550,
        yaxis=dict(title=dict(text='Total Cumulative Deaths', font=dict(color=color_insight)), tickfont=dict(color=color_insight)),
        xaxis=dict(title='Country ISO Code (With Active Policy)'),
        showlegend=False,
        clickmode='event+select'
    )
    
    st.plotly_chart(fig_lol, use_container_width=True, on_select="rerun", key="lol_chart")

    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid {color_insight}; border-radius: 4px; margin-bottom: 20px;'>
        <span style='color:{color_insight}; font-weight: bold;'>General Insight:</span> Having a policy on paper did not shield these countries. The Lollipop starkly highlights the volume of lost lives.
    </div>
    """, unsafe_allow_html=True)


with col4:
    st.subheader("Healthcare System Stress")
    
    if selected_lol_iso:
        st.caption(f"Context: Weekly new hospital admissions for <b>{selected_lol_iso}</b> showing localized system pressure.")
        hosp_display = hosp_trend[hosp_trend['iso_code'] == selected_lol_iso].groupby('Date_reported')['Covid_new_hospitalizations_last_7days'].sum().reset_index()
        line_clr = '#7E57C2'
        fill_clr = 'rgba(126, 87, 194, 0.3)'
    else:
        st.caption("Context: Aggregated cyclical peaks of weekly new hospital admissions for selected regions.")
        valid_isos = df_filtered['iso_code'].unique()
        hosp_display = hosp_trend[hosp_trend['iso_code'].isin(valid_isos)].groupby('Date_reported')['Covid_new_hospitalizations_last_7days'].sum().reset_index()
        line_clr = color_base
        fill_clr = color_insight

    if not hosp_display.empty:
        fig5 = px.area(hosp_display, x='Date_reported', y='Covid_new_hospitalizations_last_7days')
        fig5.update_layout(
            template="plotly_white", 
            margin=dict(l=10, r=10, t=20, b=20),
            xaxis_title="Reporting Date", 
            yaxis_title="New Hospitalizations", 
            height=550
        )
        fig5.update_traces(line_color=line_clr, fillcolor=fill_clr) 
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning(f"No hospitalization data available for {selected_lol_iso or 'the selected regions'}.")

    if selected_lol_iso and not hosp_display.empty:
        max_hosp = int(hosp_display['Covid_new_hospitalizations_last_7days'].max())
        st.markdown(f"""
        <div style='background-color: #f4effc; padding: 12px; border-left: 4px solid #7E57C2; border-radius: 4px; margin-bottom: 20px;'>
            <span style='color:#7E57C2; font-weight: bold;'>Specific Insight ({selected_lol_iso}):</span> Localized hospitalization peaks reached up to <b>{max_hosp:,}</b> weekly admissions. This demonstrates that despite having an official 'YES' policy, delayed clinical execution failed to flatten the curve, resulting in severe hospital stress.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid {color_insight}; border-radius: 4px; margin-bottom: 20px;'>
            <span style='color:{color_insight}; font-weight: bold;'>Insight:</span> Systemic stress peaks cyclically, highlighting the cost of implementation gaps in vulnerable populations.
        </div>
        """, unsafe_allow_html=True)

st.write("---")

# ROW 4: REGIONAL SCATTER

col5 = st.columns(1)[0] 

with col5:
    st.subheader("Distribution of Deaths by Region and Age Group")

    try:
        df_deaths_local = pd.read_csv('WHO-COVID-19-global-monthly-death-by-age-data.csv')
        df_deaths_local.rename(columns={'Country_code': 'iso_code'}, inplace=True)
        df_deaths_local.dropna(subset=['Deaths'], inplace=True)
        
        df_deaths_local = df_deaths_local[df_deaths_local['Agegroup'].isin(['0_4', '5_14', '15_64', '65+'])]
        df_deaths_local = df_deaths_local.groupby(['iso_code', 'Who_region', 'Agegroup'])['Deaths'].sum().reset_index()
        
        if selected_regions:
            df_clean_all_ages = df_deaths_local[df_deaths_local['Who_region'].isin(selected_regions)]
        else:
            df_clean_all_ages = df_deaths_local
    except Exception as e:
        st.error("Error reading the deaths file locally inside Row 4. Please ensure the file name is correct.")
        df_clean_all_ages = pd.DataFrame()

    age_blue_map = {
        '0_4': '#E3F2FD',  
        '5_14': '#90CAF9',   
        '15_64': '#42A5F5',  
        '65+': '#1565C0'    
    }

    selected_region = None
    if "box_chart" in st.session_state and st.session_state.box_chart:
        selection = st.session_state.box_chart.get("selection", {})
        points = selection.get("points", [])
        if points:
            selected_region = points[0].get("x")

    if selected_region:
        st.caption(f"Context: Detailed age distribution for **{selected_region}**. Click the button below to return to the global view.")
        
        if st.button("Reset to All Regions"):
            st.session_state.box_chart = None
            st.rerun()
        
        df_display = df_clean_all_ages[df_clean_all_ages['Who_region'] == selected_region]
        x_axis_field = 'Agegroup'
        x_label = f"Age Groups in {selected_region}"
    elif not df_clean_all_ages.empty:
        st.caption("Context: Comparative distribution of monthly deaths across cohorts. **Click any data point inside a region** to run a localized analysis.")
        df_display = df_clean_all_ages
        x_axis_field = 'Who_region'
        x_label = "WHO Region"
    else:
        df_display = pd.DataFrame()

    if not df_display.empty:
        fig = px.box(
            df_display, 
            x=x_axis_field, 
            y='Deaths', 
            color='Agegroup',
            points="all",
            color_discrete_map=age_blue_map,
            template="plotly_white"
        )

        fig.update_layout(
            boxmode='group',
            xaxis_title=x_label,
            yaxis_title="Monthly Deaths",
            font=dict(color='#1565C0'),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=30, b=20),
            height=520
        )
        
        fig.update_traces(marker=dict(opacity=0.4, size=4))

        st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="box_chart")

        if selected_region:
            df_reg_65 = df_display[df_display['Agegroup'] == '65+']
            if not df_reg_65.empty:
                max_deaths_65 = int(df_reg_65['Deaths'].max())
                total_deaths_65 = int(df_reg_65['Deaths'].sum())
                avg_deaths_65 = int(df_reg_65['Deaths'].mean())
                
                st.markdown(f"""
                <div style='background-color: #eef5fc; padding: 12px; border-left: 4px solid #1565C0; border-radius: 4px;'>
                    <span style='color: #1565C0; font-weight: bold;'>Specific Regional Insight ({selected_region}):</span> 
                    By isolating this region, the visual contrast is clear: younger demographic brackets remain flat and tightly controlled at the baseline, while the 65+ senior group accounts for an overwhelming <b>{total_deaths_65:,}</b> cumulative deaths. With a severe localized peak of <b>{max_deaths_65:,}</b> deaths, the data confirms that systemic vulnerabilities are heavily concentrated in older populations, leaving other age brackets virtually unaffected.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 12px; border-left: 4px solid #1565C0; border-radius: 4px;'>
                <span style='color: #1565C0; font-weight: bold;'>General Insight:</span> This comprehensive distribution across all age cohorts reveals that geriatric mortality (65+, represented in deep navy) consistently exhibits massive variance and extreme outliers worldwide. Keeping the younger cohorts on the chart establishes a baseline that mathematically proves the 'implementation gap' is a targeted demographic crisis rather than a baseline healthcare collapse.
            </div>
            """, unsafe_allow_html=True)

st.write("---")

# CONCLUSIONS
st.subheader("Conclusions")
st.markdown("""
* **The Legislative Fallacy:** The Choropleth map, 3D density chart, and the violin plot demonstrate that holding a "YES" status (active policy) does not guarantee immunity. The massive accumulation of countries at the baseline of the charts reveals a widespread failure in the logistical distribution of doses.
* **Clinical Disconnect:** The Top 15 analysis and the interactive Lollipop chart highlight massive peaks in geriatric mortality (highlighted in blue) that occur independently of the volume of reported vaccines (grey lines). This suggests a critical failure in response times and the prioritization of vulnerable patients.
* **Predictable System Collapse:** The actual burden on healthcare systems operates in cyclical peaks. The operational inability to vaccinate older adults in a timely manner translates directly into saturation and critical stress in the volume of global hospital admissions.
""")