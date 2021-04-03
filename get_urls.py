
import os
import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime

directory = os.path.dirname(os.path.abspath(__file__))
search_tag_file_path = os.path.join(directory, "search_tags.txt")

def parse_tag_file():
    with open(search_tag_file_path) as file:
        return file.read().split("\n")

def get_base_search_page(tags):
    query = "+".join(tags)
    return f"https://nhentai.net/search/?q={query}&sort=popular"

def get_total_search_pages_from_base(base_search_page):
    res = requests.get(base_search_page)
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        last_url = soup.select("section a.last")[0]["href"]
        total_search_pages = re.search(r"^\/search\/\?q=.*&sort=popular&page=(.*)$", last_url).group(1)
    
        return int(total_search_pages)

    except Exception:
        return 0


def get_doujin_info_on_search_page(search_page_url):

    ret = []

    res = requests.get(search_page_url)
    soup = BeautifulSoup(res.text, "html.parser")

    gallery_links = soup.select("div.index-container div.gallery a")
    for gallery_link in gallery_links:
        doujin_url = f"https://nhentai.net{gallery_link['href']}"
        doujin_title = gallery_link.select("div.caption")[0].getText()
        ret.append(
            (doujin_url, doujin_title)
        )

    return ret


def get_doujin_info_from_tags(tags):
    base_search_page = get_base_search_page(tags)
    total_search_pages = get_total_search_pages_from_base(base_search_page)

    doujin_info = []
    if total_search_pages != 0:
        for page_num in range(1, total_search_pages + 1):
            doujin_info = doujin_info + get_doujin_info_on_search_page(
                f"{base_search_page}&page={page_num}"
            )
    
    doujin_info.sort(key=lambda info:info[1])

    return doujin_info

def write_doujin_info(tags, doujin_info):
    write_file_path = os.path.join(directory, "urls_out.txt")
    with open(write_file_path, "a+") as file:
        file.write(f"# TAGS: {' '.join(tags)} DATE: {datetime.today().strftime('%Y%m%d')}\n")
        for line in doujin_info:
            file.write(f"{line[0]} {line[1]}\n")

tags = parse_tag_file()
doujin_info = get_doujin_info_from_tags(tags)
write_doujin_info(tags, doujin_info)

