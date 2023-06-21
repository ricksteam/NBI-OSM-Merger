import osmium
import numpy as np

class OSMBridgeCounter(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.total = 0
        self.footway = 0

    def way(self, w):
        if w.tags.get('bridge') == 'yes':
            self.total += 1
            if w.tags.get('highway') == 'footway':
                self.footway += 1

class OSMParser(osmium.SimpleHandler):
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
            # print(mid_lat,mid_lon)

            clean.append({'id':id, 'lat': round(mid_lat, 4), 'lon': round(mid_lon, 4)})
        
        return clean

class OSMNBIMerger(osmium.SimpleHandler):
    def __init__(self, writer, ways, debug=False) -> None:
        super().__init__()
        self.writer = writer
        self.ways = ways
        self.debug = debug # If True, OSM and matching values will be logged for each entry.
        if self.debug:
            self.log = open('out/osm_log', 'w')

    def is_bridge(self, tags):
        return tags.get('bridge') == 'yes' and tags.get('highway') != 'footway'

    def way(self, w):
        id = str(w.id)
        if self.debug:
            self.log.write(f'{w.tags.get("bridge")=="yes"}, {w.tags.get("highway")!="footway"}, {id in list(self.ways.keys())}\n')
        # if self.is_bridge(w.tags) and id in list(self.ways.keys()):
       
        # For now, we are ignoring bridge labels so we can assign more data.
        # if w.tags.get('bridge') == 'yes' \
        if w.tags.get('highway') != 'footway' \
            and id in list(self.ways.keys()):
            # print(id)
            new_tags = {
                                'nbi:id':str(self.ways[id]['id-state']+","+self.ways[id]['id-no']+","+self.ways[id]['id-owner']),
                                'nbi:super-cond':self.ways[id]['super-cond'],
                                'nbi:sub-cond':self.ways[id]['sub-cond'],
                                'nbi:op-rating':self.ways[id]['op-rating'],
                                'nbi:op-method-code':self.ways[id]['op-method-code'],
                                'nbi:deck-rating':self.ways[id]['deck-rating'],
                                'nbi:inv-rating':self.ways[id]['inv-rating'],
                                }
            orig_tags = dict(w.tags)
            all_tags = orig_tags | new_tags     
            new = w.replace(tags=all_tags, version=w.version+1)
            self.writer.add_way(new)
        else:
            self.writer.add_way(w)
    
    def node(self, n):
        self.writer.add_node(n)

    def relation(self, r):
        self.writer.add_relation(r)

    def close(self):
        if self.debug:
            self.log.close()
