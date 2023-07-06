import overpy

api = overpy.Overpass(url="http://52.201.224.66:12345/api/interpreter")

result = api.query("""
    nwr(41.319, -96.045, 41.323, -96.04);

    out;
    """)

for way in result.ways:
    print("Name: %s" % way.tags.get("name"))
    print("  Highway: %s" % way.tags.get("highway"))
    print("  Bridge: %s" % way.tags.get("bridge"))
    print("  Nodes:")
    for node in way.get_nodes(resolve_missing=True):
        print("    Lat: %f, Lon: %f" % (node.lat, node.lon))