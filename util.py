import csv
import math
import numpy as np
from overpy import Way
class nbiparser:
    '''A class that helps with parsing data from NBI files in the csv format.'''
    def __init__(self, file: str):
        '''
        Initializes an nbiparser class with a filename and puts its data in self.mylist.
        
        Parameters
        -----
        file : str
            The path of the NBI CSV file to open.
        
        Returns
        -----
        A new nbiparser class with prepared data'''
        NBI_filtered_data = open(file, 'r')
        reader = csv.DictReader(NBI_filtered_data)
        self.myList = list(reader)

    def modified_data(self) -> list:
        '''
        Creates a list of human-readable data in the form of a list of dictionaries.
        
        Returns
        -----
        A list of dictionaries. Each dictionary is one bridge entry from NBI and contains keys such as:
            id-state, carried-by, lat, lon, deck-rating, inv-rating, culvert rating, etc.'''
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
    '''A class that functions as a VERY simple wrapper for the Nominatim API. Currently, keys are not supported by this class.'''
    def __init__(self, address="https://nominatim.openstreetmap.org") -> None:
        '''
        Initialize a nominatim object with a set address. 
        
        Parameters
        -----
        address : str
            The API address to resolve requests to. (default is https://nominatim.openstreetmap.org)
            
        Returns
        -----
        A nominatim object with a set address.
        '''
        self.address = address
        
    def request(self, parameters:dict, endpoint:str) -> any:
        '''
        Creates a request to the Nominatim API defined by self.address and returns the response in json format.
        
        Parameters
        -----
        parameters : dict
            a dictionary of parameters to apply to the query.
        endpoint : str
            The endpoint to use. (e.g. "search", "reverse", "status")

        Returns
        -----
        A json object containing the Nominatim response'''
        url = self.address
        url += "/" + endpoint
        
        if len(parameters.keys()) != 0:
            url += "?"
            for k,v in parameters.items():
                url += f"{k}={v}&"
                # print(k,v)
        
        response = requests.request("GET", url)
        return response.json()


