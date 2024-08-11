# import requests

# error_list = {"watching": [], "on_hold": [], "plan_to_watch": [], "dropped": [], "completed": []}


# def populate_list(hi_list, headers):
#     mal_list = {}
#     for status, titles in hi_list.items():
#         for title in titles:
#             print(title, end=": ")
#             body = {"q": title, "limit": 1}
#             mal_anime_id = requests.get("https://api.myanimelist.net/v2/anime", headers=headers, params=body).json()["data"]
#             if not mal_anime_id:
#                 error_list[status].append(title)
#                 continue
#             mal_anime_id = mal_anime_id[0]["node"]["id"]
#             mal_list[mal_anime_id] = {
#                 "status": status,
#             }
#             print(mal_anime_id)
import aiohttp
import asyncio
from aiohttp import ClientSession

error_list = {"watching": [], "on_hold": [], "plan_to_watch": [], "dropped": [], "completed": []}
CONCURRENCY_LIMIT = 4

async def fetch_anime_id(semaphore, session: ClientSession, title: str, headers: dict):
    url = "https://api.myanimelist.net/v2/anime"
    params = {"q": title, "limit": 1}

    async with semaphore:
        try:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Failed to fetch {title}: {response.status}")
                    return None

                data = await response.json()
                mal_anime_id = data.get("data", [])

                if not mal_anime_id:
                    return None

                return mal_anime_id[0]["node"]["id"]

        except aiohttp.ClientError as e:
            print(f"Request error for {title}: {e}")
            return None

async def populate_list(hi_list, headers):
    mal_list = {}
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for status, titles in hi_list.items():
            for title in titles:
                tasks.append(fetch_anime_id(semaphore, session, title, headers))

        results = await asyncio.gather(*tasks)

        for (status, title), mal_anime_id in zip(((s, t) for s in hi_list for t in hi_list[s]), results):
            print(title, end=": ")
            if mal_anime_id:
                mal_list[mal_anime_id] = {"status": status}
                print(mal_anime_id)
            else:
                error_list[status].append(title)
                print("Not found")

    return {'mal_list': mal_list, 'error_list': error_list}

# Example usage
# hi_list = { "watching": ["Naruto", "One Piece"], "completed": ["Death Note"] }
# headers = { "Authorization": "Bearer YOUR_ACCESS_TOKEN" }
# asyncio.run(populate_list(hi_list, headers))
