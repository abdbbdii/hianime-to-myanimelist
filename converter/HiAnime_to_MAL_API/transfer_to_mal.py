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


def transfer_to_mal(hi_list: list[dict], user_headers: dict, client_headers: dict):
    """
    Transfer HiAnime list to MAL list
    :param mal_list: list of anime to transfer
        - title: title of anime
        - status: status of anime
    :param headers: headers for MAL API
    """

    error_list = []

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
            import_to_mal(anime_id, anime["status"], user_headers)
        except Exception as e:
            error_list.append({"title": anime["title"], "reason": str(e)})
    return error_list

