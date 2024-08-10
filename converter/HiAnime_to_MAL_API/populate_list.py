# import requests

# error_list = {"watching": [], "on_hold": [], "plan_to_watch": [], "dropped": [], "completed": []}


# def populate_list(hi_list, headers):
#     mal_list = {}
#     for status, titles in hi_list.items():
#         for title in titles:
#             print(title)
#             body = {"q": title, "limit": 1}
#             mal_anime_id = requests.get("https://api.myanimelist.net/v2/anime", headers=headers, params=body).json()["data"]
#             if not mal_anime_id:
#                 error_list[status].append(title)
#                 continue
#             mal_anime_id = mal_anime_id[0]["node"]["id"]
#             mal_list[mal_anime_id] = {
#                 "status": status,
#             }

#     return {"mal_list": mal_list, "error_list": error_list}

import aiohttp
import asyncio
from aiohttp import ClientError, ClientTimeout

error_list = {"watching": [], "on_hold": [], "plan_to_watch": [], "dropped": [], "completed": []}

async def fetch_anime_id(session, url, headers, params, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, params=params, timeout=ClientTimeout(total=10)) as response:
                if response.status != 200:
                    print(f"Request failed with status {response.status} on attempt {attempt + 1}")
                    await asyncio.sleep(2 ** attempt)
                    continue

                json_response = await response.json()
                return json_response.get("data")
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"Exception occurred: {e} on attempt {attempt + 1}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

    print(f"Failed to fetch data after {retries} attempts")
    return None

async def populate_list(hi_list, headers):
    mal_list = {}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for status, titles in hi_list.items():
            for title in titles:
                url = "https://api.myanimelist.net/v2/anime"
                params = {"q": title, "limit": 1}
                print(f"Creating task for: {title}")
                tasks.append((status, title, fetch_anime_id(session, url, headers, params)))

        for status, title, task in tasks:
            mal_anime_id = await task
            if not mal_anime_id:
                error_list[status].append(title)
            else:
                mal_anime_id = mal_anime_id[0]["node"]["id"]
                mal_list[mal_anime_id] = {
                    "status": status,
                }
            print(f"Processed title: {title}")

    print("All tasks completed")
    return {"mal_list": mal_list, "error_list": error_list}
