import csv
import overpass, overpy
import geopandas as gpd
from util import geo, nbiparser, heuristics
from datetime import datetime
from tqdm import tqdm
from osm_handlers import OSMNBIAnalyzer
from visualiser_folium import folyzer

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')

# Prep Nominatim API
ovpy = overpy.Overpass(url=f"{OVP_ENDPOINT}/interpreter")
# ovps = overpass.API(endpoint=f"{OVP_ENDPOINT}/interpreter")

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

relations = {}

count = 0
print("Querying OSM data per bridge using Overpass...")
for bridge in nbi_dat:#tqdm(nbi_dat):
    # Add match info
    bridge.update({"osm-match":"False"})
    bridge.update({"osm-match-id": "None"})

    # Drop culvert bridges for now. 
    if bridge['culvert-rating'] != "N":
        continue

    # Make the query for Overpass
    lat = float(bridge['lat'])
    lon = float(bridge['lon'])

    # Bounding box size in meters
    size = 100
    north, south, east, west = geo.bbox_from_point((lat, lon), size)
    
    # Create the Overpass Query. Get Nodes and Ways within the bounding box
    query = f"nw({south}, {west}, {north}, {east}); out;"
    response = ovpy.query(query)

    # Continue if the repsonse is empty
    if len(response.ways) == 0: continue

    osm_scores={}
    # TODO: Determine what ways in the query should have the NBI data applied to it.
    for way in response.ways:
        
        # In Overpy, tags are stored in a basic dictionary.
        if way.tags.get("bridge") == "yes" and way.tags.get("highway") != "footway" and way.tags.get("highway") != "cycleway":
        # Apply bridge heuristics with the if statement here.
            nbi_point = geo.make_point(bridge['carried-by'], (bridge['lat'], bridge['lon']))
            osm_point = geo.make_point(way.tags.get("name"), geo.centroid(geo.make_polyline(way)))
            # score = heuristics.calculate_score_simple(nbi_point, osm_point)
            dscore = heuristics.simple_distance(nbi_point['coord'], osm_point['coord'], x=20)
            pscore = heuristics.simple_pattern(nbi_point['name'], osm_point['name'])

        # An OSM way can have AT MOST one NBI bridge 
        # Multiple OSM ways may have the same NBI data 
        # for id in way_ids:
            # Key: OSM_ID, Value: NBI_Data
            relations.update({str(way.id): bridge})
            osm_scores.update({way: (dscore, pscore)})

    # Currently, If we find any number of bridges besides 1, something wonky is going on.
    # 0 Bridges means OSM data is bad. 2+ bridges means we need to employ good heuristics.
    # if len(bridge_ways) != 1:
    folyzer.visualize_point(bridge, osm_scores)

    count += 1
    # if count == 40: exit(0)

# TODO: Add visualizer code in here so we can snapshot bad data points
# It looks like we can use OSMNX or non-OX version. Benchmark to see which is faster and implement.    

# Create the PBF Handler and apply the desired OSM data for tag editing.
file_writer = OSMNBIAnalyzer(relations, nbi_dat[0].keys())

print("Writing NBI tags to OSM...")
file_writer.apply_file("in/nebraska-latest.osm.pbf")

    
# writing to csv file 
with open("out/NBI-Analysis-ovp.csv", 'w', newline='') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(nbi_dat[0].keys()) 
    
    for bridge in nbi_dat:
        # writing the data rows 
        csvwriter.writerow(list(bridge.values()))

print("Done!")
