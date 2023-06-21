from osm_handlers import OSMNodeMerger
import osmium
from util import nbiparser
from datetime import datetime

## Using pyosmium will likely not work for this, as it intended for editing existing data, not adding new data.
## Please use merge-node-xml instead.

# If true, NBI info will be logged.
DEBUG = False

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# parse nbi data
nbi_file = "in/NE_NBI_DATA.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

# Use the OSM parser to write new OSM data to a file.

# Create the PBF Handler and apply the desired OSM data for tag editing.
osm_writer = osmium.SimpleWriter('merge-nodes'+time+'.osm')
file_writer = OSMNodeMerger(osm_writer, nbi_dat)

# Create the OSM Handler and apply the desired OSM data for tag editing.
# pbf_writer = osmium.SimpleWriter('merge'+time+'.pbf')
# file_writer = OSMNBIMerger(pbf_writer, ways)

print("Writing NBI tags to OSM...")
file_writer.apply_file("in/nebraska-latest.osm.pbf")

# Close OSM writer and finish up!
file_writer.close()
print("Done!")