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
    # Check if file exists, if not download it
    if not os.path.exists(GEOJSON_PATH):
        st.info("Downloading zoning data...")
        response = requests.get(ZONING_URL, stream=True)
        if response.status_code == 200:
            with open(GEOJSON_PATH, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            st.success("Zoning data downloaded successfully.")
        else:
            st.error("Failed to download zoning data.")
            return None
    
    # Load the GeoJSON data
    gdf = gpd.read_file(GEOJSON_PATH)
    gdf = gdf.to_crs("EPSG:4326")  # Convert CRS
    gdf = gdf[gdf.is_valid]  # Remove invalid geometries
    return gdf

def find_property_zone(lon, lat, zoning_gdf):
    property_location = Point(lon, lat)
    property_series = gpd.GeoSeries([property_location], crs="EPSG:4326")
    property_zone = gpd.sjoin(property_series.to_frame(name='geometry'), zoning_gdf, how='left', predicate='intersects')
    return property_zone

def visualize_zoning(zoning_gdf, lon, lat):
    fig, ax = plt.subplots(figsize=(10, 10))
    zoning_gdf.plot(ax=ax, edgecolor='black', alpha=0.5)
    ax.scatter(lon, lat, color='red', s=100, label='Property Location')
    ax.legend()
    plt.title("Property Zoning Overlay")
    st.pyplot(fig)

if __name__ == "__main__":
    st.title("Brisbane Property Zoning Checker")

    try:
        zoning_gdf = load_zoning_data()
        if zoning_gdf is None:
            st.error("Could not load zoning data.")
        else:
            lon = st.number_input("Enter Longitude:", value=153.0251, format="%.6f")
            lat = st.number_input("Enter Latitude:", value=-27.4698, format="%.6f")

            if st.button("Check Zoning"):
                property_zone = find_property_zone(lon, lat, zoning_gdf)
                if property_zone is not None and not property_zone.empty:
                    st.write("### Zoning Information:")
                    st.write(property_zone)
                    visualize_zoning(zoning_gdf, lon, lat)
                else:
                    st.warning("No zoning data found for this location.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
