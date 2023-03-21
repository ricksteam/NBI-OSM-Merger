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
                "id":ele["8 - Structure Number"].strip(),
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
        