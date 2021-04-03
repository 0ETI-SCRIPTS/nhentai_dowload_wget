import sys
import os
import re
import requests
import subprocess
from bs4 import BeautifulSoup

directory = os.path.dirname(
    os.path.abspath(__file__)
)

def parse_url_file():
    file_path = os.path.join(directory, "urls.txt")
    
    with open(file_path) as file:
        urls = file.read().split("\n")

        return urls

def get_doujin_info(url):
    res1 = requests.get(url)
    soup1 = BeautifulSoup(res1.text, "html.parser")

    doujin_title = soup1.find("h1").text
    doujin_pages = soup1.findAll("span", attrs = {"class": "name"})[-1].text
    doujin_number = re.search(r"^https://nhentai.net/g/(.*)/$", url).group(1)

    # res2 = requests.get(f"https://nhentai.net/g/{doujin_number}/1/")
    # soup2 = BeautifulSoup(res2.text)
    # gallery_url = soup2.find("section", attrs = {"id": "image-container"}).a.img["src"]
    # gallery_number = re.search(r"^https://i.nhentai.net/galleries/(.*)/1.jpg$")

    return doujin_title, doujin_pages, doujin_number

def download_page(doujin_number, page_num):
    res = requests.get(f"https://nhentai.net/g/{doujin_number}/{page_num}/")
    soup =  BeautifulSoup(res.text, "html.parser")

    image_url = soup.find("section", attrs = {"id": "image-container"}).a.img["src"]
    
    subprocess.run(["wget", image_url])

def download_doujin(url):
    doujin_title, doujin_pages, doujin_number = get_doujin_info(url)

    download_dest = os.path.join(directory, "downloads", doujin_title.replace("/", "-"))
    
    if os.path.isdir(download_dest):
        return
    else:
        os.mkdir(download_dest)
        os.chdir(download_dest)

    for i in range(1, int(doujin_pages) + 1):
        download_page(doujin_number, i)


lines = parse_url_file()

for line in lines:
    if line.startswith("#") or line == "" or line.isspace():
        continue

    download_doujin(line.split(" ")[0])