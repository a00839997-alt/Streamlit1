import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Sales Dashboard") #App title
uploaded_file = st.file_uploader("Upload your sales data (XLSX)", type="xlsx") #File uploader: Accepts only xlsx files

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)  #Read the Excel file into a DataFrame

    df['VENDOR'] = df['NAME'] + ' ' + df['LASTNAME']#Combine name and lastname into a single vendor column

    st.subheader("Region filtered data") #Dropdown to filter by region
    regions = ["All"] + list(df['REGION'].unique()) #Add "All" to the list of regions for filtering
    selected_region = st.selectbox("Select a region", regions)
    filtered_data = df if selected_region == "All" else df[df['REGION'] == selected_region]  #Filter data based on selected region

    st.subheader("Specific vendors") #Show filtered table
    st.write(filtered_data)

    st.subheader("Vendor details")  #Dropdown to select a specific vendor
    selected_vendor = st.selectbox("Select a vendor", sorted(df['VENDOR'].unique()))
    vendor_df = df[df['VENDOR'] == selected_vendor] #Filter and display data for the selected vendor
    st.write(vendor_df)

    #Display three charts side by side
    st.subheader("Sales Graphs")

    #Units sold per region
    st.write("Units Sold")
    st.bar_chart(filtered_data.groupby('VENDOR')['SOLD UNITS'].sum(), color= "orange")
    st.bar_chart(filtered_data.groupby('REGION')['SOLD UNITS'].sum(), color= "orange")
    st.divider() #Add a divider between charts
    
    #Total sales per vendor
    st.write("Total Sales")
    st.bar_chart(filtered_data.groupby(['VENDOR'])['TOTAL SALES'].sum(), color= "green")
    st.divider() #Add a divider between charts

    #Average sales per region
    st.write("Average Sales")
    st.bar_chart(filtered_data.groupby('VENDOR')['SALES AVERAGE'].mean(), color='#008080')
    st.bar_chart(filtered_data.groupby('REGION')['SALES AVERAGE'].mean(), color='#008080')


else:
    with st.spinner("Waiting for file upload..."): # Show a spinner while waiting
        st.empty()