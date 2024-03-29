import osmium
from osm_handlers import OSMNBIMergerNominatim
from util import nbiparser, nominatim
from datetime import datetime
from tqdm import tqdm

# If true, NBI info will be logged.
DEBUG = False

from dotenv import load_dotenv
import os
load_dotenv()
NMN_ENDPOINT = os.environ.get('NMN_ENDPOINT')

# Prep Nominatim API
nom = nominatim(NMN_ENDPOINT)

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

if DEBUG: 
    # Open file for Rev Geoc log
    log_file = open(f"out/rg-log-{time}.txt", "w")

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

ways = {}

count = 0
print("Reverse-geocoding NBI data using Nominatim...")
for bridge in tqdm(nbi_dat):
    # Drop culvert bridges for now. 
    if bridge['culvert-rating'] != "N":
        if DEBUG: # DEBUG LOG
            count += 1
            log_file.write(f"{count}\tculvert\n")
            # END DEBUG
        continue

    response = nom.request({'format':'jsonv2',
            'lat':bridge['lat'],
            'lon':bridge['lon'],},
            'reverse')

    if DEBUG: # DEBUG LOG
        count += 1
        log_file.write(f"{count}\t{response['osm_id']}\n")
        # END DEBUG

    # print(response['osm_type'], response['osm_id'])
    ways.update({str(response['osm_id']): bridge})

if DEBUG:
    # Close and save the log file
    log_file.close()

# Use the OSM parser to write new OSM data to a file.

# Create the PBF Handler and apply the desired OSM data for tag editing.
osm_writer = osmium.SimpleWriter('out/merge'+time+'.osm')
file_writer = OSMNBIMergerNominatim(osm_writer, ways, debug=True)

# Create the OSM Handler and apply the desired OSM data for tag editing.
# pbf_writer = osmium.SimpleWriter('merge'+time+'.pbf')
# file_writer = OSMNBIMerger(pbf_writer, ways)

print("Writing NBI tags to OSM...")
file_writer.apply_file("in/nebraska-latest.osm.pbf")

# Close OSM writer and finish up!
file_writer.close()
print("Done!")