import osmium
from osm_handlers import OSMNBIMergerOP
from util import nbiparser, CoordinateCalculator
import overpy
from datetime import datetime
from tqdm import tqdm

# If true, NBI info will be logged.
DEBUG = False

# Prep Overpass API
ovp = overpy.Overpass(url="http://52.201.224.66:12345/api/interpreter")

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

if DEBUG: 
    # Open file for debug log
    log_file = open(f"out/rg-log-{time}.txt", "w")

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

relations = {}

count = 0
print("Querying OSM data per bridge using Overpass...")
for bridge in tqdm(nbi_dat):
    # Drop culvert bridges for now. 
    if bridge['culvert-rating'] != "N":
        if DEBUG: # DEBUG LOG
            count += 1
            log_file.write(f"{count}\tculvert\n")
            # END DEBUG
        continue

    # Make the query for Overpass
    pt_lat = float(bridge['lat'])
    pt_lon = float(bridge['lon'])
    # Bounding box size in sq km
    box_size = 0.8
    tl, br = CoordinateCalculator.get_bounding_box((pt_lat, pt_lon), box_size/2)
    # print(f"nwr({br[0]}, {tl[1]}, {tl[0]}, {br[1]});")
    response = ovp.query(
        # f"nwr(south, west, north, east);"
        f"nwr({br[0]}, {tl[1]}, {tl[0]}, {br[1]});"
        f"out;"
        )
    
    if DEBUG: # DEBUG LOG
        count += 1
        for way in response.ways:
            print("Name: %s" % way.tags.get("name"))
            print("  Highway: %s" % way.tags.get("highway"))
            print("  Bridge: %s" % way.tags.get("bridge"))

    way_ids=[]
    # TODO: Determine what ways in the query should have the NBI data applied to it.
    for way in response.ways:
        # In Overpy, tags are stored in a basic dictionary.
        if way.tags.get("bridge") == "yes": #and way.tags.get("highway") != "footway" and way.tags.get("highway") != "cycleway":
            # An OSM way can have AT MOST one NBI bridge 
            # Multiple OSM ways may have the same NBI data 
            # In other words, one NBI bridge may be associated with multiple OSM ways
            # Key: OSM_ID, Value: NBI_ID
            relations.update({str(way.id): bridge})
            # way_ids.append(way.id)
    
    if DEBUG: print("Relations found: " + str(len(relations)))

if DEBUG:
    # Close and save the log file
    log_file.close()

# Use the OSM parser to write new OSM data to a file.

# Create the PBF Handler and apply the desired OSM data for tag editing.
extension = 'pbf'
osm_writer = osmium.SimpleWriter(f'out/merge{time}.{extension}')
file_writer = OSMNBIMergerOP(osm_writer, relations)

print("Writing NBI tags to OSM...")
file_writer.apply_file("in/nebraska-latest.osm.pbf")

# Close OSM writer and finish up!
file_writer.close()
print("Done!")