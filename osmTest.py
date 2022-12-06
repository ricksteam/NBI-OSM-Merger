import pandas
import osmium

class TestHandler(osmium.SimpleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.num_nodes = 0
        self.bridges = []

    def is_bridge(self, tags):
        return tags.get('bridge') == 'yes'

    def node(self, n):
        if self.is_bridge(n.tags):
            self.num_nodes += 1
            self.bridges.append(n.tags['highway'])

    def way(self, w):
        if self.is_bridge(w.tags):
            self.num_nodes += 1
            self.bridges.append(w.tags['highway'])
        
    def relation(self, r):
        if self.is_bridge(r.tags):
            self.num_nodes += 1
            self.bridges.append(r.tags['highway'])
        

# TEST RUN
h = TestHandler()

h.apply_file("sample.osm")

print("Number of bridge nodes: %d" % h.num_nodes)

print(h.bridges)

filename = "Updated_NBI_DATA_POC.csv"
csv = pandas.read_csv(filename)

print("Non-footway bridges in OSM: %d" % (len(h.bridges) - h.bridges.count('footway')))
print("Bridges in NBI: %d" % len(csv))

exit(0)