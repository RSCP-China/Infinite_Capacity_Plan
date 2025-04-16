# 无限产能规划工具

## 功能说明
- 上传自定义负荷数据(Load.CSV)和资源数据(Resource.CSV)
- 按日/周/月查看产能利用率
- 利用率热力图显示（红色>100%, 黄色80-100%, 绿色<80%）
- 数据导出功能

## 使用说明

1. 启动应用：
```bash
streamlit run app.py
```

2. 准备数据文件：

### Load.CSV 格式要求：
- Job Number（工单号）
- Part Number（零件号）
- Due Date（交期, 格式: YYYY-MM-DD）
- Priority（优先级）
- Quantity（数量）
- WorkCenter（工作中心）
- Run Time（运行时间）
- Setup Time（设置时间）
- Place（地点）
- Customer（客户）

### Resource.CSV 格式要求：
- WorkCenter（工作中心）
- Available Quantity（可用数量）
- Shift hours（班次小时数）
- Shift Pattern（班次模式）
- Place（地点）

3. 使用步骤：
   1) 上传数据文件：
      - 点击"上传负荷数据文件"选择Load.CSV
      - 点击"上传资源数据文件"选择Resource.CSV
   
   2) 在左侧边栏设置：
      - 选择开始日期
      - 选择结束日期
      - 选择显示周期（日/周/月）

   3) 查看结果：
      - 产能利用率表格会自动更新
      - 使用颜色标识不同利用率水平
      - 可点击"下载数据"保存结果

## 系统要求
- Python 3.7+
- 依赖包：
```bash
pip install -r requirements.txt
```

## 注意事项
- 确保CSV文件编码为UTF-8
- 日期格式必须为YYYY-MM-DD
- 工作中心名称在Load.CSV和Resource.CSV中必须保持一致
- 数值型字段不要包含特殊字符（如逗号、货币符号等）