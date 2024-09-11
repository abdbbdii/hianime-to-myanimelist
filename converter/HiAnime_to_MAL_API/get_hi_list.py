from bs4 import BeautifulSoup
import requests
import re

HIANIME_URL = "https://hianime.to"

statuses = {
    "watching": 1,
    "on_hold": 2,
    "plan_to_watch": 3,
    "dropped": 4,
    "completed": 5,
}

def get_n_pages(cookies):
    with requests.Session() as s:
        hi_n_pages: dict = {}
        for status, status_id in statuses.items():
            soup = BeautifulSoup(s.get(HIANIME_URL + f"/user/watch-list", params=({"type": status_id, "page": 1}), cookies=cookies).content, "html.parser")
            last = soup.find("a", class_="page-link", title="Last")
            if last:
                hi_n_pages[status] = int(re.search(r"page=(\d+)", last.attrs.get("href")).group(1))
            else:
                hi_n_pages[status] = -1

    print(hi_n_pages)
    return hi_n_pages
