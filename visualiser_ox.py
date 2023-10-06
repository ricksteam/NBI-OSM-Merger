import matplotlib.pyplot as plt
import osmnx as ox

from dotenv import load_dotenv
import os

load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')
NMN_ENDPOINT = os.environ.get('NMN_ENDPOINT')

ox.settings.overpass_endpoint = OVP_ENDPOINT
ox.settings.nominatim_endpoint = NMN_ENDPOINT
ox.settings.overpass_rate_limit = False
# ox.settings.use_cache = False

class VisualizerOX:

    @classmethod
    def analyze_point(c, point: tuple, show:bool=False, save:bool=False):
        # Returns (north, south, east, west)
        bbox:tuple = ox.utils_geo.bbox_from_point(point, 200)

        # gdf = ox.graph_from_bbox(*bbox)
        gdf = ox.features_from_bbox(*bbox, tags={
                                        'bridge': True,
                                        'highway': True,
                                        'building': True,
                                        'waterway': True,
                                        'amenity': True,
                                        'barrier': True, })

        # create the initial map
        ax = gdf.plot(markersize=0)

        # # Iterate through the returned rows
        series_itr = gdf.iterrows()
        for row in series_itr:
            # rows are in (id, Series) format
            series = row[1]
            # If the Series has a bridge tag, highlight it
            if getattr(series, 'bridge', None) == "yes" and \
                series.highway != "footway" and \
                series.highway != "cycleway":
                
                ax.plot(*series.geometry.xy, color='red')

        # Limit the map to the query's bounding box
        plt.ylim(bbox[1], bbox[0])
        plt.xlim(bbox[3], bbox[2])

        # plot the NBI point, origin
        ax.plot(point[1], point[0], 'y*', markersize=10)
        plt.title(point)

        # Show the map
        if show: plt.show()

        if save: plt.savefig(f"./out/ox-viz/nx{point}.jpg", format='jpg')
        
        plt.close()