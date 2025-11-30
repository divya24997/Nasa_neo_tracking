import requests
from datetime import datetime

API_Key = 'mXGH1grlBTLYagdqbShqUPYfHt7xzpwwyIpAKLcT'
url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date=2024-01-01&end_date=2024-01-07&api_key={API_Key}"

asteroids_data = []

target = 10000

while len(asteroids_data) < target:

      response = requests.get(url)
      data = response.json()
      details = data['near_earth_objects']

      for date, asteroids in details.items():

         for asteroid in asteroids:

              # Safely get close_approach_data list
              cad_list = asteroid.get('close_approach_data', [])
              cad = cad_list[0] if cad_list else {}

              asteroids_data.append(
                dict(
                    id = int(asteroid.get('id', 0)),
                    neo_reference_id = int(asteroid.get('neo_reference_id', 0)),
                    name = asteroid.get('name', 'Unknown'),
                    absolute_magnitude_h = asteroid.get('absolute_magnitude_h', 0.0),
                    estimated_diameter_min_km = asteroid.get('estimated_diameter', {}) \
                                                     .get('kilometers', {}) \
                                                     .get('estimated_diameter_min', 0.0),
                    estimated_diameter_max_km = asteroid.get('estimated_diameter', {}) \
                                                     .get('kilometers', {}) \
                                                     .get('estimated_diameter_max', 0.0),
                    is_potentially_hazardous_asteroid = asteroid.get('is_potentially_hazardous_asteroid', False),
                    close_approach_date = datetime.strptime(cad.get('close_approach_date', '1970-01-01'), "%Y-%m-%d").date(),
                    relative_velocity_kmph = float(cad.get('relative_velocity', {}).get('kilometers_per_hour', 0.0)),
                    astronomical = float(cad.get('miss_distance', {}).get('astronomical', 0.0)),
                    miss_distance_km = float(cad.get('miss_distance', {}).get('kilometers', 0.0)),
                    miss_distance_lunar = float(cad.get('miss_distance', {}).get('lunar', 0.0)),
                    orbiting_body = cad.get('orbiting_body', 'Unknown')
                )
            )

              if len(asteroids_data) >= target :
                          break

         if len(asteroids_data) >= target :
                        break
      url = data['links']['next']

asteroids_data
