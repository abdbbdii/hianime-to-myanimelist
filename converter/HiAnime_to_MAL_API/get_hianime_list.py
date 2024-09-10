import requests
from bs4 import BeautifulSoup

HIANIME_URL = "https://hianime.to"

statuses = {
    "watching": 1,
    "on_hold": 2,
    "plan_to_watch": 3,
    "dropped": 4,
    "completed": 5,
}


def get_list(cookies):
    with requests.Session() as s:
        hi_list: list[dict] = []
        for status, status_id in statuses.items():
            page = 1
            while True:
                soup = BeautifulSoup(s.get(HIANIME_URL + f"/user/watch-list", params=({"type": status_id, "page": page}), cookies=cookies).content, "html.parser")
                titles = soup.find_all("a", class_="dynamic-name")
                if not titles:
                    break
                for title in titles:
                    hi_list.append(
                        {
                            "title": title.text,
                            "status": status,
                        }
                    )
                page += 1

    return hi_list


# import aiohttp
# from bs4 import BeautifulSoup
# from typing import Dict, List

# HIANIME_URL = "https://hianime.to"

# statuses = {
#     "watching": 1,
#     "on_hold": 2,
#     "plan_to_watch": 3,
#     "dropped": 4,
#     "completed": 5,
# }

# async def get_list(cookies):
#     async with aiohttp.ClientSession(cookies=cookies) as session:
#         hi_list: Dict[str, List[str]] = {}
#         for status, query in statuses.items():
#             hi_list[status] = []
#             page = 1
#             while True:
#                 async with session.get(HIANIME_URL + "/user/watch-list", params={"type": query, "page": page}) as response:
#                     content = await response.text()
#                     soup = BeautifulSoup(content, "html.parser")
#                     titles = soup.find_all("a", class_="dynamic-name")
#                     if not titles:
#                         break
#                     for title in titles:
#                         hi_list[status].append(title.text)
#                     page += 1

#     return hi_list
