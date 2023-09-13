import csv
import osmium
from util import nbiparser, nominatim
from datetime import datetime
from tqdm import tqdm
from osm_handlers import OSMNBIAnalyzerNom

# Prep Nominatim API
nom = nominatim("http://52.201.224.66:8080")

# We will write to a tags<TIME>.osm file
time = str(datetime.timestamp(datetime.now()))

# parse nbi data
nbi_file = "in/NE_NBI_FULL.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

ways = {}

count = 0
print("Reverse-geocoding NBI data using Nominatim...")
for bridge in tqdm(nbi_dat):
    bridge.update({"osm-match":"False"})
    bridge.update({"osm-match-id": "None"})


    response = nom.request({'format':'jsonv2',
            'lat':bridge['lat'],
            'lon':bridge['lon'],},
            'reverse')

    # print(response['osm_type'], response['osm_id'])
    ways.update({str(response['osm_id']): bridge})

# Create the PBF Handler and apply the desired OSM data for tag editing.
file_writer = OSMNBIAnalyzerNom(ways, nbi_dat[0].keys())

print("Writing NBI tags to OSM...")
file_writer.apply_file("in/nebraska-latest.osm.pbf")


    
# writing to csv file 
with open("out/NBI-Analysis-nmn.csv", 'w', newline='') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(nbi_dat[0].keys()) 
    
    for bridge in nbi_dat:
        # writing the data rows 
        csvwriter.writerow(list(bridge.values()))

print("Done!")