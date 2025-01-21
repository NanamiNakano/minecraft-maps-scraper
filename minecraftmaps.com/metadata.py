import asyncio
import os
from typing import List

import bs4.element
import jsonpickle
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

from type import MCMap

globals()["root_url"] = "https://www.minecraftmaps.com"


def get_maps_tag() -> List[bs4.element.Tag]:
    root_url = globals()["root_url"]
    map_list_html = requests.get("https://www.minecraftmaps.com/creation").text
    next_map_list_soup = BeautifulSoup(map_list_html, "lxml")
    map_tags = next_map_list_soup.select("center > h2 > a")
    if __name__ == "__main__":
        print(f"Scraped {len(map_tags)} maps")

    current_url = root_url
    while next_map_list_soup.select_one("ul>li>a.next"):
        next_page_url = root_url + next_map_list_soup.select_one("ul>li>a.next")["href"]
        next_map_list_html = requests.get(next_page_url, headers={"Referer": current_url}).text
        next_map_list_soup = BeautifulSoup(next_map_list_html, "lxml")
        map_tags += next_map_list_soup.select("center > h2 > a")
        if __name__ == "__main__":
            print(f"Scraped {len(map_tags)} maps")
        current_url = next_page_url

    return map_tags


async def get_metadata(session: ClientSession, map_tag: bs4.element.Tag) -> MCMap:
    root_url = globals()["root_url"]
    async with session.get(root_url + map_tag["href"]) as response:
        map_soup = BeautifulSoup(await response.text(), "html5lib")

        name_tag = map_soup.select_one(".jd-item-page > h1:nth-child(2) > center:nth-child(1)")
        name = name_tag.text

        download_tag = map_soup.select_one("center > a.jdbutton")
        download_url = root_url + download_tag["href"]

        creator_tag = map_soup.select_one(
            ".stats_data > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > span:nth-child(1)")
        creator = creator_tag.text if creator_tag else ""

        rating_tag = map_soup.select_one(".jwajaxvote-star-rating li.current-rating")
        rating = rating_tag["style"].split(":")[1].split("%")[0] if rating_tag else ""

        map_version_tag = map_soup.select_one(
            ".stats_data > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2) > span:nth-child(1)")
        map_version = map_version_tag.text if map_version_tag else ""

        mc_version_tag = map_soup.select_one(
            ".stats_data > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2) > span:nth-child(1)")
        mc_version = mc_version_tag.text if mc_version_tag else ""

        date_added_tag = map_soup.select_one(
            ".stats_data > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2) > span:nth-child(1)")
        date_added = date_added_tag.text if date_added_tag else ""

        download_count_tag = map_soup.select_one(
            ".stats_data > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2) > span:nth-child(1)")
        download_count = download_count_tag.text if download_count_tag else ""

        description_tags = map_soup.select(
            ".map-download > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > p")
        md_strs = []
        html_strs = []
        for tag in description_tags:
            tag: bs4.element.Tag
            html_strs.append(str(tag))
            md_strs.append(md(str(tag)))
        description_md = "\n".join(md_strs)
        description_html = "\n".join(html_strs)

        mc_map = MCMap(name=name, download_url=download_url, creator=creator, rating=rating, map_version=map_version,
                       mc_version=mc_version, date_added=date_added, download_count=download_count,
                       description_md=description_md, description_html=description_html)
        return mc_map


async def scrape(map_tags: List[bs4.element.Tag]) -> List[MCMap]:
    results = []
    for i in tqdm(range(0, len(map_tags), 5)):
        async with ClientSession() as session:
            results.extend(await asyncio.gather(*[get_metadata(session, map_tag) for map_tag in map_tags[i:i + 5]]))
    return results


if __name__ == "__main__":
    print("Scraping map tags")
    tags = get_maps_tag()
    print("Scraping metadata")
    metadata = asyncio.run(scrape(tags))
    os.makedirs("./data", exist_ok=True)
    with open("./data/metadata.json", "w") as f:
        f.write(jsonpickle.encode(metadata))
