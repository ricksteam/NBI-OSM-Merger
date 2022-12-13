import csv
class nbiparser:
    def __init__(self):
        NBI_filtered_data = open('Updated_NBI_DATA_POC.csv', 'r')
        reader = csv.DictReader(NBI_filtered_data)
        self.myList = list(reader)
    def modified_data(self):
        final_list = []
        for ele in self.myList:
            final_list.append({"Bridgeid":ele["8 - Structure Number"].strip(),"latitude":ele["16 - Latitude (decimal)"],"longitude":ele["17 - Longitude (decimal)"]})
        return final_list

c1 =  nbiparser()
finalst =  c1.modified_data()
print(finalst)