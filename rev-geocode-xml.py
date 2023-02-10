import osmnx as nx
import osmium
from nbi_parser import nbiparser
import numpy as np
import xml.etree.ElementTree as et

def NBIElem(parent, key, value):
    tag = et.SubElement(parent, 'tag')
    tag.attrib.update({'k':key,'v':value})

# parse nbi data
nbi_file = "Updated_NBI_DATA_POC.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

# print(nbi_dat)
ways = {}

for i, bridge in enumerate(nbi_dat):
    # Drop culvert bridges for now. 
    if bridge['super-cond'] == "'N'":
        continue

    # TODO: Try to get just the closest node (not way) from this Nominatim request. (This may not be necessary, culverts are causing issues)
    response = \
    nx.downloader.nominatim_request({'format':'jsonv2',
                                    'lat':bridge['lat'],
                                    'lon':bridge['lon'],
                                    },
                                    "reverse")
    # print(response['osm_type'], response['osm_id'])
    ways.update({str(response['osm_id']): bridge})

# Test API call
# reverse?format=jsonv2&lat=41.3154&lon=-96.0524

# Test response is in a dictionary format like so:
# {
# 'place_id': 145032528, 
# 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', 
# 'osm_type': 'way', 
# 'osm_id': 166431111, 
# 'lat': '41.31539279311863', 
# 'lon': '-96.05235745346259', 
# 'place_rank': 26, 
# 'category': 'highway', 
# 'type': 'primary', 
# 'importance': 0.09999999999999998, 
# 'addresstype': 'road', 
# 'name': 'Sorensen Parkway', 
# 'display_name': 'Sorensen Parkway, Irvington, Omaha, Douglas County, Nebraska, 68122, United States', 
# 'address': { 
#   'road': 'Sorensen Parkway', 
#   'hamlet': 'Irvington', 
#   'city': 'Omaha', 
#   'county': 'Douglas County', 
#   'state': 'Nebraska', 
#   'ISO3166-2-lvl4': 'US-NE', 
#   'postcode': '68122', 'country': 
#   'United States', 
#   'country_code': 'us'}, 
# 'boundingbox': ['41.3150507', '41.31551', '-96.0524154', '-96.0523376']
# }


# This is all the OLD merging process using XML
# We want to instead, parse these new tags into a new OSM file.
tree = et.parse("area-original.osm")
root = tree.getroot()
# root.find()
for osm_way in root.findall("way"):
    if osm_way.attrib['id'] in list(ways.keys()):
        print(osm_way.attrib['id'] + ": ", end="")
        # Check stored ways for bridge/footway tags. 
        # If it is not a bridge, list it out to view the issues.
        if osm_way.find(".//tag[@k='bridge'][@v='yes']") == None:
            print("NOT A BRIDGE:", len(osm_way.findall(".//nd")), "nodes")
            continue
        NBIElem(osm_way, 'nbi', 'yes')
        NBIElem(osm_way, 'nbi:super-cond', ways[osm_way.attrib['id']]['super-cond'])
        NBIElem(osm_way, 'nbi:sub-cond', ways[osm_way.attrib['id']]['sub-cond'])
        NBIElem(osm_way, 'nbi:op-rating', ways[osm_way.attrib['id']]['op-rating'])
        NBIElem(osm_way, 'nbi:op-method-code', ways[osm_way.attrib['id']]['op-method-code'])
        NBIElem(osm_way, 'nbi:deck-rating', ways[osm_way.attrib['id']]['deck-rating'])
        print("BRIDGE:\t", len(osm_way.findall(".//nd")), "nodes")


tree.write('area-merged-culverts.osm')
