import overpass
import geopandas as gpd
import matplotlib.pyplot as plt
from util import geo, mapbox_static

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')
MAPBOX_KEY = os.environ.get('MAPBOX_KEY')

class Visualizer:
    ovp = overpass.API(endpoint=f"{OVP_ENDPOINT}/interpreter")
    points = [(41.3209, -96.0449),(41.3236, -96.0449),(41.3154, -96.0524),\
                (41.3293, -96.0482),(41.311 , -96.0475),(40.0249, -95.3837)]

    @classmethod
    def analyze_point(c, point:tuple, show:bool=False, save:bool=False):
        pt_lat = point[0]
        pt_lon = point[1]

        # Bounding box size in m
        side_length = 200
        bbox = geo.bbox_from_point((pt_lat, pt_lon), side_length)
        north, south, east, west = bbox

        # Relations break our queries for some reason and are not needed. Just use nodes and ways.
        query = f"nw({south}, {west}, {north}, {east}); out;"

        # Query the data and put it into a GeoDataFrame
        response = c.ovp.get(query, verbosity="geom")
        gdf = gpd.GeoDataFrame(response.features)
        
        # If the data frame is empty, exit
        if gdf.size == 0: return
        # print(gdf.tail(10))

        # set the coordinate relation system
        # gdf.set_crs("EPSG:4326")

        # img = mapbox_static.get_img_from_bbox(MAPBOX_KEY, bbox,)
        # plt.imshow(img)

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
        plt.xlim(west, east)
        plt.ylim(south, north)

        # plot the NBI point, origin
        ax.plot(point[1], point[0], 'y*', markersize=10)

        plt.title(point)

        # Show the map
        if show: plt.show()

        if save: plt.savefig(f"./out/nonx-viz/nonx{point}.jpg", format='jpg')
        
        plt.close()