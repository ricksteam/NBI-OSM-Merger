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
nbi_file = "NBI_HAWAII.csv"
c1 =  nbiparser(f"in/{nbi_file}")
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
            # dscore = heuristics.simple_distance(nbi_point['coord'], osm_point['coord'], t=20)
            dscore = heuristics.shortest_distance(geo.make_polyline(way), nbi_point['coord'], t=20)
            # pscore = heuristics.simple_pattern(nbi_point['name'], osm_point['name'])
            pscore = heuristics.sorensen_dice(nbi_point['name'], osm_point['name'])

            way_inf.append({'way': way, 'scores': ('%.3f'%dscore, '%.3f'%pscore), 'selected': False})
            
            # An OSM way can have AT MOST one NBI bridge 
            # Multiple OSM ways may have the same NBI data 

    matches = []
    num_entries = len(way_inf)
    all_avg = [((float(d) + float(p))/2) for d,p in [e['scores'] for e in way_inf]]
    for entry in way_inf:
        dscore = float(entry['scores'][0])
        pscore = float(entry['scores'][1])
        avg_score = (dscore + pscore) / 2

        # Currently, If we find any number of bridges besides 1, something wonky is going on.
        # 0 Bridges means OSM data is bad. 2+ bridges means we need to employ good heuristics.
        # These are some magic numbers and conditions. We should find a way to describe them.

        # 1 bridge
        if num_entries == 1 and dscore >= 0.5:
            entry['selected'] = True
            matches.append(entry)

        # For 2 bridges
        elif num_entries == 2 and (dscore > 0.5 and pscore > 0.3): 
            entry['selected'] = True
            matches.append(entry)

        # 3+ bridges
        elif (dscore > 0.5 and pscore > 0.3) or (pscore == 1): 
            entry['selected'] = True
            matches.append(entry)

        # If other multiple bridge cases fail, and if this entry has the largest average score, consider it a match
        elif avg_score == max(all_avg):
            entry['selected'] = True
            matches.append(entry)

        # If there is another way with the same name, we assume it's a double bridge and match it.
        # NOTE: This is iffy. It looks like it's matching bridges that aren't ACTUALLY the same.
        # TODO: Confirm this is unnessecary for double-way bridges
        # elif entry['way'].tags.get("name") != None and \
        #         [w['way'].tags.get('name') for w in way_inf].count(entry['way'].tags.get("name")) == 2:
        #     entry['selected'] = True
        #     matches.append(entry)


    if len(matches) > 0:
        # Update match info
        bridge.update({"osm-match":"True"})
        bridge.update({"osm-match-id": [i['way'].id for i in matches]})
        bridge.update({"osm-match-dsps": [i['scores'] for i in matches]})

    # visualize the nearby bridges and selected merge bridges
    folyzer.visualize_point(bridge, way_inf)

    count += 1
    # if count == 400: break


print("Writing info to CSV...")
# writing to csv file 
with open(f"out/{nbi_file}-Analysis.csv", 'w', newline='') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(nbi_dat[0].keys()) 
    
    # writing the data rows 
    for bridge in nbi_dat:
        csvwriter.writerow(list(bridge.values()))

print("Done!")
