import argparse
import asyncio
import os.path
from typing import List

import jsonpickle
from aiohttp import ClientSession

from type import MCMap
from tqdm import tqdm

globals()["root_url"] = "https://www.minecraftmaps.com"


async def download_map(session: ClientSession, map_url: str, map_name: str, no_skip: bool):
    if os.path.exists(f"./data/maps/{map_name}.zip") and not no_skip:
        return
    async with session.get(map_url, headers={"Referer": map_url}) as response:
        result = await response.read()
        with open(f"./data/maps/{map_name}.zip", "wb") as f:
            f.write(result)

async def download(metadata: List[MCMap], no_skip: bool):
    for i in tqdm(range(0, len(metadata), 5)):
        async with ClientSession() as session:
            await asyncio.gather(*[download_map(session, map.download_url, map.name, no_skip) for map in metadata[i:i+5]])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="./data/metadata.json")
    parser.add_argument("-n", "--no-skip", action="store_true", default=False)
    args = parser.parse_args()

    metadata: List[MCMap] = jsonpickle.decode(open(args.metadata, "r").read())
    os.makedirs("./data/maps", exist_ok=True)
    asyncio.run(download(metadata, args.no_skip))
