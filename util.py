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
class CoordinateCalculator:
    # mean radius = 6,371km
    earth_radius = 6371.137
    # Angle to top-left is 315 degrees
    tl_angle = radians(315)
    # Angle to bottom right is 135 degrees
    br_angle = radians(135)

    @classmethod
    def get_bounding_box(c, origin: tuple, side_length: float):
        # Get distance of half the diagonal of the square
        half_distance = (side_length * sqrt(2)) / 2
        tl_lat, tl_lon = c.calc_dest(origin, c.tl_angle, half_distance)
        br_lat, br_lon = c.calc_dest(origin, c.br_angle, half_distance)

        return((tl_lat,tl_lon) , (br_lat,br_lon))

    @classmethod
    def calc_dest(c, origin: tuple, bearing: float, distance: float):
        # from: https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
        # and: https://math.stackexchange.com/questions/72294/how-can-i-get-a-square-starting-with-a-latitude-and-longitude-point
        # and: http://www.movable-type.co.uk/scripts/latlong.html
        lat1 = radians(origin[0])
        lon1 = radians(origin[1])
        dR = distance/c.earth_radius

        # lat2 = asin(sin(lat1)*cos(d/R) + cos(lat1)*sin(d/R)*cos(θ))
        lat2 = asin(sin(lat1)*cos(dR) + cos(lat1)*sin(dR)*cos(bearing))
        # lon2 = lon1 + atan2(sin(θ)*sin(d/R)*cos(lat1), cos(d/R)−sin(lat1)*sin(lat2))
        lon2 = lon1 + atan2(sin(bearing)*sin(dR)*cos(lat1), cos(dR)-sin(lat1)*sin(lat2))
        # θ is the bearing (in radians, clockwise from north); 
        # d/R is the angular distance (in radians), 
        # where d is the distance travelled and R is the earth’s radius

        return (degrees(lat2), degrees(lon2))
            