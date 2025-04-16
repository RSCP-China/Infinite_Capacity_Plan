# Infinite Capacity Planning Application

## 1. Project Structure
```
infinite_capacity_planner/
├── app.py              # Main Streamlit app
├── utils.py            # Helper utility functions  
├── requirements.txt    # Dependencies
├── README.md           # Usage instructions
└── data/               # Data directory
    ├── Load.CSV        # Production order data
    └── Resource.CSV    # Resource/work center data
```

## 2. Application Flow
1. **Load Data**
   - Allow user to upload Load.CSV and Resource.CSV files
   - Validate and load data into pandas DataFrames

2. **Filter Data**
   - Provide date range picker to filter load data
   - Apply date filter on load data

3. **Prepare Data**
   - Group load data by work center and aggregate quantities
   - Join with resource data to get available capacity
   - Calculate utilization percentage 

4. **Display Results**
   - Create an interactive table with:
     - Work Center as rows
     - Columns for required capacity, available capacity, utilization %
     - Apply color coding based on utilization levels
   - Allow toggling between day/week/month views

5. **UI Components**
   - File uploaders for Load.CSV and Resource.CSV
   - Date range picker 
   - Toggle for view granularity (day/week/month)
   - Utilization table

## 3. Implementation Steps
1. Set up project structure and dependencies
2. Implement data loading and validation
3. Create date filtering functionality
4. Develop data preparation logic 
5. Build utilization calculation
6. Create utilization table with color coding
7. Integrate UI components
8. Add usage instructions and documentation

## 4. Dependencies
- streamlit
- pandas
- plotly (optional - for visualization)
- numpy