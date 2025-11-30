1.Count how many times each asteroid has approached Earth
        SELECT id,name,count(*) as count 
        FROM nasa_neo_project.asteroids 
        GROUP BY id,name;

2.Average velocity of each asteroid over multiple approaches
        SELECT ast.id,ast.name,avg(ca.relative_velocity_kmph) as average_velocity 
        FROM nasa_neo_project.asteroids ast 
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id
        GROUP BY ast.id,ast.name;

3.List top 10 fastest asteroids
        SELECT a.id,a.name,a.average_velocity 
        FROM (SELECT ast.id,ast.name,
        avg(ca.relative_velocity_kmph) as average_velocity 
        FROM nasa_neo_project.asteroids ast  
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id 
        GROUP BY ast.id,ast.name) a 
        ORDER BY average_velocity DESC LIMIT 10;

4.Find potentially hazardous asteroids that have approached Earth more than 3 times
        SELECT id,name,is_potentially_hazardous_asteroid 
        FROM nasa_neo_project.asteroids 
        GROUP BY id,name,is_potentially_hazardous_asteroid 
        HAVING count(*) > 3 AND is_potentially_hazardous_asteroid = 1;

5.Find the month with the most asteroid approaches
        WITH max_cnt AS (
            SELECT MONTH(close_approach_date) AS mon, COUNT(*) AS cnt
            FROM nasa_neo_project.close_approach 
            GROUP BY MONTH(close_approach_date)
        )
        SELECT mon FROM max_cnt 
        WHERE cnt = (SELECT MAX(cnt) FROM max_cnt);

6.Get the asteroid with the fastest ever approach speed
        SELECT ast.id,ast.name,ca.relative_velocity_kmph 
        FROM nasa_neo_project.asteroids ast 
        JOIN nasa_neo_project.close_approach ca 
        ON ast.id = ca.neo_reference_id 
        WHERE ca.relative_velocity_kmph = (
            SELECT MAX(relative_velocity_kmph) 
            FROM nasa_neo_project.close_approach
        );

7.Sort asteroids by maximum estimated diameter (descending)
        SELECT id,name,absolute_magnitude_h,estimated_diameter_min_km,
        estimated_diameter_max_km,is_potentially_hazardous_asteroid
        FROM nasa_neo_project.asteroids
        ORDER BY estimated_diameter_max_km DESC;

8.An asteroid whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)
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
        JOIN close_ap ca ON at.id=ca.neo_reference_id;

9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.
        SELECT DISTINCT at.id,at.name,ca.close_approach_date,ca.miss_distance_km 
        FROM nasa_neo_project.asteroids at 
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id;

10.List names of asteroids that approached Earth with velocity > 50,000 km/h
        SELECT DISTINCT at.id,at.name,ca.relative_velocity_kmph 
        FROM nasa_neo_project.asteroids at 
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE ca.relative_velocity_kmph > 50000;

11.Count how many approaches happened per month
        SELECT MONTH(close_approach_date) AS mon, COUNT(*) AS cnt
        FROM nasa_neo_project.close_approach
        GROUP BY MONTH(close_approach_date);

 12.Find asteroid with the highest brightness (lowest magnitude value)
        SELECT id,name,absolute_magnitude_h 
        FROM nasa_neo_project.asteroids 
        WHERE absolute_magnitude_h = 
        (SELECT MIN(absolute_magnitude_h) FROM nasa_neo_project.asteroids);

13.Get number of hazardous vs non-hazardous asteroids
        SELECT COUNT(*) FROM nasa_neo_project.asteroids 
        WHERE is_potentially_hazardous_asteroid = 1;
        SELECT COUNT(*) FROM nasa_neo_project.asteroids 
        WHERE is_potentially_hazardous_asteroid = 0;

14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.
        SELECT DISTINCT at.id,at.name,ca.close_approach_date,ca.miss_distance_lunar 
        FROM nasa_neo_project.asteroids at
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE miss_distance_lunar < 1.0;

15.Find asteroids that came within 0.05 AU(astronomical distance)
        SELECT DISTINCT at.id,at.name,ca.astronomical 
        FROM nasa_neo_project.asteroids at
        JOIN nasa_neo_project.close_approach ca 
        ON at.id = ca.neo_reference_id 
        WHERE ca.astronomical < 0.05;

16.Most frequent asteroid
        WITH ast AS (
            SELECT id,name,COUNT(*) AS cnt 
            FROM nasa_neo_project.asteroids a
            JOIN nasa_neo_project.close_approach ca 
            ON a.id = ca.neo_reference_id 
            GROUP BY id,name
        )
        SELECT id,name FROM ast 
        WHERE cnt = (SELECT MAX(cnt) FROM ast);

17.Which asteroid appeared Earth the most
		WITH ast as (
		SELECT at.id,at.name,count(*) as cnt FROM 
		(SELECT DISTINCT id,name FROM nasa_neo_project.asteroids)at 
		JOIN nasa_neo_project.close_approach ca on at.id = ca.neo_reference_id GROUP BY id,name)
		SELECT a.id,a.name FROM ast a WHERE cnt = (SELECT max(cnt) FROM ast);
		
18.Find the earliest and latest approach dates for each asteroid
		SELECT at.name,at.id,max(ca.close_approach_date) as max_dt,min(ca.close_approach_date) as min_dt FROM 
		(SELECT DISTINCT id,name FROM nasa_neo_project.asteroids)at 
		JOIN nasa_neo_project.close_approach ca on at.id = ca.neo_reference_id GROUP BY id,name;
		
19.Find asteroids that have come within 1 lunar distance more than once.
        SELECT at.name,at.id FROM 
		(SELECT distinct id,name FROM nasa_neo_project.asteroids)at 
		JOIN nasa_neo_project.close_approach ca on at.id = ca.neo_reference_id 
		WHERE miss_distance_lunar < 1.0 GROUP BY id,name
		HAVING count(*) >1;
		
20.Find the latest close approach date for each month
		SELECT mon,max(close_approach_date) as max_dt FROM
		(SELECT neo_reference_id,close_approach_date,month(close_approach_date) as mon 
		FROM nasa_neo_project.close_approach)a GROUP BY mon;
		