import os
import requests
import geopandas as gpd

ZONING_URL = "https://data.brisbane.qld.gov.au/dataset/cp14-zoning-overlay/download/geojson"
GEOJSON_PATH = "zoning_data.geojson"

def load_zoning_data():
    # Check if file exists
    if not os.path.exists(GEOJSON_PATH):
        print("Downloading zoning data...")
        response = requests.get(ZONING_URL, stream=True)
        if response.status_code == 200:
            with open(GEOJSON_PATH, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print("Download complete.")
        else:
            raise Exception("Failed to download zoning data.")

    # Load the downloaded GeoJSON
    gdf = gpd.read_file(GEOJSON_PATH)
    gdf = gdf.to_crs("EPSG:4326")  # Convert CRS
    gdf = gdf[gdf.is_valid]  # Remove invalid geometries
    return gdf
