import pandas as pd
import folium
from sklearn.cluster import KMeans

print("script started")
# Sample data - replace with your own CSV if needed
data = pd.DataFrame({
    'latitude': [21.2002, 21.1710, 21.1805, 21.1750, 21.1680, 21.1695, 22.1415],
    'longitude': [72.8595, 72.8320, 72.8403, 72.8350, 72.8300, 72.8335, 72.8345]
})

# KMeans Clustering
X = data[['latitude', 'longitude']]
kmeans = KMeans(n_clusters=3, random_state=0)
kmeans.fit(X)
data['cluster'] = kmeans.labels_.astype(int)
centers = kmeans.cluster_centers_

# Create folium map
map_center = [data['latitude'].mean(), data['longitude'].mean()]
crime_map = folium.Map(location=map_center, zoom_start=13)
colors = ['red', 'green', 'blue']

# Add data points and clusters
for i, row in data.iterrows():
    folium.CircleMarker(
        location=(row['latitude'], row['longitude']),
        radius=6,
        color=colors[int(row['cluster'])],
        fill=True,
        fill_color=colors[int(row['cluster'])],
        fill_opacity=0.7,
        popup=f"Crime Point - Cluster {int(row['cluster']) + 1}"
    ).add_to(crime_map)

# Add cluster centers
for i, center in enumerate(centers):
    folium.Marker(
        location=(center[0], center[1]),
        icon=folium.Icon(color='black', icon='info-sign'),
        popup=f"Hotspot Center {i+1}"
    ).add_to(crime_map)

# Save map
output_path = "crime_hotspots_map.html"
crime_map.save(output_path)
print(f"Map saved to: {output_path}")
print("script end")
