import requests
import json

def get_MAL(headers, username, offset_inc) -> dict:
    data = {}
    j = 0
    while True:
        print(f"Getting MAL data for offset {offset_inc*j}")
        response = requests.get(f"https://api.myanimelist.net/v2/users/{username}/animelist", params={"fields":"list_status","limit":offset_inc, "offset": offset_inc*j}, headers=headers).json()
        if not response.get("data"):
            break
        for i in range(len(response["data"])):
            if not response["data"][i]["list_status"]["status"] in data:
                data[response["data"][i]["list_status"]["status"]] = []
            data[response["data"][i]["list_status"]["status"]].append(response["data"][i]["node"])
        j += 1

    return data