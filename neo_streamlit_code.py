import streamlit as st
import pymysql
import pandas as pd
from datetime import date

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
@st.cache_resource
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Temp4now",
        database="nasa_neo_project"
    )

# ---------------------------
# SKY BLUE / WHITE BACKGROUND
# ---------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #b3d9ff, #e6f2ff);
    color: #003366;
}
h1, h2, h3 {
    color: #003366 !important;
}
.sidebar .sidebar-content {
    background-color: #cce6ff !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# PREDEFINED QUERIES
# ---------------------------
queries = {
    "Count of each asteroid has approached Earth":"""
        SELECT id,name,count(*) as count 
        FROM nasa_neo_project.asteroids 
        GROUP BY id,name;""",

    "Average velocity of each asteroid over multiple approaches":"""
        SELECT ast.id,ast.name,avg(ca.relative_velocity_kmph) as average_velocity 
        FROM nasa_neo_project.asteroids ast 
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id
        GROUP BY ast.id,ast.name;""",

    "Top 10 fastest asteroids":"""
        SELECT a.id,a.name,a.average_velocity 
        FROM (SELECT ast.id,ast.name,
        avg(ca.relative_velocity_kmph) as average_velocity 
        FROM nasa_neo_project.asteroids ast  
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id 
        GROUP BY ast.id,ast.name) a 
        ORDER BY average_velocity DESC LIMIT 10;""",

    "Potentially hazardous asteroids (>3 approaches)":"""
        SELECT id,name,is_potentially_hazardous_asteroid 
        FROM nasa_neo_project.asteroids 
        GROUP BY id,name,is_potentially_hazardous_asteroid 
        HAVING count(*) > 3 AND is_potentially_hazardous_asteroid = 1;""",

    "Month with most asteroid approaches":"""
        WITH max_cnt AS (
            SELECT MONTH(close_approach_date) AS mon, COUNT(*) AS cnt
            FROM nasa_neo_project.close_approach 
            GROUP BY MONTH(close_approach_date)
        )
        SELECT mon FROM max_cnt 
        WHERE cnt = (SELECT MAX(cnt) FROM max_cnt)""",

    "Asteroid with fastest approach":"""
        SELECT ast.id,ast.name,ca.relative_velocity_kmph 
        FROM nasa_neo_project.asteroids ast 
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id 
        WHERE ca.relative_velocity_kmph = (
            SELECT MAX(relative_velocity_kmph) 
            FROM nasa_neo_project.close_approach
        );""",

    "Sort by estimated max diameter":"""
        SELECT id,name,absolute_magnitude_h,estimated_diameter_min_km,
        estimated_diameter_max_km,is_potentially_hazardous_asteroid
        FROM nasa_neo_project.asteroids
        ORDER BY estimated_diameter_max_km DESC;""",

    "Asteroid getting nearer over time":"""
        WITH aster AS (
            SELECT DISTINCT id,name FROM nasa_neo_project.asteroids
        ),
        close_ap AS (
            SELECT a.neo_reference_id 
            FROM (
                SELECT neo_reference_id, close_approach_date, miss_distance_km,
                LAG(miss_distance_km) OVER (PARTITION BY neo_reference_id ORDER BY close_approach_date) AS prev,
                CASE 
                    WHEN miss_distance_km < LAG(miss_distance_km) OVER 
                    (PARTITION BY neo_reference_id ORDER BY close_approach_date)
                    THEN 1 ELSE 0 END AS is_dec
                FROM nasa_neo_project.close_approach
            ) a
            WHERE a.prev IS NOT NULL
            GROUP BY a.neo_reference_id
            HAVING SUM(is_dec)=COUNT(*)
        )
        SELECT at.id,at.name 
        FROM aster at 
        JOIN close_ap ca ON at.id=ca.neo_reference_id;""",

    "Asteroids & closest approach dates":"""
        SELECT DISTINCT at.id,at.name,ca.close_approach_date,ca.miss_distance_km 
        FROM nasa_neo_project.asteroids at 
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id;""",

    "Asteroids > 50,000 km/h":"""
        SELECT DISTINCT at.id,at.name,ca.relative_velocity_kmph 
        FROM nasa_neo_project.asteroids at 
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE ca.relative_velocity_kmph > 50000;""",

    "Approaches per month":"""
        SELECT MONTH(close_approach_date) AS mon, COUNT(*) AS cnt
        FROM nasa_neo_project.close_approach
        GROUP BY MONTH(close_approach_date);""",

    "Highest brightness asteroid":"""
        SELECT id,name,absolute_magnitude_h 
        FROM nasa_neo_project.asteroids 
        WHERE absolute_magnitude_h = 
        (SELECT MIN(absolute_magnitude_h) FROM nasa_neo_project.asteroids);""",

    "Hazardous asteroid count":"""
        SELECT COUNT(*) FROM nasa_neo_project.asteroids 
        WHERE is_potentially_hazardous_asteroid = 1;""",

    "Non-hazardous asteroid count":"""
        SELECT COUNT(*) FROM nasa_neo_project.asteroids 
        WHERE is_potentially_hazardous_asteroid = 0;""",

    "Asteroids <1 LD":"""
        SELECT DISTINCT at.id,at.name,ca.close_approach_date,ca.miss_distance_lunar 
        FROM nasa_neo_project.asteroids at
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE miss_distance_lunar < 1.0;""",

    "Asteroids <0.05 AU":"""
        SELECT DISTINCT at.id,at.name,ca.astronomical 
        FROM nasa_neo_project.asteroids at
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE ca.astronomical < 0.05;""",

    "Most frequent asteroid":"""
        WITH ast AS (
            SELECT id,name,COUNT(*) AS cnt 
            FROM nasa_neo_project.asteroids a
            JOIN nasa_neo_project.close_approach ca 
            ON a.id = ca.neo_reference_id 
            GROUP BY id,name
        )
        SELECT id,name FROM ast 
        WHERE cnt = (SELECT MAX(cnt) FROM ast);"""
}

# --------------------------------------
# MULTI-SCREEN NAVIGATION
# --------------------------------------
screen = st.selectbox("Select Screen", ["Home", "Filter Console", "Query Console"])

# --------------------------------------
# HOME SCREEN
# --------------------------------------
if screen == "Home":
    # Centered title and content
    st.markdown("""
    <div style="text-align: center;">
        <h1>🌌 NASA Asteroid Explorer Dashboard</h1>
        <h2>Welcome!</h2>
        <p>Use the dropdown above to navigate between:</p>
        <p>🔹 <b>Filter Console</b> – Apply filters & view results</p>
        <p>🔹 <b>Query Console</b> – Run predefined SQL queries</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# FILTER CONSOLE
# ---------------------------
elif screen == "Filter Console":
    
    st.markdown("""
    <style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
    background-color: #001f4d !important;  /* Dark blue */
    color: white !important;
    }
    /* Sidebar headers, labels, text */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {
    color: white !important;
    }
    /* Sidebar sliders, number inputs, selectboxes text */
    [data-testid="stSidebar"] .st-bf {
    color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


    # Sidebar filters
    st.sidebar.header("Filter Options")

    start_date = st.sidebar.date_input("Start Date", value=date(2000,1,1))
    end_date = st.sidebar.date_input("End Date", value=date.today())

    au_limit = st.sidebar.slider("Max Astronomical Units (AU)", 0.0, 10.0, 5.0)
    ld_limit = st.sidebar.slider("Max Lunar Distance (LD)", 0.0, 500.0, 300.0)
    velocity_min = st.sidebar.slider("Min Velocity (km/h)", 0, 300000, 0)
    diameter_min = st.sidebar.number_input("Min Diameter (km)", 0.0, 50.0, 0.0)
    diameter_max = st.sidebar.number_input("Max Diameter (km)", diameter_min, 50.0, 50.0)

    hazard = st.sidebar.selectbox("Hazardous?", ["All", "Yes", "No"])

    # Build conditions
    conditions = [
        f"ca.close_approach_date BETWEEN '{start_date}' AND '{end_date}'",
        f"ca.astronomical <= {au_limit}",
        f"ca.miss_distance_lunar <= {ld_limit}",
        f"ca.relative_velocity_kmph >= {velocity_min}",
        f"ast.estimated_diameter_min_km >= {diameter_min}",
        f"ast.estimated_diameter_max_km <= {diameter_max}"
    ]

    if hazard == "Yes":
        conditions.append("ast.is_potentially_hazardous_asteroid = 1")
    elif hazard == "No":
        conditions.append("ast.is_potentially_hazardous_asteroid = 0")

    final_query = f"""
        SELECT 
            ast.id, ast.name, ast.is_potentially_hazardous_asteroid,
            ast.estimated_diameter_min_km, ast.estimated_diameter_max_km,
            ca.close_approach_date, ca.relative_velocity_kmph,
            ca.astronomical, ca.miss_distance_lunar
        FROM nasa_neo_project.asteroids ast
        JOIN nasa_neo_project.close_approach ca ON ca.neo_reference_id = ast.id
        WHERE {" AND ".join(conditions)}
        ORDER BY ca.close_approach_date DESC;
    """

    st.subheader("Generated SQL Query")
    st.code(final_query, language="sql")

    # Execute
    conn = get_connection()
    df = pd.read_sql(final_query, conn)
    st.subheader("Filtered Results")
    st.dataframe(df)


# --------------------------------------
# QUERY CONSOLE
# --------------------------------------
elif screen == "Query Console":

    st.title("💻 SQL Query Console")

    query_name = st.selectbox("Select a Query", list(queries.keys()))
    st.subheader("SQL Query")
    st.code(queries[query_name], language="sql")

    conn = get_connection()
    df2 = pd.read_sql(queries[query_name], conn)

    st.subheader("Query Output")
    st.dataframe(df2)
