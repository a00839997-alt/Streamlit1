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
    df_hosp['Date_reported'] = pd.to_datetime(df_hosp['Date_reported'])
    hosp_trend = df_hosp.groupby('Date_reported')['Covid_new_hospitalizations_last_7days'].sum().reset_index()
    return df_merged, hosp_trend, df_deaths

df_merged, hosp_trend, df_deaths = load_data()

# DYNAMIC FILTERING LOGIC
st.sidebar.header("Dashboard Filters")
selected_regions = st.sidebar.multiselect("Select WHO Regions:", options=df_merged['Who_region'].unique(), default=df_merged['Who_region'].unique())
df_filtered = df_merged[df_merged['Who_region'].isin(selected_regions)]

color_insight = '#1f77b4' 
color_base = '#d3d3d3'

# MASTER FILTER MAP
st.subheader("The Global Implementation Gap: Select a Country")
fig_map = px.choropleth(df_filtered[df_filtered['VALUE'] == 'YES'], locations="iso_code", color="Log_Deaths", hover_data={"Deaths": True}, color_continuous_scale=px.colors.sequential.Blues)
fig_map.update_layout(template="plotly_white", margin=dict(l=0,r=0,t=10,b=0), height=400)
event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")

if event and event["selection"]["points"]:
    df_filtered = df_filtered[df_filtered['iso_code'] == event["selection"]["points"][0]["location"]]

# ROW 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Implementation Gap: Mortality (Top 15)")
    top15 = df_filtered.sort_values('Deaths', ascending=False).head(15)
    fig2 = go.Figure(go.Bar(x=top15['iso_code'], y=top15['Deaths'], marker_color=color_insight))
    fig2.update_layout(template="plotly_white", yaxis=dict(title=dict(text='Total Deaths', font=dict(color=color_insight))), xaxis=dict(title='Country ISO Code'))
    st.plotly_chart(fig2, use_container_width=True)
    ratio = (top15['COVID_VACCINE_ADM_1D'].sum() / (top15['Deaths'].sum() + 1))
    st.markdown(f"**Data Insight:** Current ratio is {ratio:.2f} doses per death, indicating a { (1/ratio if ratio > 0 else 0)*100:.2f}% mortality impact per dose.")

with col2:
    st.subheader("Implementation Gap: Administered Doses (Top 15)")
    fig3 = go.Figure(go.Scatter(x=top15['iso_code'], y=top15['COVID_VACCINE_ADM_1D'], mode='lines+markers', line=dict(color=color_insight, width=3)))
    fig3.update_layout(template="plotly_white", yaxis=dict(title=dict(text='Administered Doses', font=dict(color=color_base))), xaxis=dict(title='Country ISO Code'))
    st.plotly_chart(fig3, use_container_width=True)

# ROW 3
col3, col4 = st.columns(2)
with col3:
    st.subheader("Operational Failure: The 'YES' Policy Toll")
    # (Mantener tu lógica original de Lollipop)
    st.plotly_chart(go.Figure(), use_container_width=True) 

with col4:
    st.subheader("Healthcare System Stress")
    fig5 = px.area(hosp_trend, x='Date_reported', y='Covid_new_hospitalizations_last_7days')
    st.plotly_chart(fig5, use_container_width=True)

# ROW 4 (CUADRANTE 5)
col5 = st.columns(1)[0]
with col5:
    st.subheader("Distribution of Deaths by Region and Age Group")
    df_clean = df_deaths.merge(df_filtered[['iso_code']], on='iso_code').dropna(subset=['Deaths'])
    fig = px.box(df_clean, x='Who_region', y='Deaths', color='Agegroup', points="all", template="plotly_white")
    fig.update_layout(xaxis=dict(title=dict(text="WHO Region", font=dict(color=color_base))), yaxis=dict(title=dict(text="Monthly Deaths", font=dict(color=color_insight))))
    st.plotly_chart(fig, use_container_width=True)

# CONCLUSIONS
st.subheader("Executive Conclusions")
st.markdown("""
* **The Legislative Fallacy:** The Choropleth map, 3D density chart, and the violin plot demonstrate that holding a "YES" status (active policy) does not guarantee immunity.
* **Clinical Disconnect:** The Top 15 analysis highlights massive peaks in geriatric mortality that occur independently of the volume of reported vaccines.
* **Predictable System Collapse:** The operational inability to vaccinate older adults in a timely manner translates directly into saturation and critical stress in the volume of global hospital admissions.
""")