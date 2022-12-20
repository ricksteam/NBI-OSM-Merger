import csv
class nbiparser:
    def __init__(self, file):
        NBI_filtered_data = open(file, 'r')
        reader = csv.DictReader(NBI_filtered_data)
        self.myList = list(reader)
    def modified_data(self):
        final_list = []
        for ele in self.myList:
            final_list.append({"id":ele["8 - Structure Number"].strip(),"lat":ele["16 - Latitude (decimal)"],"lon":ele["17 - Longitude (decimal)"]})
        return final_list
        