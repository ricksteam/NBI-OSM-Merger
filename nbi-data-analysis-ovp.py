import csv
import overpy
from util import geo, nbiparser, heuristics
from datetime import datetime
from tqdm import tqdm
from visualiser_folium import folyzer

from dotenv import load_dotenv
import os
load_dotenv()
OVP_ENDPOINT = os.environ.get('OVP_ENDPOINT')

# Prep Nominatim API
ovpy = overpy.Overpass(url=f"{OVP_ENDPOINT}/interpreter")
# ovps = overpass.API(endpoint=f"{OVP_ENDPOINT}/interpreter")

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

count = 0
print("Querying OSM data per bridge using Overpass...")
for bridge in tqdm(nbi_dat):
    # Add match info
    bridge.update({"osm-match":"False"})
    bridge.update({"osm-match-id": "None"})
    bridge.update({"osm-match-dsps": "None"})

    # Drop culvert bridges for now. 
    if bridge['culvert-rating'] != "N":
        continue

    # Get lat and lon values
    lat = float(bridge['lat'])
    lon = float(bridge['lon'])

    # Bounding box size in meters
    size = 100
    north, south, east, west = geo.bbox_from_point((lat, lon), size)
    
    # Create the Overpass Query. Get Nodes and Ways within the bounding box
    query = f"nw({south}, {west}, {north}, {east}); out;"
    response = ovpy.query(query)

    # Continue if the repsonse is empty
    if len(response.ways) == 0: continue

    way_inf=[]
    for way in response.ways:
        # In Overpy, tags are stored in a basic dictionary.
        if way.tags.get("bridge") == "yes" and way.tags.get("highway") != "footway" and way.tags.get("highway") != "cycleway":
            nbi_point = geo.make_point(bridge['carried-by'], (bridge['lat'], bridge['lon']))
            osm_point = geo.make_point(way.tags.get("name"), geo.centroid(geo.make_polyline(way)))
            # score = heuristics.calculate_score_simple(nbi_point, osm_point)
            dscore = heuristics.simple_distance(nbi_point['coord'], osm_point['coord'], t=20)
            # pscore = heuristics.simple_pattern(nbi_point['name'], osm_point['name'])
            pscore = heuristics.sorensen_dice(nbi_point['name'], osm_point['name'])

            way_inf.append({'way': way, 'scores': ('%.3f'%dscore, '%.3f'%pscore), 'selected': False})
            
            # An OSM way can have AT MOST one NBI bridge 
            # Multiple OSM ways may have the same NBI data 

    matches = []
    num_entries = len(way_inf)
    for entry in way_inf:
        dscore = float(entry['scores'][0])
        pscore = float(entry['scores'][1])
        
        # Currently, If we find any number of bridges besides 1, something wonky is going on.
        # 0 Bridges means OSM data is bad. 2+ bridges means we need to employ good heuristics.
        # These are some magic numbers and conditions. We should find a way to describe them.
        if num_entries == 1 and dscore >= 0.5:
            entry['selected'] = True
            matches.append(entry)
        elif num_entries == 2 and (dscore > 0.5 and pscore > 0.3):
            #TODO: For multiple bridges, create a method of checking if this bridge's scores are higher than others.
            # if true, add the bridge
            entry['selected'] = True
            matches.append(entry)
        elif (dscore > 0.5 and pscore > 0.3) or (pscore == 1) or (dscore >= 0.6): # 3+ bridges
            entry['selected'] = True
            matches.append(entry)

    if len(matches) > 0:
        # Update match info
        bridge.update({"osm-match":"True"})
        bridge.update({"osm-match-id": [i['way'].id for i in matches]})
        bridge.update({"osm-match-dsps": [i['scores'] for i in matches]})

    # visualize the nearby bridges and selected merge bridges
    folyzer.visualize_point(bridge, way_inf)

    count += 1
    if count == 100: break


print("Writing info to CSV...")
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
