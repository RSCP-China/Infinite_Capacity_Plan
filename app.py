import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Capacity Planning Tool", layout="wide")

def load_csv_data(uploaded_file):
    if uploaded_file is not None:
        try:
            # Try different encodings
            encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
            for encoding in encodings:
                try:
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    uploaded_file.seek(0)  # Reset file pointer for next attempt
                    continue
                except Exception as e:
                    st.error(f"Error reading file with {encoding} encoding: {str(e)}")
                    uploaded_file.seek(0)
                    continue
            
            st.error("Could not read the file with any supported encoding")
            return None
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    return None

def create_daily_resource_data(resource_df, start_date, end_date):
    """Create daily resource availability data"""
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    daily_resources = []
    
    for _, row in resource_df.iterrows():
        for date in dates:
            daily_resources.append({
                'Date': date,
                'WorkCenter': row['WorkCenter'],
                'Place': row['Place'],
                'Daily Hours': row['Available Quantity'] * row['Shift hours']
            })
    
    return pd.DataFrame(daily_resources)

def process_capacity_data(load_df, resource_df):
    if load_df is None or resource_df is None:
        return None, None, None, None
    
    try:
        # Display raw data for debugging
        st.write("Load Data:")
        st.write(load_df.head())
        st.write("\nResource Data:")
        st.write(resource_df.head())
        
        # Convert date to datetime
        if 'Due Date' in load_df.columns:
            st.write("\nSample Due Date value:", load_df['Due Date'].iloc[0])
            load_df['Due Date'] = pd.to_datetime(load_df['Due Date'], dayfirst=True)
            st.write("Date conversion successful")
        else:
            st.error("Due Date column not found in Load data")
            return None, None, None, None
        
        # Get date range from load data
        start_date = load_df['Due Date'].min()
        end_date = load_df['Due Date'].max()
        
        # Create daily resource data
        daily_resource_df = create_daily_resource_data(resource_df, start_date, end_date)
        
        # Calculate monthly capacity requirements
        monthly_load = (
            load_df.groupby([pd.Grouper(key='Due Date', freq='ME'), 'WorkCenter'])
            ['Quantity'].sum()
            .reset_index()
        )
        monthly_load = monthly_load.pivot(
            index='Due Date',
            columns='WorkCenter',
            values='Quantity'
        ).fillna(0).reset_index()
        monthly_load.columns.name = None
        
        # Calculate monthly resource availability
        monthly_resource = (
            daily_resource_df.groupby([pd.Grouper(key='Date', freq='ME'), 'WorkCenter'])
            ['Daily Hours'].sum()
            .reset_index()
        )
        monthly_resource = monthly_resource.pivot(
            index='Date',
            columns='WorkCenter',
            values='Daily Hours'
        ).fillna(0).reset_index()
        monthly_resource.columns.name = None
        
        # Calculate weekly capacity requirements
        weekly_load = (
            load_df.groupby([pd.Grouper(key='Due Date', freq='W-MON'), 'WorkCenter'])
            ['Quantity'].sum()
            .reset_index()
        )
        weekly_load = weekly_load.pivot(
            index='Due Date',
            columns='WorkCenter',
            values='Quantity'
        ).fillna(0).reset_index()
        weekly_load.columns.name = None
        
        # Calculate weekly resource availability
        weekly_resource = (
            daily_resource_df.groupby([pd.Grouper(key='Date', freq='W-MON'), 'WorkCenter'])
            ['Daily Hours'].sum()
            .reset_index()
        )
        weekly_resource = weekly_resource.pivot(
            index='Date',
            columns='WorkCenter',
            values='Daily Hours'
        ).fillna(0).reset_index()
        weekly_resource.columns.name = None
        
        # Rename date columns
        monthly_load = monthly_load.rename(columns={'Due Date': 'Month'})
        monthly_resource = monthly_resource.rename(columns={'Date': 'Month'})
        weekly_load = weekly_load.rename(columns={'Due Date': 'Week'})
        weekly_resource = weekly_resource.rename(columns={'Date': 'Week'})
        
        return monthly_load, monthly_resource, weekly_load, weekly_resource
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None, None, None, None

def display_capacity_tables(monthly_load, monthly_resource, weekly_load, weekly_resource):
    if monthly_load is None or monthly_resource is None or weekly_load is None or weekly_resource is None:
        return
    
    try:
        st.header("Capacity Overview")
        
        # Monthly View
        st.subheader("Monthly View")
        st.write("Load Requirements by Work Center:")
        st.dataframe(monthly_load)
        st.write("Resource Availability by Work Center (Hours per Month):")
        st.dataframe(monthly_resource)
        
        # Weekly View
        st.subheader("Weekly View")
        st.write("Load Requirements by Work Center:")
        st.dataframe(weekly_load)
        st.write("Resource Availability by Work Center (Hours per Week):")
        st.dataframe(weekly_resource)
        
    except Exception as e:
        st.error(f"Error displaying tables: {str(e)}")

def main():
    st.title("Infinite Capacity Planning Tool")
    
    # File upload section
    st.header("Upload Data Files")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Load Requirements")
        load_file = st.file_uploader("Upload Load.CSV", type=['csv'])
        if load_file:
            st.write("File name:", load_file.name)
        
    with col2:
        st.subheader("Resource Availability")
        resource_file = st.file_uploader("Upload Resource.CSV", type=['csv'])
        if resource_file:
            st.write("File name:", resource_file.name)
    
    # Load and process data
    load_df = load_csv_data(load_file)
    resource_df = load_csv_data(resource_file)
    
    # Process data when both files are uploaded
    if load_df is not None and resource_df is not None:
        monthly_load, monthly_resource, weekly_load, weekly_resource = process_capacity_data(load_df, resource_df)
        display_capacity_tables(monthly_load, monthly_resource, weekly_load, weekly_resource)
    else:
        st.info("Please upload both Load.CSV and Resource.CSV files to view capacity analysis.")

if __name__ == "__main__":
    main()