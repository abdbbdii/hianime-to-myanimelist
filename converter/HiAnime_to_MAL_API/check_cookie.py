import requests
from bs4 import BeautifulSoup

HIANIME_URL = "https://www.hianime.to/"

def is_valid(cookies) -> bool:
    soup = BeautifulSoup(requests.get(HIANIME_URL + f"/user/watch-list", cookies=cookies).content, "html.parser")
    print(soup.title.string)
    return soup.title.string != "HiAnime Free Anime Streaming Homepage"