import requests
from ..models import Cache

def get_mal_id(title: str, headers: dict) -> int:
    """
    Get MAL ID of anime
    :param title: title of anime
    :param headers: headers for MAL API
    :return: MAL ID of anime
    """

    body = {"q": title, "limit": 1}
    anime = requests.get("https://api.myanimelist.net/v2/anime", headers=headers, params=body).json().get("data")
    if not anime:
        return None
    return anime[0]["node"]["id"]


def import_to_mal(id: int, status: str, headers: dict):
    """
    Import anime to MAL
    :param id: MAL ID of anime
    :param status: status of anime
    :param headers: headers for MAL API
    """

    requests.put(f"https://api.myanimelist.net/v2/anime/{id}/my_list_status", headers=headers, data={"status": status})


def get_prev_list(headers: dict) -> list[dict]:
    """
    Get previous list of anime from MAL
    :param headers: headers for MAL API
    :return: previous list of anime
    """

    prev_list = []
    offset = 0
    while True:
        body = {"fields": "list_status", "limit": 1000, "offset": offset}
        anime_list = requests.get("https://api.myanimelist.net/v2/users/@me/animelist", headers=headers, params=body).json()
        if not anime_list.get("data"):
            break
        for anime in anime_list["data"]:
            prev_list.append({"id": anime["node"]["id"], "status": anime["list_status"]["status"]})
        offset += 1000
    return prev_list


def transfer_to_mal(hi_list: list[dict], prev_list: list[dict], user_headers: dict, client_headers: dict, request) -> list[dict]:
    """
    Transfer HiAnime list to MAL list
    :param mal_list: list of anime to transfer
        - title: title of anime
        - status: status of anime
    :param headers: headers for MAL API
    """

    error_list = []

    if prev_list is None:
        print("Getting previous list")
        prev_list = get_prev_list(user_headers)
        request.session["prev_list"] = prev_list


    for anime in hi_list:
        print(anime)
        try:
            entry = Cache.objects.filter(title=anime["title"])
            if entry.exists():
                anime_id = entry.first().anime_id
            else:
                anime_id = get_mal_id(anime["title"], client_headers)
                Cache.objects.create(anime_id=anime_id, title=anime["title"])
            if not anime_id:
                error_list.append({"title": anime["title"], "reason": "Anime not found on MAL"})
                continue
            for prev_anime in prev_list:
                if prev_anime["id"] == anime_id and prev_anime["status"] == anime["status"]:
                    print("Anime already in MAL")
                    error_list.append({"title": anime["title"], "reason": "Anime already in MAL"})
                    break
            else:
                import_to_mal(anime_id, anime["status"], user_headers)
        except Exception as e:
            error_list.append({"title": anime["title"], "reason": str(e)})
    return error_list

