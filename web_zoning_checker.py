import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import requests
import os

# Define constants
ZONING_URL = "https://data.brisbane.qld.gov.au/dataset/cp14-zoning-overlay/download/geojson"
GEOJSON_PATH = "zoning_data.geojson"

def load_zoning_data():
    """Download and load a subset of zoning data to improve performance."""
    st.info("Checking zoning data...")

    if not os.path.exists(GEOJSON_PATH):
        st.warning("Downloading zoning data... (May take a few minutes)")
        try:
            response = requests.get(ZONING_URL, stream=True, timeout=30)  # Set timeout to prevent freezing
            if response.status_code == 200:
                with open(GEOJSON_PATH, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                st.success("Zoning data downloaded successfully.")
            else:
                st.error("Failed to download zoning data.")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
            return None

    st.info("Loading zoning data...")

    try:
        gdf = gpd.read_file(GEOJSON_PATH, rows=1000)  # Load first 1000 rows for performance
        gdf = gdf.to_crs("EPSG:4326")
        gdf = gdf[gdf.is_valid]
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {e}")
        return None

    st.info("Loading zoning data...")
    gdf = gpd.read_file(GEOJSON_PATH, rows=1000)  # Load only 1000 rows to reduce memory usage
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf[gdf.is_valid]  # Remove invalid geometries