from math import *
class geo:
    '''A class that contains methods for working with and generating geometrical and geographical data'''
    def bbox_from_point(point:tuple, dist:float=1000) -> tuple:
        """
        Create a bounding box from a (lat, lon) center point.

        Create a bounding box some distance in each direction (north, south, east,
        and west) from the center point and optionally project it.

        Code from OSMNX Source: https://github.com/gboeing/osmnx/blob/main/osmnx/utils_geo.py#L427 
        
        Parameters
        ----------
        point : tuple
            The (lat, lon) center point to create the bounding box around
        dist : int
            Bounding box distance in meters from the center point

        Returns
        -------
        A tuple in the form:
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
    
    def centroid(polyline:list) -> tuple:
        """
        Get the centroid point of a group of polylines. This is the average of all points in the list.
        Parameters
        -------
        polyline : list
            A polyline object in list format: [[x,y], [x,y],...]

        Returns
        -------
        The centroid of the polyline as a tuple: (x,y)
        e.g. centroid([[3,3], [1,1]]) >>> (2,2)
        """
        t = (sum([item[0] for item in polyline])/len(polyline), sum([item[1] for item in polyline])/len(polyline))
        return t
    
    def make_point(name:str, point: tuple[float, float]):
        '''
        Creates a 'point' that contains a name and coordinates.
        
        Parameters
        -----
        name : str
            The name of the point. This is used for pattern matching in the heuristics class.
        point : tuple
            A tuple that contains the coordinates in the format (lat, lon).
            
        Returns
        -----
        A dict of the format
            {'name': "name", 'coord': (lat,lon)}'''
        return {'name': name, 'coord': point}
    

    def make_polyline(way: Way) -> list[list[float, float]]:
        '''
        Creates a 'Polyline' object from an Overpy Way object. This Polyline is a set of points that define a line.
        
        Parameters
        -----
        way : overpy.Way
            An overpy Way object
        
        Returns
        -----
        A 'Polyline' object as a list of lists.
            e.g. [[0,1], [0,2], [1,3]]
        '''
        return [[float(node.lat), float(node.lon)] for node in way.get_nodes(resolve_missing=True)]
    
    # class point:
        # def __init__(self, name: str, point: tuple[float,float]):
        #     self.name = name
        #     self.point = point
        #     pass
    
from PIL import Image
import io 
class mapbox_static:
    '''An unused class that defines usage for mapbox. (https://www.mapbox.com)'''
    def get_img_from_bbox(key:str, bbox:tuple, user:str='mapbox', style:str='satellite-streets-v12', size:tuple=(400, 400)) -> Image.Image:
        '''
        Gets a static image from the Mapbox API and returns it as a PIL Image.

        Parameters
        ---
        key : str
            The key to use for the mapbox API.
        bbox : tuple
            A tuple that defines the image's bounding box in the form (north, south, east, west). This is equivalient to a bounding box returned
            from geo.bbox_from_point()
        user : str, optional
            The name of the user if a spcific map style is desired. (default is mapbox)
        style : str, optional
            The name of the style to use. (default is satellite-streets-v12)
        size : tuple, optional
            The size of the image to generate. (default is 400x400px)

        Returns
        -----
        A PIL Image containing the returned static map.
        '''
        north, south, east, west = bbox

        call = f'https://api.mapbox.com/styles/v1/{user}/{style}/static/[{west},{south},{east},{north}]/{size[0]}x{size[1]}?access_token={key}'

        response = requests.get(call)

        stream = io.BytesIO(response.content)
        img = Image.open(stream)
        return img

from difflib import SequenceMatcher
from geopy import distance
class heuristics:
    '''A class to define heuristics and scoring.'''
    def simple_pattern(str1:str, str2:str) -> float:
        '''Calculates a simple heuristic using only Python's Sequence Matcher Class.
        This is done by getting the average match score between two strings (mscore1+mscore2)/2, 
        since Sequencematcher.ratio() is not commutative. Returns a score in range (0...1].
        
        Parameters
        -----
        str1 : str
            A string to compare against str2
        str2 : str
            A string to compare against str1

        Returns
        -----
        A score as a float from range (0,1].
        '''
        if str1 == None or str2 == None: return 0
        strcln1 = str.lower(str1)
        strcln2 = str.lower(str2)
        if strcln1 == strcln2: return 1
        ratio1 = SequenceMatcher(lambda x: x==' ', strcln1, strcln2).ratio()
        ratio2 = SequenceMatcher(lambda x: x==' ', strcln2, strcln1).ratio()
        return (ratio1 + ratio2) / 2

    def sorensen_dice(str1:str, str2:str) -> float:
        '''Calculates a score using the Sorensen Dice Algorithm. Returns a score in range (0...1].
        
        Parameters
        -----
        str1 : str
            A string to compare against str2
        str2 : str
            A string to compare against str1

        Returns
        -----
        A score as a float from range (0,1].
        '''
        if str1 == None or str2 == None: return 0
        strcln1 = str.lower(str1)
        strcln2 = str.lower(str2)
        if strcln1 == strcln2: return 1
        a = set(strcln1)
        b = set(strcln2)
        score = (2*len(a.intersection(b))) / (len(a) + len(b))
        return score
    
    def simple_distance(coord1:tuple, coord2:tuple, t:float=10) -> float:
        '''Calculates a simple distance between two (x,y) points and returns a score.
        A lower score means the points are further apart. A score of 1 means the points are the same.
    
        Parameters
        -------
        coord1 : tuple
            A tuple in the form of (latitude, longitude) that describes the coordinates of point 1.
        
        coord2 : tuple
            A tuple in the form of (latitude, longitude) that describes the coordinates of point 2.

        t : float, optional
            A threshold value to score on. When distance between the two coordinates is less than t, 
            the resulting score > 0.5. Otherwise, the score <= 0.5. Score is in range (0...1]. (Default is 10)
        
        Returns
        -----
        A score as a float from range (0,1].
        '''
        if coord1 == coord2: return 1
        dist = distance.distance(coord1, coord2).meters
        # Use a simple equation to create a score
        score = t/(dist+t)
        # score = max(0, 1-(dist/x))
        return score
    
    def shortest_distance(polyline:list[list], point:list, t:float=10) -> float:
        '''Calculates the shortest distance between a point and a polyline and returns a score.
        A lower score means the points are further apart. A score of 1 means the points are the same.
        Heavily refers to the anser found here: https://stackoverflow.com/questions/10983872/distance-from-a-point-to-a-polygon.
    
        Parameters
        -------
        polyline : list[list]
            A list the describes a polyline in the form of [[x1,y1], [x2,y2], ...].
        
        coord2 : tuple
            A tuple in the form of (latitude, longitude) that describes the coordinates of the point.

        t : float, optional
            A threshold value to score on. When distance between the two is less than t, 
            the resulting score > 0.5. Otherwise, the score <= 0.5. Score is in range (0...1]. (Default is 10)
        
        Returns
        -----
        A score as a float from range (0,1].
        '''
        min_dist = None

        vertices = np.array(polyline)
        x = np.array(point, dtype=np.float64)
        for i in range(vertices.shape[0]-1):
            p1 = vertices[i]
            p2 = vertices[i+1]
            r = np.dot((np.subtract(p2, p1)), (np.subtract(x, p1)))
            r /= (np.linalg.norm(np.subtract(p2, p1)) ** 2)

            if r < 0:
                dist = distance.distance(x, p1).meters
            elif r > 1:
                dist = distance.distance(x, p2).meters
            else:
                dist = sqrt(abs(distance.distance(x, p1).meters ** 2 - (r * distance.distance(p2, p1).meters) ** 2))

            min_dist = dist if min_dist == None else min(dist,min_dist)

        # Use a simple equation to create a score
        score = t/(min_dist+t)
        # score = max(0, 1-(dist/x))
        return score
    
    @classmethod
    def calculate_score_simple(c, point1: dict, point2: dict) -> float:
        '''Calculates a score that takes the average of simple_distance() and simple_pattern().
        Returns a score is in range (0...1].
        
        Parameters
        -------
        point1 : dict
            A dictionary in the form of {name:"name", coord:(x,y)}. This is equivalent to a point returned by geo.make_point().
        point2 : dict
            A dictionary in the form of {name:"name", coord:(x,y)}. This is equivalent to a point returned by geo.make_point().
        
        Returns
        -----
        A score as a float from range (0,1].
        '''
        dist_score = c.simple_distance(point1.get('point'), point2.get('point'))
        patr_score = c.simple_pattern(point1.get('name'), point2.get('name'))
        return (dist_score + patr_score) / 2
