import osmnx as nx
import osmium
from osm_handler import *
from nbi_parser import nbiparser
from datetime import datetime

# parse nbi data
nbi_file = "Updated_NBI_DATA_POC.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

# print(nbi_dat)
ways = {}

for i, bridge in enumerate(nbi_dat):
    # Drop culvert bridges for now. 
    if bridge['super-cond'] == "N":
        continue

    response = \
    nx.downloader.nominatim_request({'format':'jsonv2',
                                    'lat':bridge['lat'],
                                    'lon':bridge['lon'],
                                    },
                                    "reverse")
    # print(response['osm_type'], response['osm_id'])
    ways.update({str(response['osm_id']): bridge})


# Use the OSM parser to write new OSM data to a file.

# We will write to a tags<TIME>.osm file
s_writer = osmium.SimpleWriter('tags'+str(datetime.timestamp(datetime.now()))+'.osm')

# Create the OSM Handler and apply the desired OSM data for tag editing.
file_writer = OSMNBIMerger(s_writer, ways)
file_writer.apply_file("area-original.osm")
