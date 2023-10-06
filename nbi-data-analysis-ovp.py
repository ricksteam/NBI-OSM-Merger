import csv
import overpy
from util import CoordinateCalculator, nbiparser
from datetime import datetime
from tqdm import tqdm
from osm_handlers import OSMNBIAnalyzer

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')

# Prep Nominatim API
ovp = overpy.Overpass(url=f"{OVP_ENDPOINT}/interpreter")

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

relations = {}

count = 0
print("Querying OSM data per bridge using Overpass...")
for bridge in tqdm(nbi_dat):
    # Add match info
    bridge.update({"osm-match":"False"})
    bridge.update({"osm-match-id": "None"})

    # Drop culvert bridges for now. 
    if bridge['culvert-rating'] != "N":
        continue

    # Make the query for Overpass
    lat = float(bridge['lat'])
    lon = float(bridge['lon'])
    # Bounding box size in km
    side_length = 0.25
    tl, br = CoordinateCalculator.get_bounding_box((lat, lon), side_length)
    # print(f"nwr({br[0]}, {tl[1]}, {tl[0]}, {br[1]});")
    response = ovp.query(
        # f"nwr(south, west, north, east);"
        f"nw({br[0]}, {tl[1]}, {tl[0]}, {br[1]});"
        f"out;"
        )

    way_ids=[]
    # TODO: Determine what ways in the query should have the NBI data applied to it.
    for way in response.ways:
        # In Overpy, tags are stored in a basic dictionary.
        if way.tags.get("bridge") == "yes" and way.tags.get("highway") != "footway" and way.tags.get("highway") != "cycleway":
            # Key: OSM_ID, Value: NBI_ID
            relations.update({str(way.id): bridge})
            # way_ids.append(way.id)

    # An OSM way can have AT MOST one NBI bridge 
    # Multiple OSM ways may have the same NBI data 
    # for id in way_ids:
            # Key: OSM_ID, Value: NBI_ID
            # relations.update({str(id): bridge})

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