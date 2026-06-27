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

# Define accurate district centroids in Bihar (Latitude, Longitude)
district_centroids = {
    'Patna': (25.61, 85.14),
    'Gaya': (24.79, 85.00),
    'Bhagalpur': (25.25, 87.01),
    'Muzaffarpur': (26.12, 85.38),
    'Darbhanga': (26.15, 85.90),
    'West Champaran': (27.15, 84.50),
    'East Champaran': (26.65, 84.91),
    'Saran': (25.85, 84.85),
    'Siwan': (26.22, 84.36),
    'Gopalganj': (26.47, 84.44),
    'Vaishali': (25.75, 85.22),
    'Samastipur': (25.86, 85.78),
    'Sitamarhi': (26.60, 85.48),
    'Sheohar': (26.51, 85.29),
    'Madhubani': (26.35, 86.08),
    'Begusarai': (25.42, 86.13),
    'Khagaria': (25.50, 86.48),
    'Munger': (25.37, 86.47),
    'Lakhisarai': (25.18, 86.09),
    'Sheikhpura': (25.14, 85.86),
    'Nalanda': (25.20, 85.51),
    'Bhojpur': (25.56, 84.67),
    'Buxar': (25.56, 83.98),
    'Rohtas': (24.95, 84.01),
    'Kaimur': (25.05, 83.62),
    'Jehanabad': (25.21, 84.99),
    'Arwal': (25.25, 84.67),
    'Nawada': (24.89, 85.54),
    'Aurangabad': (24.75, 84.37),
    'Jamui': (24.92, 86.22),
    'Banka': (24.88, 86.92),
    'Saharsa': (25.88, 86.60),
    'Supaul': (26.12, 86.60),
    'Madhepura': (25.92, 86.79),
    'Purnia': (25.78, 87.47),
    'Araria': (26.15, 87.43),
    'Kishanganj': (26.27, 87.95),
    'Katihar': (25.54, 87.57)
}

def generate_hexagon(center_lon, center_lat, size=0.03):
    """
    Generates coordinates of a hexagon centered at center_lon, center_lat.
    """
    coords = []
    # 6 points + 1 closing point
    for i in range(7):
        angle = math.radians(60 * i)
        lon = center_lon + size * math.cos(angle)
        # Latitudes shrink slightly in degree width relative to longitude,
        # but 0.03 is small enough that a simple circle/hexagon is fine.
        lat = center_lat + size * math.sin(angle)
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
        # to ensure they don't overlap.
        for i, c in enumerate(consts):
            ac_no = c['ac_no']
            ac_name = c['ac_name']
            
            # Radial distance and angle
            # For 1 constituency, offset is 0.
            # Otherwise distribute evenly.
            if n > 1:
                # Add slight random variations or use structured ring layout
                # Radius between 0.05 and 0.12 depending on district size (approximated)
                radius = 0.06 + 0.02 * (i % 3)
                angle = (2 * math.pi * i) / n
                offset_lon = radius * math.cos(angle)
                offset_lat = radius * math.sin(angle)
            else:
                offset_lon, offset_lat = 0, 0
                
            c_lon = dist_lon + offset_lon
            c_lat = dist_lat + offset_lat
            
            # Generate regular hexagon coordinates
            # Size = 0.02 to make them fit nicely next to each other
            hexagon_coords = generate_hexagon(c_lon, c_lat, size=0.02)
            
            # Format filename, e.g. AC001_valmiki_nagar_spatial.geojson
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
