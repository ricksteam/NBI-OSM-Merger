from osm_handlers import OSMBridgeCounter
from util import nbiparser, CoordinateCalculator

from math import *
origin = (40.02285, -95.36835)
distance = 1
results = CoordinateCalculator.get_bounding_box(origin, distance)
print(results)

# RUN __main__
osm = OSMBridgeCounter()

# Parse osm data
osm_file = "in/nebraska-latest.osm.pbf"
osm.apply_file(osm_file)

# parse nbi data
# nbi_file = "in/NE_NBI_DATA.csv"
# c1 =  nbiparser(nbi_file)
# nbi_dat =  c1.modified_data()

# print(nbi_dat)
# print(osm_dat)

print("Non-footway bridges in OSM: %d" % (osm.total))
# print("Bridges in NBI: %d" % len(nbi_dat))
exit(0)