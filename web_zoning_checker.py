import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import requests
import json
from fpdf import FPDF

def download_geojson(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'w') as file:
            json.dump(response.json(), file)
        return save_path
    else:
        st.error("Failed to download zoning data.")
        return None

def load_zoning_data(geojson_path):
    gdf = gpd.read_file(geojson_path)
    gdf = gdf.to_crs("EPSG:4326")  # Convert dataset to standard lat/lon CRS
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

def generate_pdf_report(lon, lat, zoning_info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Brisbane Property Zoning Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.cell(200, 10, f"Longitude: {lon}", ln=True)
    pdf.cell(200, 10, f"Latitude: {lat}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, "Zoning Information:", ln=True)
    pdf.ln(5)
    
    for col in zoning_info.columns:
        pdf.cell(200, 10, f"{col}: {zoning_info.iloc[0][col]}", ln=True)
    
    pdf_file = "zoning_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

def main():
    st.title("Brisbane Property Zoning Checker")
    
    zoning_url = "https://data.brisbane.qld.gov.au/dataset/cp14-zoning-overlay/download/geojson"
    geojson_path = "zoning_data.geojson"
    
    if st.button("Download Latest Zoning Data"):
        download_geojson(zoning_url, geojson_path)
        st.success("Zoning data downloaded successfully.")
    
    zoning_gdf = load_zoning_data(geojson_path)
    
    lon = st.number_input("Enter Longitude:", value=153.0251, format="%.6f")
    lat = st.number_input("Enter Latitude:", value=-27.4698, format="%.6f")
    
    if st.button("Check Zoning"):
        property_zone = find_property_zone(lon, lat, zoning_gdf)
        st.write("### Zoning Information:")
        st.write(property_zone)
        
        visualize_zoning(zoning_gdf, lon, lat)
        
        pdf_file = generate_pdf_report(lon, lat, property_zone)
        st.download_button(label="Download Zoning Report", data=open(pdf_file, "rb"), file_name="zoning_report.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
