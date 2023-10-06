import overpass
import geopandas as gpd
import matplotlib.pyplot as plt
from util import CoordinateCalculator

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')

class Visualizer:
    ovp = overpass.API(endpoint=f"{OVP_ENDPOINT}/interpreter")
    points = [(41.3209, -96.0449),(41.3236, -96.0449),(41.3154, -96.0524),\
                (41.3293, -96.0482),(41.311 , -96.0475),(40.0249, -95.3837)]

    @classmethod
    def analyze_point(c, point:tuple, show:bool=False, save:bool=False):
        pt_lat = point[0]
        pt_lon = point[1]

        # Bounding box size in km
        side_length = 0.2
        tl, br = CoordinateCalculator.get_bounding_box((pt_lat, pt_lon), side_length)

        # Relations break our queries for some reason and are not needed. Just use nodes and ways.
        query = f"nw({br[0]}, {tl[1]}, {tl[0]}, {br[1]}); out;"

        # Query the data and put it into a GeoDataFrame
        response = c.ovp.get(query, verbosity="geom")
        gdf = gpd.GeoDataFrame(response.features)
        
        # If the data frame is empty, exit
        if gdf.size == 0: return
        # print(gdf.tail(10))

        # set the coordinate relation system
        gdf.set_crs("EPSG:4326")

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
        ax.plot(point[1], point[0], 'y*', markersize=10)

        plt.title(point)

        # Show the map
        if show: plt.show()

        if save: plt.savefig(f"./out/nonx-viz/nonx{point}.jpg", format='jpg')
        
        plt.close()