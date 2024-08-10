import requests
from bs4 import BeautifulSoup

HIANIME_URL = "https://www.hianime.to/"

def is_valid(cookies) -> bool:
    soup = BeautifulSoup(requests.get(HIANIME_URL + f"/user/watch-list", cookies=cookies).content, "html.parser")
    return soup.title.string != "HiAnime Free Anime Streaming Homepage"


if __name__ == "__main__":
    print(is_valid({"connect.sid": "s%3AxxGGtFfXSHd17Z60TVgv2vYvHH3Ed8wj.p4IRlagurwQZb2T6w8gDIf5UJBKQ2Fs%2FGFnGSMrn4rk"}))