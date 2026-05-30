# Earthquake Simulation - Team 3 Final Project

## Project Overview

This project analyzes earthquake data and creates geographical visualizations. The team is divided into two main components:
- **Data Processing & Analysis** (Greedy Algorithm) - processes CSV data and generates analysis results
- **Geo-Visualization** (Mapping) - visualizes the analyzed data on interactive maps

## Project Structure

```
earthquake-simulation/
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
│
├── data/
│   ├── input/
│   │   ├── [CSV File 1]        # Input data file 1
│   │   ├── [CSV File 2]        # Input data file 2
│   │   └── input_data.json     # JSON input from preprocessing
│   └── output/
│       └── analysis_result.json # Output from greedy algorithm
│
├── src/
│   ├── __init__.py
│   ├── algorithm.py            # Greedy algorithm implementation
│   ├── processor.py            # Data processing & analysis logic
│   └── utils.py                # Helper functions
│
└── notebooks/
    └── analysis.ipynb          # Original analysis notebook
```

## Team Responsibilities

### Part 1: Data Processing & Greedy Algorithm
**Assigned to:** [Your Name]

**Tasks:**
- Read and parse two CSV files
- Process JSON input data
- Apply greedy algorithm for earthquake data analysis
- Output results as JSON
- Pass results to visualization team

**Input:** 2 CSV files + JSON data
**Output:** JSON analysis results

### Part 2: Geo-Visualization & Mapping
**Assigned to:** [Mapping Team Member]

**Tasks:**
- Receive JSON analysis from Part 1
- Combine with geographical data
- Create interactive map visualizations
- Display earthquake patterns/analysis

**Input:** JSON analysis results + Geo data
**Output:** Interactive map/visualization

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Analysis
```bash
python src/processor.py
```

This will:
- Read data from `data/input/`
- Apply the greedy algorithm
- Generate output in `data/output/analysis_result.json`

### 3. Pass Results to Mapping Team
The JSON file in `data/output/` is ready for the mapping visualization step.

## Technologies Used
- **Python 3.x** - Main programming language
- **Pandas** - Data processing
- **NumPy** - Numerical computations
- **JSON** - Data serialization
- *(Add mapping libraries here: Folium, Leaflet, etc.)*

## Getting Started

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements.txt`
5. Add your CSV files to `data/input/`
6. Modify `src/processor.py` with your algorithm

## Next Steps

- [ ] Implement greedy algorithm in `src/algorithm.py`
- [ ] Create data processing pipeline in `src/processor.py`
- [ ] Test with sample data
- [ ] Generate JSON output
- [ ] Coordinate with mapping team for visualization

## Team Contact
- Data Processing: [Your Name/Contact]
- Mapping: [Team Member Name/Contact]

---

*Last Updated: May 2026*
