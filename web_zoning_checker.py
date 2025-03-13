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

if __name__ == "__main__":
    st.title("Brisbane Property Zoning Checker")

    try:
        st.info("Initializing zoning checker...")  # Add debug message
        zoning_gdf = load_zoning_data()
        
        if zoning_gdf is None:
            st.error("Could not load zoning data.")
        else:
            st.success("Zoning data loaded successfully.")

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
        st.error(f"An error occurred: {e}")
