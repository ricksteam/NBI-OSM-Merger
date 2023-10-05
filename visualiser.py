import overpass
import geopandas as gpd
import matplotlib.pyplot as plt
from util import CoordinateCalculator

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')

# class Visualizer:
#     def __init__(self):
ovp = overpass.API(endpoint=f"{OVP_ENDPOINT}/interpreter")
origin = (41.3209, -96.0449)
# origin = (41.3236, -96.0449)
# origin = (41.3154, -96.0524)
# origin = (41.3293, -96.0482)
# origin = (41.311 , -96.0475)


pt_lat = origin[0]
pt_lon = origin[1]

# Bounding box size in km
side_length = 0.25
tl, br = CoordinateCalculator.get_bounding_box((pt_lat, pt_lon), side_length)

# Relations break our queries for some reason and are not needed. Just use nodes and ways.
query = f"nw({br[0]}, {tl[1]}, {tl[0]}, {br[1]}); out;"

# Query the data and put it into a GeoDataFrame
response = ovp.get(query, verbosity="geom")
gdf = gpd.GeoDataFrame(response.features)
# set the coordinate relation system
gdf.set_crs("EPSG:4326")

# print(gdf.tail(10))

# create the initial map
ax = gdf.plot(markersize=0)

# Iterate through the returned rows
series_itr = gdf.iterrows()
for row in series_itr:
    # rows are in (id, Series) format
    series = row[1]
    # If the Series has a bridge tag, highlight it
    if series.properties.get("bridge") == "yes" and \
        series.properties.get("highway") != "footway" and \
        series.properties.get("highway") != "cycleway":
        
        ax.plot(*series.geometry.xy, color='red')
        # print("BRIDGE!!!") 

# Limit the map to the query's bounding box
plt.xlim(tl[1], br[1])
plt.ylim(br[0], tl[0])

# plot the NBI point, origin
ax.plot(origin[1], origin[0], 'y*', markersize=10)

# Show the map
plt.show()