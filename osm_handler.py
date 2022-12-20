import osmium
import numpy as np

class OSMHandler(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.loops = 0
        self.ways = {}
        self.nodes = {}
        self.values = None

    def is_bridge(self, tags):
        return tags.get('bridge') == 'yes' and tags.get('highway') != 'footway'


    def way(self, w):
        # If not on our first iteration, leave
        if self.loops != 0:
            return

        # If we have a bridge, store its referenced node in the ways.
        if self.is_bridge(w.tags):
            self.ways[w.id] = [node.ref for node in w.nodes]


    def node(self, n):
        # if not on our second iteration, leave
        if self.loops != 1:
            return
        
        # get our node id and check if it is referenced.
        ref = n.id
        x = np.where(self.values == ref)
        # If the node is referenced, save its lat and long
        if x[0].size != 0 or x[1].size != 0: 
            self.nodes[ref] = {'lat': n.location.lat, 'lon': n.location.lon}

    def parse(self, file):
        # Iteration 1: collect bridge ways
        self.apply_file(file)
        self.values = np.array(list(self.ways.values()))
        self.loops += 1

        # Iteration 2: collect referenced node lat/lon
        self.apply_file(file)

    def clean(self):
        lats = []
        lons = []
        clean = []
        for id, nodes in self.ways.items():
            for node in nodes:
                lats.append(float(self.nodes[node]['lat']))
                lons.append(float(self.nodes[node]['lon']))
            mid_lat = np.average(lats)
            mid_lon = np.average(lons)
            print(mid_lat,mid_lon)

            clean.append({'id':id, 'lat': round(mid_lat, 4), 'lon': round(mid_lon, 4)})
        
        return clean

