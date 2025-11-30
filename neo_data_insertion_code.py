import pymysql

conn = pymysql.connect(
    host = "localhost",
    user = "root",
    password = "Temp4now",
    database = "nasa_neo_project"
)
cursor = conn.cursor()

# Create table asteroids
cursor.execute("""
CREATE TABLE IF NOT EXISTS asteroids (
    id INT,
    name VARCHAR(255),
    absolute_magnitude_h float,
    estimated_diameter_min_km float,
    estimated_diameter_max_km float,
    is_potentially_hazardous_asteroid bool
)
""")

# Insert data into table asteroids
sql_query_ast = """
INSERT INTO asteroids (
    id,
    name,
    absolute_magnitude_h,
    estimated_diameter_min_km,
    estimated_diameter_max_km,
    is_potentially_hazardous_asteroid
) VALUES (%s, %s, %s, %s, %s, %s)
"""

for asteroid in asteroids_data:
    values = (
        asteroid["id"],
        asteroid["name"],
        asteroid["absolute_magnitude_h"],
        asteroid["estimated_diameter_min_km"],
        asteroid["estimated_diameter_max_km"],
        asteroid["is_potentially_hazardous_asteroid"]
    )
    
    cursor.execute(sql_query_ast, values)
    
    
# Create table close_approach
cursor.execute("""
CREATE TABLE IF NOT EXISTS close_approach (
    neo_reference_id INT,
    close_approach_date date,
    relative_velocity_kmph float,
    astronomical float,
    miss_distance_km float,
    miss_distance_lunar float,
    orbiting_body VARCHAR(255)
)
""")

# Insert data into table close_approach
sql_query_ca = """
INSERT INTO close_approach (
    neo_reference_id,
    close_approach_date,
    relative_velocity_kmph,
    astronomical,
    miss_distance_km,
    miss_distance_lunar,
    orbiting_body
) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for asteroid in asteroids_data:
    values = (
        asteroid["neo_reference_id"],
        asteroid["close_approach_date"],
        asteroid["relative_velocity_kmph"],
        asteroid["astronomical"],
        asteroid["miss_distance_km"],
        asteroid["miss_distance_lunar"],
        asteroid["orbiting_body"]
    )
    
    cursor.execute(sql_query_ca, values)


conn.commit()

cursor.close()
conn.close()