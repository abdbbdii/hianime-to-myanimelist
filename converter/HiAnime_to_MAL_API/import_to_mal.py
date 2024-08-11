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
        trasnfers = await asyncio.gather(*tasks)
        # print(transfers)
        for transfer in trasnfers:
            if transfer.status == 200:
                print(f"Successfully transferred {transfer.url}")
            else:
                print(f"Failed to transfer {transfer.url}: {transfer.status}")