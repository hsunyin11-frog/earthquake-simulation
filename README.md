# Earthquake Simulation - Team 3 Final Project

## Project Overview

This project simulates earthquake impacts and optimizes refugee allocation to shelters. The system follows a complete workflow:

1. **Collect Data** - Load village population and shelter location data from CSV files and shapefiles
2. **Calculate Refugees** - Use earthquake physics equations (PGA, intensity, damage rates) to estimate displacement from epicenter, magnitude, and structural vulnerability
3. **Refugee Allocation** - Apply a greedy algorithm to optimally assign displaced people to nearby shelters
4. **Analysis & Visualization** - Combine simulation results with geographical data to create comprehensive disaster impact maps
5. **Web Interface** - Deploy as an interactive Streamlit web application for real-time scenario simulation

## Project Structure

```
earthquake-simulation/
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
│
├── main/
│   └── app.py                         # Main Streamlit application
│
├── data/
│   ├── village.csv                    # Village population & structural data
│   ├── shelter.csv                    # Shelter locations & capacity
│   ├── village_boundary.shp           # Shapefile: Village boundaries (geometry)
│   ├── village_boundary.shx           # Shapefile: Index file
│   ├── village_boundary.dbf           # Shapefile: Attribute data
│   ├── village_boundary.cpg           # Shapefile: Code page
│   └── village_boundary.prj           # Shapefile: Projection info
│
└── notebooks/
    ├── 受災人數計算.ipynb
    └── refugee_allocation_v2.ipynb    # Development & analysis notebook (reference)
```

**Note on notebooks:** The `受災人數計算.ipynb` and `refugee_allocation_v2.ipynb` are development notebooks used to prototype and test the calculation as well as the algorithm logic.

## Technologies Used

- **Python 3.x** - Core programming language
- **Streamlit** - Web framework for interactive application
- **Pandas** - Data processing and manipulation
- **GeoPandas** - Geospatial data handling
- **Folium** - Interactive map visualization
- **NumPy** - Numerical computations
- **Shapefile (.shp)** - Geographical boundary data format

## Core Features

### 1. Earthquake Impact Simulation
- **Haversine Distance Calculation** - Accurate distance from epicenter to villages
- **PGA (Peak Ground Acceleration) Estimation** - Physics-based formula for ground motion prediction
- **Intensity Classification** - Maps PGA to Taiwan Seismic Intensity Scale (0-7)
- **Damage Rate Calculation** - Estimates % of population needing evacuation based on building age

### 2. Greedy Refugee Allocation Algorithm
- Prioritizes zones with highest refugee numbers
- Assigns to nearest available shelters first
- Handles overflow by distributing to shelters with lowest utilization
- Tracks allocation status (normal/overflow)

### 3. Interactive Visualization
- **Color-coded Risk Map** - Shows disaster severity by district
- **Shelter Markers** - Blue (normal capacity) / Red (overflow)
- **Distance Distribution Chart** - Analyzes evacuation distances
- **Capacity Statistics** - Real-time shelter utilization metrics

### 4. Scenario Comparison
- Compare multiple earthquake magnitudes simultaneously
- Analyze how different parameters affect refugee numbers and shelter capacity

## Data Requirements

### `village.csv` Columns:
- `name1` - District name (行政區)
- `name2` - Village name (里名)
- `lat`, `lon` - Geographic coordinates
- `population` - Population in village
- `old house ratio` - Percentage of older buildings (structural vulnerability)

### `shelter.csv` Columns:
- `id` - Shelter identifier
- `name` - Shelter name
- `lat`, `lon` - Geographic coordinates
- `capacity` - Refugee capacity

### Shapefiles (`village_boundary.*`):
- Geospatial data for village boundaries
- Used to visualize impact on map with districts colored by risk level

## How to Run

### 1. View the Live Application (Quickest)
The web application is deployed and accessible online. Visit the Streamlit Cloud link to use the simulator without any installation:
* **[Live Demo Link]** https://earthquake-simulation-6bqkbljwymwvwqvzsakbsv.streamlit.app/

### 2. Run Locally (For TA / Professor Evaluation)
If you are evaluating this project and need to run the application locally, please follow these steps:

**Step 1: Download the repository**
You can download the code using either of these two methods:
* **Option A (Git):** Clone the repository to your local machine using the terminal:
  `git clone https://github.com/hsunyin11-frog/earthquake-simulation.git`
  `cd earthquake-simulation`
* **Option B (Manual ZIP):** Click the green **Code** button at the top of this GitHub page and select **Download ZIP**. Extract the folder, open your terminal, and use the `cd` command to navigate inside the extracted folder.

**Step 2: Install dependencies**
Ensure you have Python 3.8+ installed. Install all required packages by running:
`pip install -r requirements.txt`

**Step 3: Run the application**
Start the Streamlit server from your terminal:
`streamlit run app.py`
*(If the main file is inside a folder, adjust the path, e.g., `streamlit run main/app.py`)*

The application will automatically open in your default web browser at `http://localhost:8501`.

---

*Final Project - Team 3 | 2026*
