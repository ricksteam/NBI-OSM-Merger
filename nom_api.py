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
