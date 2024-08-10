# import requests

# def to_mal(mal_list, headers):
#     for id, anime in mal_list.items():
#         requests.put(f"https://api.myanimelist.net/v2/anime/{id}/my_list_status", headers=headers, data=anime)

import aiohttp
import asyncio

async def to_mal(mal_list, headers):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id, anime in mal_list.items():
            url = f"https://api.myanimelist.net/v2/anime/{id}/my_list_status"
            task = asyncio.create_task(session.put(url, headers=headers, data=anime))
            tasks.append(task)
        await asyncio.gather(*tasks)