import os
import json
import math
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../ingestion/.env'))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase environment variables not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define district centroids shifted slightly inward from borders to avoid spillover
district_centroids = {
    'Patna': (25.61, 85.14),
    'Gaya': (24.85, 85.00),         # Shifted north from 24.79 (Jharkhand border)
    'Bhagalpur': (25.25, 87.01),
    'Muzaffarpur': (26.12, 85.38),
    'Darbhanga': (26.15, 85.90),
    'West Champaran': (26.85, 84.55), # Shifted south/east from 27.15 (Nepal/UP border)
    'East Champaran': (26.55, 84.93), # Shifted south/east from 26.65 (Nepal border)
    'Saran': (25.85, 84.90),         # Shifted east from 84.85 (UP border)
    'Siwan': (26.22, 84.44),         # Shifted east from 84.36 (UP border)
    'Gopalganj': (26.47, 84.50),     # Shifted east from 84.44 (UP border)
    'Vaishali': (25.75, 85.22),
    'Samastipur': (25.86, 85.78),
    'Sitamarhi': (26.50, 85.48),     # Shifted south from 26.60 (Nepal border)
    'Sheohar': (26.45, 85.29),       # Shifted south from 26.51 (Nepal border)
    'Madhubani': (26.25, 86.08),     # Shifted south from 26.35 (Nepal border)
    'Begusarai': (25.42, 86.13),
    'Khagaria': (25.50, 86.48),
    'Munger': (25.37, 86.47),
    'Lakhisarai': (25.18, 86.09),
    'Sheikhpura': (25.14, 85.86),
    'Nalanda': (25.20, 85.51),
    'Bhojpur': (25.56, 84.67),
    'Buxar': (25.56, 84.10),         # Shifted east from 83.98 (UP border)
    'Rohtas': (24.95, 84.15),         # Shifted east from 84.01 (UP/Jharkhand border)
    'Kaimur': (25.05, 83.75),         # Shifted east from 83.62 (UP border)
    'Jehanabad': (25.21, 84.99),
    'Arwal': (25.25, 84.67),
    'Nawada': (24.95, 85.54),         # Shifted north from 24.89 (Jharkhand border)
    'Aurangabad': (24.80, 84.45),     # Shifted north/east from 24.75 (Jharkhand border)
    'Jamui': (25.00, 86.22),         # Shifted north from 24.92 (Jharkhand border)
    'Banka': (24.95, 86.92),         # Shifted north from 24.88 (Jharkhand border)
    'Saharsa': (25.88, 86.60),
    'Supaul': (26.05, 86.60),         # Shifted south from 26.12 (Nepal border)
    'Madhepura': (25.92, 86.79),
    'Purnia': (25.78, 87.47),
    'Araria': (26.10, 87.43),         # Shifted south from 26.15 (Nepal border)
    'Kishanganj': (26.20, 87.90),     # Shifted south/west from 26.27 (Nepal/WB border)
    'Katihar': (25.54, 87.57)
}

# Approx safe boundaries for Bihar to prevent crossover
BIHAR_MIN_LAT = 24.3
BIHAR_MAX_LAT = 27.4
BIHAR_MIN_LON = 83.4
BIHAR_MAX_LON = 88.1

def generate_hexagon(center_lon, center_lat, size=0.012):
    """
    Generates coordinates of a hexagon centered at center_lon, center_lat.
    """
    coords = []
    # 6 points + 1 closing point
    for i in range(7):
        angle = math.radians(60 * i)
        lon = center_lon + size * math.cos(angle)
        lat = center_lat + size * math.sin(angle)
        
        # Validation checks
        if not (BIHAR_MIN_LAT <= lat <= BIHAR_MAX_LAT):
            raise ValueError(f"Latitude {lat:.4f} is outside safe Bihar bounds ({BIHAR_MIN_LAT} to {BIHAR_MAX_LAT})")
        if not (BIHAR_MIN_LON <= lon <= BIHAR_MAX_LON):
            raise ValueError(f"Longitude {lon:.4f} is outside safe Bihar bounds ({BIHAR_MIN_LON} to {BIHAR_MAX_LON})")
            
        coords.append([round(lon, 6), round(lat, 6)])
    return [coords]

def main():
    # Fetch constituencies from Supabase
    print("Fetching constituencies from Supabase...")
    res = supabase.table('constituencies').select('ac_no, ac_name, district').execute()
    constituencies = res.data
    
    if not constituencies:
        print("No constituencies found.")
        return
        
    print(f"Loaded {len(constituencies)} constituencies.")
    
    # Group constituencies by district
    by_district = {}
    for c in constituencies:
        dist = c['district']
        by_district.setdefault(dist, []).append(c)
        
    spatial_dir = os.path.join(os.path.dirname(__file__), '../data/raw/spatial')
    os.makedirs(spatial_dir, exist_ok=True)
    
    print("Generating corrected GeoJSON files...")
    generated_count = 0
    
    for dist, consts in by_district.items():
        if dist not in district_centroids:
            print(f"Warning: Centroid not defined for district '{dist}'. Using default Patna center.")
            dist_lat, dist_lon = district_centroids['Patna']
        else:
            dist_lat, dist_lon = district_centroids[dist]
            
        n = len(consts)
        
        # Distribute constituencies of the district in a circle around the centroid
        for i, c in enumerate(consts):
            ac_no = c['ac_no']
            ac_name = c['ac_name']
            
            # Using much tighter spread (radius 0.025 to 0.045) to prevent border crossover
            if n > 1:
                radius = 0.025 + 0.01 * (i % 3)
                angle = (2 * math.pi * i) / n
                offset_lon = radius * math.cos(angle)
                offset_lat = radius * math.sin(angle)
            else:
                offset_lon, offset_lat = 0, 0
                
            c_lon = dist_lon + offset_lon
            c_lat = dist_lat + offset_lat
            
            # Hexagon size shrunk to 0.012 to fit tightly and prevent overlap
            try:
                hexagon_coords = generate_hexagon(c_lon, c_lat, size=0.012)
            except ValueError as e:
                print(f"Error generating coordinates for AC{ac_no} {ac_name} in district {dist}: {e}")
                raise e
            
            # Format filename
            slug = ac_name.lower().replace(' ', '_').replace('-', '_').replace("'", "")
            filename = f"AC{ac_no:03d}_{slug}_spatial.geojson"
            filepath = os.path.join(spatial_dir, filename)
            
            geojson_data = {
                "type": "Feature",
                "properties": {
                    "ac_no": ac_no,
                    "ac_name": ac_name,
                    "district": dist,
                    "state": "Bihar",
                    "country": "India",
                    "area_sq_km": 250.0
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": hexagon_coords
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=4)
            generated_count += 1
            
    print(f"Successfully generated {generated_count} spatial GeoJSON files.")

if __name__ == "__main__":
    main()
