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
    "Character": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Dwelling_house_character_overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Flood": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Flood_Awareness_Flood_Risk_Overall/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Overland Flow": "OVERLAND_FLOW_OVERLAY_GEOJSON_URL",
    "Traditional Building Character": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Traditional_building_character_overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
    "Bushfire": "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Bushfire_overlay/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson",
}
GEOJSON_PATH = "zoning_data.geojson"
OVERLAY_PATHS = {key: f"{key.lower().replace(' ', '_')}_overlay.geojson" for key in OVERLAY_URLS.keys()}

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
    zoning_path = download_geojson(ZONING_URL, GEOJSON_PATH)
    if zoning_path:
        gdf = gpd.read_file(zoning_path)
        gdf = gdf.to_crs("EPSG:4326")
        gdf = gdf[gdf.is_valid]
        return gdf
    return None

def load_overlay_data():
    """Download and load all overlay data."""
    overlay_gdfs = {}
    for overlay, url in OVERLAY_URLS.items():
        path = download_geojson(url, OVERLAY_PATHS[overlay])
        if path:
            overlay_gdfs[overlay] = gpd.read_file(path)
            overlay_gdfs[overlay] = overlay_gdfs[overlay].to_crs("EPSG:4326")
    return overlay_gdfs

def find_property_info(lon, lat, zoning_gdf, overlay_gdfs):
    """Find zoning and overlay information for a property."""
    property_location = Point(lon, lat)
    property_series = gpd.GeoSeries([property_location], crs="EPSG:4326")
    property_zone = gpd.sjoin(property_series.to_frame(name='geometry'), zoning_gdf, how='left', predicate='intersects')
    overlays = {}
    for overlay, gdf in overlay_gdfs.items():
        overlay_match = gpd.sjoin(property_series.to_frame(name='geometry'), gdf, how='left', predicate='intersects')
        if not overlay_match.empty:
            overlays[overlay] = overlay_match.iloc[0].to_dict()
    return property_zone, overlays

def visualize_zoning(zoning_gdf, overlay_gdfs, lon, lat):
    """Plot the property location with zoning and overlays."""
    fig, ax = plt.subplots(figsize=(10, 10))
    zoning_gdf.plot(ax=ax, column="zone_type", cmap="viridis", legend=True, edgecolor="black", alpha=0.5)
    for overlay, gdf in overlay_gdfs.items():
        gdf.plot(ax=ax, edgecolor='red', alpha=0.3, label=overlay)
    ax.scatter(lon, lat, color='red', s=100, label='Property Location')
    plt.title("Property Zoning and Overlays")
    plt.legend()
    st.pyplot(fig)

if __name__ == "__main__":
    st.title("Brisbane Property Zoning & Overlays Checker")

    try:
        st.info("Initializing zoning and overlay checker...")
        zoning_gdf = load_zoning_data()
        overlay_gdfs = load_overlay_data()

        if zoning_gdf is None:
            st.error("Could not load zoning data. Try again later.")
            st.stop()

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

        if st.button("Check Zoning and Overlays"):
            st.info("Checking zoning and overlays...")
            property_zone, overlays = find_property_info(lon, lat, zoning_gdf, overlay_gdfs)

            if property_zone is not None and not property_zone.empty:
                st.write("### Zoning Information:")
                st.write(property_zone)
                
                st.write("### Overlay Information:")
                for overlay, data in overlays.items():
                    st.write(f"**{overlay} Overlay:**")
                    st.write(data)
                
                visualize_zoning(zoning_gdf, overlay_gdfs, lon, lat)
            else:
                st.warning("No zoning data found for this location.")
    
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.stop()