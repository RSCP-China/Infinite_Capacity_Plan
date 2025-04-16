import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import codecs

st.set_page_config(page_title="无限产能规划", layout="wide")
st.title("无限产能规划工具")

def try_read_csv(file, encodings=['gbk', 'gb2312', 'utf-8']):
    """尝试使用不同编码读取CSV文件"""
    for encoding in encodings:
        try:
            # Reset file pointer to start
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
            st.sidebar.write(f"成功使用 {encoding} 编码读取文件")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"读取文件时出错: {str(e)}")
            return None
    st.error("无法使用支持的编码读取文件（尝试过GBK、GB2312和UTF-8）")
    return None

def load_data(load_file, resource_file):
    """加载生产负荷和资源数据"""
    try:
        # Load data with multiple encoding support
        load_df = try_read_csv(load_file)
        if load_df is None:
            return None, None
            
        resource_df = try_read_csv(resource_file)
        if resource_df is None:
            return None, None
        
        # Display data info
        st.sidebar.subheader("数据加载信息")
        st.sidebar.write(f"负荷数据行数: {len(load_df)}")
        st.sidebar.write(f"资源数据行数: {len(resource_df)}")
        
        # 转换日期列
        try:
            load_df['Due Date'] = pd.to_datetime(load_df['Due Date'])
        except Exception as e:
            st.error(f"转换日期时出错: {str(e)}")
            st.error("请确保Due Date列的格式正确（例如：YYYY-MM-DD）")
            return None, None
        
        return load_df, resource_df
        
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        return None, None

def calculate_daily_load(load_df, start_date, end_date):
    """计算每个工作中心的日负荷"""
    try:
        # 创建日期范围
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 过滤日期范围内的数据
        mask = (load_df['Due Date'] >= start_date) & (load_df['Due Date'] <= end_date)
        filtered_df = load_df[mask]
        
        if len(filtered_df) == 0:
            st.warning(f"所选日期范围内没有数据: {start_date.date()} 到 {end_date.date()}")
            return None
        
        # 按工作中心和日期分组计算负荷
        daily_load = filtered_df.groupby(['WorkCenter', 'Due Date']).agg({
            'Run Time': 'sum',
            'Setup Time': 'sum',
            'Quantity': 'sum'
        }).reset_index()
        
        return daily_load
        
    except Exception as e:
        st.error(f"计算日负荷时出错: {str(e)}")
        return None

def aggregate_by_period(df, period='W'):
    """按周或月聚合数据"""
    try:
        # 创建周期标签
        if period == 'W':
            period_label = df['Due Date'].dt.strftime('%Y-W%U')
        else:  # 'M'
            period_label = df['Due Date'].dt.strftime('%Y-%m')
        
        # 创建带有周期标签的临时数据框
        temp_df = df.copy()
        temp_df['Period'] = period_label
        
        # 只聚合数值列
        aggregated = temp_df.groupby(['WorkCenter', 'Period']).agg({
            'Run Time': 'sum',
            'Setup Time': 'sum',
            'Quantity': 'sum',
            'Total Time': 'sum'
        }).reset_index()
        
        return aggregated
        
    except Exception as e:
        st.error(f"聚合数据时出错: {str(e)}")
        return None

def calculate_utilization(load_df, resource_df, start_date, end_date, period='D'):
    """计算产能利用率"""
    try:
        # 获取日负荷
        daily_load = calculate_daily_load(load_df, start_date, end_date)
        if daily_load is None:
            return None
            
        # 计算总工时需求（运行时间 + 设置时间）
        daily_load['Total Time'] = daily_load['Run Time'] + daily_load['Setup Time']
        
        # 如果需要按周或月聚合
        if period in ['W', 'M']:
            daily_load = aggregate_by_period(daily_load, period)
            if daily_load is None:
                return None
        
        # 合并资源可用性数据
        result = pd.merge(daily_load, resource_df[['WorkCenter', 'Available Quantity', 'Shift hours']], 
                         on='WorkCenter', how='left')
        
        # 计算可用产能和利用率
        result['Available Capacity'] = result['Available Quantity'] * result['Shift hours']
        result['Utilization'] = (result['Total Time'] / result['Available Capacity']) * 100
        
        # Round numerical columns
        result = result.round(2)
        
        return result
        
    except Exception as e:
        st.error(f"计算利用率时出错: {str(e)}")
        return None

def apply_color_scale(value):
    """根据利用率返回颜色"""
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
    # 文件上传
    st.header("数据文件上传")
    col1, col2 = st.columns(2)
    
    with col1:
        load_file = st.file_uploader("上传负荷数据文件 (Load.CSV)", type=['csv'])
    
    with col2:
        resource_file = st.file_uploader("上传资源数据文件 (Resource.CSV)", type=['csv'])
    
    if not (load_file and resource_file):
        st.warning("请上传所需的数据文件")
        return
    
    # 侧边栏：时间范围选择
    with st.sidebar:
        st.header("参数设置")
        
        # 时间范围选择
        min_date = datetime.now()
        max_date = min_date + timedelta(days=365)
        
        start_date = st.date_input("开始日期", min_date)
        end_date = st.date_input("结束日期", min_date + timedelta(days=30))
        
        if start_date > end_date:
            st.error("结束日期必须晚于开始日期")
            return
        
        # 聚合周期选择
        period = st.selectbox("聚合周期", 
                            options=['日', '周', '月'],
                            format_func=lambda x: {'日': 'Daily', '周': 'Weekly', '月': 'Monthly'}[x])
    
    # 加载数据
    load_df, resource_df = load_data(load_file, resource_file)
    
    if load_df is not None and resource_df is not None:
        # 转换聚合周期
        period_map = {'日': 'D', '周': 'W', '月': 'M'}
        
        # 计算利用率
        utilization_df = calculate_utilization(
            load_df, 
            resource_df,
            pd.Timestamp(start_date),
            pd.Timestamp(end_date),
            period_map[period]
        )
        
        if utilization_df is not None:
            # 显示结果
            st.header("产能利用率分析")
            
            # 格式化显示
            display_df = utilization_df.style.applymap(
                apply_color_scale, 
                subset=['Utilization']
            )
            
            st.dataframe(display_df, use_container_width=True)
            
            # 添加下载按钮
            csv = utilization_df.to_csv(index=False)
            st.download_button(
                label="下载数据",
                data=csv,
                file_name=f"capacity_utilization_{period}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
