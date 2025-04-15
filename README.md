# Infinite Capacity Planning Tool

A Streamlit-based web application for capacity planning and resource management.

## Features

- Upload and process Load.CSV and Resource.CSV files
- View monthly and weekly capacity requirements
- Analyze resource availability by work center
- Calculate daily resource hours and aggregate into monthly/weekly views

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd infinite-capacity-plan
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (usually http://localhost:8501)

3. Upload your Load.CSV and Resource.CSV files:
   - Load.CSV should contain: Job Number, Part Number, Due Date, Priority, Quantity, WorkCenter, Run Time, Setup Time, Place, Customer
   - Resource.CSV should contain: WorkCenter, Available Quantity, Shift Hours, Place

## Data Format

### Load.CSV
- Job Number: Unique identifier for each job
- Part Number: Identifier for the part being manufactured
- Due Date: Target completion date (DD/MM/YYYY)
- Priority: Job priority
- Quantity: Number of parts to be produced
- WorkCenter: Production work center ID
- Run Time: Processing time per unit
- Setup Time: Initial setup time
- Place: Location identifier
- Customer: Customer name/ID

### Resource.CSV
- WorkCenter: Work center identifier
- Available Quantity: Number of resources available
- Shift Hours: Working hours per shift
- Place: Location identifier