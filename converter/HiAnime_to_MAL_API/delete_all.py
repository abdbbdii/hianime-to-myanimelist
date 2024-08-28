import requests


def delete_all(headers):
    ids = []
    i = 0
    while True:
        lis = requests.get(f"https://api.myanimelist.net/v2/users/@me/animelist", params={"offset": 10 * i}, headers=headers).json()["data"]
        if not lis:
            break
        ids.extend([i["node"]["id"] for i in lis])
        i += 1
    print(ids)
    for i in ids:
        print("Deleting", i)
        requests.delete(f"https://api.myanimelist.net/v2/anime/{i}/my_list_status", headers=headers)
    return "Deleted " + str(len(ids)) + " entries"
