from dataclasses import dataclass

@dataclass
class MCMap:
    name: str
    download_url: str
    creator: str
    rating: str
    map_version: str
    mc_version: str
    date_added: str
    download_count: str
    description_md: str
    description_html: str