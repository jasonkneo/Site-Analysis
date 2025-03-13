import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import requests
import os
from geopy.geocoders import Nominatim

# Define constants
ZONING_URL = "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Zoning_opendata/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
OVERLAY_URLS = {
    "Character": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Character_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Flood": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Flood_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Overland Flow": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Overland_Flow_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Traditional Building Character": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/TBC_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Bushfire": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Bushfire_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Heritage": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Heritage_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Pre-1911 Buildings": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Pre1911_Overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Transport Noise Corridors": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Transport_Noise_Corridors/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
}
GEOJSON_PATH = "zoning_data.geojson"
OVERLAY_PATHS = {key: f"{key.lower().replace(' ', '_')}_overlay.geojson" for key in OVERLAY_URLS.keys()}

# Limit overlays to load initially to prevent overload
OVERLAYS_TO_LOAD = ["Character", "Flood", "Overland Flow"]

def geocode_address(address):
    """Convert an address to latitude and longitude."""
    geolocator = Nominatim(user_agent="zoning_checker")
    location = geolocator.geocode(address)
    if location:
        return location.longitude, location.latitude
    else:
        return None, None

def download_geojson(url, path):
    """Download a geojson file if it does not exist."""
    if not os.path.exists(path):
        try:
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                with open(path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return path
        except requests.exceptions.RequestException:
            return None
    return path

def load_zoning_data():
    """Download and load zoning data."""
    st.info("Downloading zoning data... (Please wait)")
    zoning_path = download_geojson(ZONING_URL, GEOJSON_PATH)
    
    if zoning_path:
        try:
            st.info("Loading zoning data into memory...")
            gdf = gpd.read_file(zoning_path)
            gdf = gdf.to_crs("EPSG:4326")
            gdf = gdf[gdf.is_valid]
            st.success("Zoning data loaded successfully!")
            return gdf
        except Exception as e:
            st.error(f"Error loading zoning data: {e}")
            return None
    else:
        st.error("Zoning data download failed.")
        return None

def load_overlay_data():
    """Download and load a limited number of overlay data."""
    overlay_gdfs = {}
    
    for overlay in OVERLAYS_TO_LOAD:
        if overlay in OVERLAY_URLS:
            st.info(f"Downloading {overlay} overlay data... (Please wait)")
            path = download_geojson(OVERLAY_URLS[overlay], OVERLAY_PATHS[overlay])
            
            if path:
                try:
                    st.info(f"Loading {overlay} overlay data...")
                    overlay_gdfs[overlay] = gpd.read_file(path)
                    overlay_gdfs[overlay] = overlay_gdfs[overlay].to_crs("EPSG:4326")
                    st.success(f"{overlay} overlay loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading {overlay} overlay: {e}")
            else:
                st.warning(f"Could not download {overlay} overlay.")
    return overlay_gdfs

# Rest of the existing code remains the same