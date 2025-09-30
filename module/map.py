# import folium
# from folium.plugins import MarkerCluster, HeatMap, Geocoder
# import pandas as pd

# # -------------------------
# # Example "Live" Data (replace with API/DB fetch)
# # -------------------------
# projects = [
#     {"project": "Mangrove Restoration - Gujarat", "lat": 21.6417, "lon": 72.2097, "carbon_tons": 1200, "year": 2021, "status": "Verified"},
#       {"project": "Seagrass Plantation - Tamil Nadu", "lat": 10.78, "lon": 79.13, "carbon_tons": 850, "year": 2022, "status": "Pending"},
#     {"project": "Saltmarsh Revival - Sundarbans", "lat": 22.0, "lon": 88.0, "carbon_tons": 2500, "year": 2019, "status": "Verified"},
#     {"project": "Community Plantation - Kerala", "lat": 9.9312, "lon": 76.2673, "carbon_tons": 600, "year": 2023, "status": "Ongoing"},
#     {"project": "Mangrove Belt - Maharashtra", "lat": 18.97, "lon": 72.82, "carbon_tons": 1500, "year": 2020, "status": "Verified"},
#     {"project": "Community Plantation - Aurangabad Satara Parisar", "lat": 19.8773, "lon": 75.3391, "carbon_tons": 900, "year": 2023, "status": "Ongoing"},
  
# ]

# df = pd.DataFrame(projects)

# # -------------------------
# # Base Map (Satellite)
# # -------------------------
# m = folium.Map(
#     location=[20.5937, 78.9629],
#     zoom_start=5,
#     tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
#     attr="Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
# )

# # -------------------------
# # Clustered Markers
# # -------------------------
# marker_cluster = MarkerCluster(name="Registry Projects").add_to(m)

# for _, row in df.iterrows():
#     popup_html = f"""
#     <div style="font-size:14px;">
#         <b>{row['project']}</b><br>
#         <b>Carbon Stored:</b> {row['carbon_tons']} tons<br>
#         <b>Year:</b> {row['year']}<br>
#         <b>Status:</b> {row['status']}<br>
#     </div>
#     """
#     folium.CircleMarker(
#         location=[row["lat"], row["lon"]],
#         radius=7 + (row["carbon_tons"]/1000),  # bubble size depends on carbon
#         popup=folium.Popup(popup_html, max_width=300),
#         color="darkgreen" if row["status"] == "Verified" else "orange",
#         fill=True,
#         fill_color="blue",
#         fill_opacity=0.7
#     ).add_to(marker_cluster)

# # -------------------------
# # Heatmap Layer
# # -------------------------
# heat_data = [[row["lat"], row["lon"], row["carbon_tons"]] for _, row in df.iterrows()]
# HeatMap(
#     heat_data,
#     name="Carbon Storage Heatmap",
#     radius=30,
#     blur=15,
#     max_zoom=10
# ).add_to(m)

# # -------------------------
# # Extra Map Layers
# # -------------------------
# folium.TileLayer("CartoDB positron", name="Light Mode").add_to(m)
# folium.TileLayer("CartoDB dark_matter", name="Dark Mode").add_to(m)

# # -------------------------
# # Add Search/Geocoder
# # -------------------------
# Geocoder(collapsed=False, add_marker=True).add_to(m)

# # -------------------------
# # Layer Control
# # -------------------------
# folium.LayerControl().add_to(m)

# # -------------------------
# # Save Map
# # -------------------------
# m.save("templates/blue_carbon_registry_satellite_map.html")
# print("✅ Satellite map created: open blue_carbon_registry_satellite_map.html")
