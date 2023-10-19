import csv

class nbiparser:
    def __init__(self, file):
        NBI_filtered_data = open(file, 'r')
        reader = csv.DictReader(NBI_filtered_data)
        self.myList = list(reader)
    def modified_data(self):
        final_list = []
        for ele in self.myList:
            final_list.append({
                "id-state":ele["1 - State Code"],
                "carried-by":ele["7 - Facility Carried By Structure"].strip(),
                "id-no":ele["8 - Structure Number"].strip(),
                "lat":ele["16 - Latitude (decimal)"],
                "lon":ele["17 - Longitude (decimal)"],
                "id-owner":ele["22 - Owner Agency"].strip(),
                "yr-built":ele["27 - Year Built"].strip(),
                "deck-rating":ele["58 - Deck Condition Rating"].strip(),
                "super-cond":ele["59 - Superstructure Condition Rating"].strip(),
                "sub-cond":ele["60 - Substructure Condition Rating"].strip(),
                "culvert-rating":ele["62 - Culverts Condition Rating"].strip(),
                "op-method-code":ele["63 - Operating Rating Method Code"].strip(),
                "op-rating":ele["64 - Operating Rating (US tons)"],
                "inv-rating":ele["66 - Inventory Rating (US tons)"],
                "insp-freq":ele["91 - Designated Inspection Frequency"],
                })
        return final_list
        
import requests

class nominatim:
    def __init__(self, address="https://nominatim.openstreetmap.org") -> None:
        self.address = address
        
    def request(self, parameters:dict, endpoint:str) -> str:
        url = self.address
        url += "/" + endpoint

        if len(parameters.keys()) != 0:
            url += "?"
            for k,v in parameters.items():
                url += f"{k}={v}&"
                # print(k,v)
        
        response = requests.request("GET", url)
        return response.json()

# Example usage
# n = nominatim("...")
# response = n.request({'format':'jsonv2',
#             'lat':"41.3154",
#             'lon':"-96.0524",},
#             'reverse')
# print(response)


from math import *
class geo:

    def bbox_from_point(point:tuple, dist:float=1000) -> tuple:
        """
        Create a bounding box from a (lat, lon) center point.

        Create a bounding box some distance in each direction (north, south, east,
        and west) from the center point and optionally project it.

        Code from OSMNX Source: https://github.com/gboeing/osmnx/blob/main/osmnx/utils_geo.py#L427 
        Parameters
        ----------
        point : tuple
            the (lat, lon) center point to create the bounding box around
        dist : int
            bounding box distance in meters from the center point

        Returns
        -------
        tuple
            (north, south, east, west)
        """
        earth_radius = 6_371_009  # meters
        lat, lon = point

        delta_lat = (dist / earth_radius) * (180 / pi)
        delta_lon = (dist / earth_radius) * (180 / pi) / cos(lat * pi / 180)
        north = lat + delta_lat
        south = lat - delta_lat
        east = lon + delta_lon
        west = lon - delta_lon

        # otherwise
        return north, south, east, west
    
    def centroid(polyline:list):
        t = (sum([item[0] for item in polyline])/len(polyline), sum([item[1] for item in polyline])/len(polyline))
        return t
    
from PIL import Image
import io 
class mapbox_static:
    def get_img_from_bbox(key:str, bbox:tuple, user:str='mapbox', style:str='satellite-streets-v12', size:tuple=(400, 400)) -> Image.Image:
        north, south, east, west = bbox

        call = f'https://api.mapbox.com/styles/v1/{user}/{style}/static/[{west},{south},{east},{north}]/{size[0]}x{size[1]}?access_token={key}'

        response = requests.get(call)

        stream = io.BytesIO(response.content)
        img = Image.open(stream)
        return img

