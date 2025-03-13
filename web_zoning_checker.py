import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import requests
import os
from geopy.geocoders import Nominatim

# Define constants
ZONING_URL = "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Zoning_opendata/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
GEOJSON_PATH = "zoning_data.geojson"

def geocode_address(address):
    """Convert an address to latitude and longitude."""
    geolocator = Nominatim(user_agent="zoning_checker")
    location = geolocator.geocode(address)
    if location:
        return location.longitude, location.latitude
    else:
        return None, None

def load_zoning_data():
    """Download and load zoning data from the new ArcGIS source."""
    st.info("Checking zoning data...")

    if not os.path.exists(GEOJSON_PATH):
        st.warning("Downloading zoning data... (This may take a few minutes)")
        try:
            response = requests.get(ZONING_URL, stream=True, timeout=60)  # Increased timeout
            if response.status_code == 200:
                with open(GEOJSON_PATH, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                st.success("Zoning data downloaded successfully.")
            else:
                st.error(f"Failed to download zoning data. HTTP Status: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
            return None

    st.info("Loading zoning data...")

    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        gdf = gdf.to_crs("EPSG:4326")  # Convert CRS
        gdf = gdf[gdf.is_valid]  # Ensure valid geometries
        st.success("Zoning data loaded successfully.")
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {e}")
        return None

def find_property_zone(lon, lat, zoning_gdf):
    """Find the zoning information for a given longitude and latitude."""
    property_location = Point(lon, lat)
    property_series = gpd.GeoSeries([property_location], crs="EPSG:4326")
    property_zone = gpd.sjoin(property_series.to_frame(name='geometry'), zoning_gdf, how='left', predicate='intersects')
    return property_zone

def visualize_zoning(zoning_gdf, lon, lat):
    """Plot the property location on the zoning overlay."""
    fig, ax = plt.subplots(figsize=(10, 10))
    zoning_gdf.plot(ax=ax, edgecolor='black', alpha=0.5)
    ax.scatter(lon, lat, color='red', s=100, label='Property Location')
    ax.legend()
    plt.title("Property Zoning Overlay")
    st.pyplot(fig)

if __name__ == "__main__":
    st.title("Brisbane Property Zoning Checker")

    try:
        st.info("Initializing zoning checker... (This should be visible)")
        zoning_gdf = load_zoning_data()

        if zoning_gdf is None:
            st.error("Could not load zoning data. Try again later.")
            st.stop()  # Stops execution but prevents the app from crashing
        else:
            st.success("Zoning data loaded successfully.")

            address = st.text_input("Enter Address (or leave blank to use coordinates):")
            lon, lat = None, None
            
            if address:
                st.info("Geocoding address...")
                lon, lat = geocode_address(address)
                if lon is None or lat is None:
                    st.error("Could not find coordinates for the given address.")
                    st.stop()
            else:
                lon = st.number_input("Enter Longitude:", value=153.0251, format="%.6f")
                lat = st.number_input("Enter Latitude:", value=-27.4698, format="%.6f")

            if st.button("Check Zoning"):
                st.info("Checking zoning data...")
                property_zone = find_property_zone(lon, lat, zoning_gdf)

                if property_zone is not None and not property_zone.empty:
                    st.write("### Zoning Information:")
                    st.write(property_zone)
                    visualize_zoning(zoning_gdf, lon, lat)
                else:
                    st.warning("No zoning data found for this location.")

    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()  # Ensures the app stops cleanly without crashing