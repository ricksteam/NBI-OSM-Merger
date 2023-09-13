import csv
import overpy
from util import nbiparser
from datetime import datetime
from tqdm import tqdm
from osm_handlers import OSMNBIAnalyzer

# Prep Nominatim API
ovp = overpy.Overpass(url="http://52.201.224.66:12345/api/interpreter")

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
    # TODO: It currently uses a static bounding box. This should be changed to be dynamic.
    # TODO: Make it more of a box. Latitude and longitude are not quite the same distance
    lat = float(bridge['lat'])
    lon = float(bridge['lon'])
    half_lat = 0.002
    half_lon = 0.002
    # print (f"nwr({max(-90.0, lat-half_lat)}, {max(-180.0, lon-half_lon)}, {min(90.0, lat+half_lat)}, {min(180.0, lon+half_lon)});\n")
    response = ovp.query(
        # Make the bounding box size non-static.
        f"nwr({max(-90.0, lat-half_lat)}, {max(-180.0, lon-half_lon)}, {min(90.0, lat+half_lat)}, {min(180.0, lon+half_lon)});"

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