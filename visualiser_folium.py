import folium
from util import geo

class folyzer:
    esri_attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

    label_attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    label_tiles = 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png'
    
    @classmethod
    def visualize_point(c, nbi_data:list, osm_bridges:list):
        point = (nbi_data.get("lat"), nbi_data.get("lon"))
        # Use ESRI Imaging as the base map
        map = folium.Map(location = point, tiles=c.esri_tiles, attr=c.esri_attr, max_zoom=25, zoom_start = 18)

        # Add Carto Labels for understandability
        folium.TileLayer(tiles=c.label_tiles, attr=c.label_attr, overlay=True, opacity=1).add_to(map)

        # Add our ways to the map in the form of PolyLine
        for way in osm_bridges:
            pline = [[float(node.lat), float(node.lon)] for node in way.get_nodes(resolve_missing=True)]
            folium.PolyLine(pline,    
                            color="#FF0000",
                            weight=5,
                            popup=f"""OSM Bridge: w{way.id}  
                            name: {way.tags.get('name')}""",
                            ).add_to(map)
            
            # folium.Marker(geo.centroid(pline)).add_to(map)

        # Add NBI Marker to the map
        folium.Marker(point, 
                      popup=f"""NBI Bridge: {nbi_data.get("id-no")} 
                      coords: {nbi_data.get("lat")}, {nbi_data.get("lon")}
                      carried by: {nbi_data.get("carried-by")}
                      """
                      ).add_to(map)

        # Allow Layer Control
        folium.LayerControl().add_to(map)

        # Save the map as HTML file
        map.save(f"out/folium/bad/fol{point}.html")
        return
