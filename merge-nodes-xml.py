from util import nbiparser
import xml.etree.ElementTree as et

def addTag(parent, key, value):
    et.SubElement(parent, 'tag', attrib={'k':key, 'v':value})

def addNBInode(parent : et.Element, nbi_info, nid):
    # Create the node
    node = et.Element('node', attrib={'id':str(nid), 'visible':"true", 'version':'1', 'lat':nbi_info['lat'], 'lon':nbi_info['lon'] })
    # add NBI tags to the node
    addTag(node, 'nbi', nbi_info['id-no'])
    addTag(node, 'nbi:super-cond', nbi_info['super-cond'])
    addTag(node, 'nbi:sub-cond', nbi_info['sub-cond'])
    addTag(node, 'nbi:op-rating', nbi_info['op-rating'])

    # Insert the node into the tree
    parent.insert(1, node)


# parse nbi data
nbi_file = "in/NE_NBI_DATA.csv"
c1 =  nbiparser(nbi_file)
nbi_dat =  c1.modified_data()

tree = et.parse("in/area-original.osm")
# Due to the xml structure, the root IS the osm item.
root = tree.getroot()


for i, bridge in enumerate(nbi_dat):
    # Add the bridge data in a new NBI node.
    # This functions fine, but we mey need to do id validation for larger sets.
    addNBInode(root, bridge, i+1)


et.indent(tree, '  ')

tree.write('out/area-merged-nodes.osm', encoding="utf-8", xml_declaration=True)
