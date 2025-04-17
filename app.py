import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import codecs

# Language dictionary
TRANSLATIONS = {
    "中文": {
        "title": "无限产能规划工具",
        "file_upload_header": "数据文件上传",
        "load_file_label": "上传负荷数据文件 (Load.CSV)",
        "resource_file_label": "上传资源数据文件 (Resource.CSV)",
        "upload_warning": "请上传所需的数据文件",
        "settings": "参数设置",
        "data_info": "数据加载信息",
        "load_rows": "负荷数据行数",
        "resource_rows": "资源数据行数",
        "start_date": "开始日期",
        "end_date": "结束日期",
        "date_error": "结束日期必须晚于开始日期",
        "period": "聚合周期",
        "daily": "日",
        "weekly": "周",
        "monthly": "月",
        "result_header": "产能利用率分析",
        "download_button": "下载数据",
        "encoding_success": "成功使用 {} 编码读取文件",
        "encoding_error": "无法使用支持的编码读取文件（尝试过GBK、GB2312和UTF-8）",
        "loading_error": "加载数据时出错: {}",
        "date_convert_error": "转换日期时出错: {}\n请确保Due Date列的格式正确（例如：YYYY-MM-DD）",
        "no_data_warning": "所选日期范围内没有数据: {} 到 {}",
        "daily_load_error": "计算日负荷时出错: {}",
        "aggregation_error": "聚合数据时出错: {}",
        "utilization_error": "计算利用率时出错: {}"
    },
    "English": {
        "title": "Infinite Capacity Planning Tool",
        "file_upload_header": "Data File Upload",
        "load_file_label": "Upload Load Data File (Load.CSV)",
        "resource_file_label": "Upload Resource Data File (Resource.CSV)",
        "upload_warning": "Please upload the required data files",
        "settings": "Settings",
        "data_info": "Data Loading Info",
        "load_rows": "Load Data Rows",
        "resource_rows": "Resource Data Rows",
        "start_date": "Start Date",
        "end_date": "End Date",
        "date_error": "End date must be after start date",
        "period": "Aggregation Period",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "result_header": "Capacity Utilization Analysis",
        "download_button": "Download Data",
        "encoding_success": "Successfully read file using {} encoding",
        "encoding_error": "Cannot read file with supported encodings (tried GBK, GB2312, and UTF-8)",
        "loading_error": "Error loading data: {}",
        "date_convert_error": "Error converting date: {}\nPlease ensure Due Date column format is correct (e.g., YYYY-MM-DD)",
        "no_data_warning": "No data in selected date range: {} to {}",
        "daily_load_error": "Error calculating daily load: {}",
        "aggregation_error": "Error aggregating data: {}",
        "utilization_error": "Error calculating utilization: {}"
    }
}

# Initialize session state for language selection
if 'language' not in st.session_state:
    st.session_state['language'] = "中文"

st.set_page_config(page_title="产能规划", layout="wide")

# Language selector in sidebar
language = st.sidebar.selectbox(
    "Language/语言",
    ["中文", "English"],
    index=0 if st.session_state['language'] == "中文" else 1
)
st.session_state['language'] = language

# Get translations for current language
t = TRANSLATIONS[language]

st.title(t["title"])

def try_read_csv(file, encodings=['gbk', 'gb2312', 'utf-8']):
    """尝试使用不同编码读取CSV文件"""
    for encoding in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
            st.sidebar.write(t["encoding_success"].format(encoding))
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(t["loading_error"].format(str(e)))
            return None
    st.error(t["encoding_error"])
    return None

def load_data(load_file, resource_file):
    try:
        load_df = try_read_csv(load_file)
        if load_df is None:
            return None, None
            
        resource_df = try_read_csv(resource_file)
        if resource_df is None:
            return None, None
        
        st.sidebar.subheader(t["data_info"])
        st.sidebar.write(f"{t['load_rows']}: {len(load_df)}")
        st.sidebar.write(f"{t['resource_rows']}: {len(resource_df)}")
        
        try:
            load_df['Due Date'] = pd.to_datetime(load_df['Due Date'])
        except Exception as e:
            st.error(t["date_convert_error"].format(str(e)))
            return None, None
        
        return load_df, resource_df
        
    except Exception as e:
        st.error(t["loading_error"].format(str(e)))
        return None, None

