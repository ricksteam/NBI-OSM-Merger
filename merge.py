from osm_handler import OSMHandler
from nbi_parser import nbiparser

# RUN __main__
osm = OSMHandler()

# Parse osm data
osm_file = "sample2.osm"
osm.parse(osm_file)
osm_dat = osm.clean()

# parse nbi data
nbi_file = "Updated_NBI_DATA_POC.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

print(nbi_dat)
print(osm_dat)

print("Non-footway bridges in OSM: %d" % (len(osm_dat) ))
print("Bridges in NBI: %d" % len(nbi_dat))
exit(0)