def load_zoning_data():
    """Download and load a subset of zoning data to improve performance."""
    if not os.path.exists(GEOJSON_PATH):
        st.info("Downloading zoning data (this may take a while)...")
        response = requests.get(ZONING_URL, stream=True)
        if response.status_code == 200:
            with open(GEOJSON_PATH, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):  # Increase chunk size for speed
                    file.write(chunk)
            st.success("Zoning data downloaded successfully.")
        else:
            st.error("Failed to download zoning data. Try again later.")
            return None

    st.info("Loading zoning data...")
    gdf = gpd.read_file(GEOJSON_PATH, rows=1000)  # Load only 1000 rows to reduce memory usage
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf[gdf.is_valid]  # Remove invalid geometries
    return gdf