def calculate_daily_load(load_df, start_date, end_date):
    try:
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        mask = (load_df['Due Date'] >= start_date) & (load_df['Due Date'] <= end_date)
        filtered_df = load_df[mask]
        
        if len(filtered_df) == 0:
            st.warning(t["no_data_warning"].format(start_date.date(), end_date.date()))
            return None
        
        daily_load = filtered_df.groupby(['WorkCenter', 'Due Date']).agg({
            'Run Time': 'sum',
            'Setup Time': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        return daily_load
        
    except Exception as e:
        st.error(t["daily_load_error"].format(str(e)))
        return None

def aggregate_by_period(df, period='W'):
    try:
        if period == 'W':
            period_label = df['Due Date'].dt.strftime('%Y-W%U')
        else:  # 'M'
            period_label = df['Due Date'].dt.strftime('%Y-%m')
        
        temp_df = df.copy()
        temp_df['Period'] = period_label
        
        aggregated = temp_df.groupby(['WorkCenter', 'Period']).agg({
            'Run Time': 'sum',
            'Setup Time': 'sum',
            'Quantity': 'sum',
            'Total Time': 'sum'
        }).reset_index()
        
        return aggregated
        
    except Exception as e:
        st.error(t["aggregation_error"].format(str(e)))
        return None

def calculate_utilization(load_df, resource_df, start_date, end_date, period='D'):
    try:
        daily_load = calculate_daily_load(load_df, start_date, end_date)
        if daily_load is None:
            return None
            
        daily_load['Total Time'] = daily_load['Run Time'] + daily_load['Setup Time']
        
        if period in ['W', 'M']:
            daily_load = aggregate_by_period(daily_load, period)
            if daily_load is None:
                return None
        
        result = pd.merge(daily_load, resource_df[['WorkCenter', 'Available Quantity', 'Shift hours']], 
                         on='WorkCenter', how='left')
        
        result['Available Capacity'] = result['Available Quantity'] * result['Shift hours']
        result['Utilization'] = (result['Total Time'] / result['Available Capacity']) * 100
        
        result = result.round(2)
        
        return result
        
    except Exception as e:
        st.error(t["utilization_error"].format(str(e)))
        return None

def apply_color_scale(value):
    try:
        if pd.isna(value):
            return ''
        if value >= 100:
            return 'background-color: red'
        elif value >= 80:
            return 'background-color: yellow'
        else:
            return 'background-color: green'
    except:
        return ''

def main():
    st.header(t["file_upload_header"])
    col1, col2 = st.columns(2)
    
    with col1:
        load_file = st.file_uploader(t["load_file_label"], type=['csv'])
    
    with col2:
        resource_file = st.file_uploader(t["resource_file_label"], type=['csv'])
    
    if not (load_file and resource_file):
        st.warning(t["upload_warning"])
        return
    
    with st.sidebar:
        st.header(t["settings"])
        
        min_date = datetime.now()
        max_date = min_date + timedelta(days=365)
        
        start_date = st.date_input(t["start_date"], min_date)
        end_date = st.date_input(t["end_date"], min_date + timedelta(days=30))
        
        if start_date > end_date:
            st.error(t["date_error"])
            return
        
        period = st.selectbox(
            t["period"], 
            options=[t["daily"], t["weekly"], t["monthly"]],
        )
    
    load_df, resource_df = load_data(load_file, resource_file)
    
    if load_df is not None and resource_df is not None:
        period_map = {
            t["daily"]: 'D',
            t["weekly"]: 'W',
            t["monthly"]: 'M'
        }
        
        utilization_df = calculate_utilization(
            load_df, 
            resource_df,
            pd.Timestamp(start_date),
            pd.Timestamp(end_date),
            period_map[period]
        )
        
        if utilization_df is not None:
            st.header(t["result_header"])
            
            display_df = utilization_df.style.applymap(
                apply_color_scale, 
                subset=['Utilization']
            )
            
            st.dataframe(display_df, use_container_width=True)
            
            csv = utilization_df.to_csv(index=False)
            st.download_button(
                label=t["download_button"],
                data=csv,
                file_name=f"capacity_utilization_{period}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
