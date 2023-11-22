import folium
from util import geo
from overpy import Way

class folyzer:
    '''A class that manages visualizing OSM and NBI data on real-world maps using folium. https://python-visualization.github.io/folium/latest/'''
    esri_attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    esri_tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

    label_attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    label_tiles = 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png'
    
    @classmethod
    def visualize_point(c, nbi_data:dict, osm_data:list[dict]) -> None:
        '''
        Visualizes an NBI point and its related NBI data using a Folium map, saved as an HTML file.
        
        Parameters
        -----
        nbi_data : dict
            A dictionary object containing all data for an NBI entry. 
            This is equivalent to an item in the list returned by util.nbiparser.modified_data()

        osm_scores : osm_scores
            A list containing dictionaries in the form:
                way : the overpy way
                
                scores : (distance-score, pattern-score)
                
                selected : bool
                
            Each entry represents a bridge way in OSM and its corresponding scores to the NBI entry

        Returns
        -----
        Returns nothing, but creates a folium map (HTML file) in out/folium/<good/bad>'''
        point = (nbi_data.get("lat"), nbi_data.get("lon"))
        
        # Use ESRI Imaging as the base map
        map = folium.Map(location = point, tiles=c.esri_tiles, attr=c.esri_attr, max_zoom=25, zoom_start = 18)

        # Add Carto Labels for understandability
        folium.TileLayer(tiles=c.label_tiles, attr=c.label_attr, overlay=True, opacity=1).add_to(map)

        num_matches = 0

        # Add our ways to the map in the form of PolyLine
        for entry in osm_data:
            pline = geo.make_polyline(entry['way'])
            
            color = "#FF0000" 
            if entry['selected'] == True:
                color = "#00FF00"
                num_matches += 1

            way : Way = entry['way']
            folium.PolyLine(pline,    
                            color=color,
                            weight=5,
                            popup=f"""OSM Bridge: w{way.id}  
                            name: {way.tags.get('name')}
                            dist-score: {entry['scores'][0]} 
                            patn-score: {entry['scores'][1]}""",
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

        map.save(f"out/folium/viz/fol{num_matches}-{len(osm_data)}-p{point}.html")
        
        return
