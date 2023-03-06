import osmium
from osm_handler import *
from nbi_parser import nbiparser
from datetime import datetime
from nom_api import nominatim

# Prep Nominatim API
nom = nominatim("http://52.201.224.66:8080")

# parse nbi data
nbi_file = "/in/NE_NBI_DATA.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

# print(nbi_dat)
ways = {}

for i, bridge in enumerate(nbi_dat):
    # Drop culvert bridges for now. 
    if bridge['super-cond'] == "N":
        continue

    response = nom.request({'format':'jsonv2',
            'lat':bridge['lat'],
            'lon':bridge['lon'],},
            'reverse')

    # print(response['osm_type'], response['osm_id'])
    ways.update({str(response['osm_id']): bridge})


# Use the OSM parser to write new OSM data to a file.

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# Create the PBF Handler and apply the desired OSM data for tag editing.
osm_writer = osmium.SimpleWriter('merge'+time+'.osm')
file_writer = OSMNBIMerger(osm_writer, ways)

# Create the OSM Handler and apply the desired OSM data for tag editing.
# pbf_writer = osmium.SimpleWriter('merge'+time+'.pbf')
# file_writer = OSMNBIMerger(pbf_writer, ways)

file_writer.apply_file("/out/nebraska-latest.osm.pbf")