ZONING_URL = "https://services2.arcgis.com/dEKgZETqwmDAh1rP/arcgis/rest/services/Zoning_opendata/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
GEOJSON_PATH = "zoning_data.geojson"

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
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON file: {e}")
        return None
