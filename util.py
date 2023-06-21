import csv

class nbiparser:
    def __init__(self, file):
        NBI_filtered_data = open(file, 'r')
        reader = csv.DictReader(NBI_filtered_data)
        self.myList = list(reader)
    def modified_data(self):
        final_list = []
        for ele in self.myList:
            final_list.append({
                "id-state":ele["1 - State Code"],
                "id-no":ele["8 - Structure Number"].strip(),
                "id-owner":ele["22 - Owner Agency"].strip("'"),
                "lat":ele["16 - Latitude (decimal)"],
                "lon":ele["17 - Longitude (decimal)"],
                "deck-rating":ele["58 - Deck Condition Rating"].strip("'"),
                "super-cond":ele["59 - Superstructure Condition Rating"].strip("'"),
                "sub-cond":ele["60 - Substructure Condition Rating"].strip("'"),
                "culvert-rating":ele["62 - Culverts Condition Rating"].strip("'"),
                "op-method-code":ele["63 - Operating Rating Method Code"].strip("'"),
                "op-rating":ele["64 - Operating Rating (US tons)"],
                "inv-rating":ele["66 - Inventory Rating (US tons)"],
                })
        return final_list
        
import requests

class nominatim:
    def __init__(self, address="https://nominatim.openstreetmap.org") -> None:
        self.address = address
        
    def request(self, parameters:dict, endpoint:str) -> str:
        url = self.address
        url += "/" + endpoint

        if len(parameters.keys()) != 0:
            url += "?"
            for k,v in parameters.items():
                url += f"{k}={v}&"
                # print(k,v)
        
        response = requests.request("GET", url)
        return response.json()

# Example usage
# n = nominatim("http://52.201.224.66:8080")
# response = n.request({'format':'jsonv2',
#             'lat':"41.3154",
#             'lon':"-96.0524",},
#             'reverse')
# print(response)