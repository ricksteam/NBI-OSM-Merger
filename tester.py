from osm_handler import OSMParser
from nbi_parser import nbiparser

# RUN __main__
osm = OSMParser()

# Parse osm data
osm_file = "in/area-original.osm"
osm.parse(osm_file)
osm_dat = osm.clean()

# parse nbi data
nbi_file = "in/NE_NBI_DATA.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

# print(nbi_dat)
# print(osm_dat)

print("Non-footway bridges in OSM: %d" % (len(osm_dat) ))
print("Bridges in NBI: %d" % len(nbi_dat))
exit(0)