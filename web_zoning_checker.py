import streamlit as st
import geopandas as gpd
import requests
import os

ZONING_URL = "https://data.brisbane.qld.gov.au/dataset/cp14-zoning-overlay/download/geojson"
GEOJSON_PATH = "zoning_data.geojson"

def load_zoning_data():
    """Download and load zoning data with a size limit."""
    if not os.path.exists(GEOJSON_PATH):
        st.info("Downloading zoning data (this may take time)...")
        response = requests.get(ZONING_URL, stream=True)
        if response.status_code == 200:
            with open(GEOJSON_PATH, 'wb') as file:
                for chunk in response.iter_content(chunk_size=4096):  # Increased chunk size
                    file.write(chunk)
            st.success("Zoning data downloaded successfully.")
        else:
            st.error("Failed to download zoning data. Try again later.")
            return None

    # Load and filter only relevant columns
    gdf = gpd.read_file(GEOJSON_PATH, rows=1000)  # Load first 1000 rows to reduce memory
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf[gdf.is_valid]  # Remove invalid geometries
    return gdf
