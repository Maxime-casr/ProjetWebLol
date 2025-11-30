from dataclasses import dataclass


@dataclass
class PopularItem:
    item: str
    percentage: float


@dataclass
class ChampionBuild:
    champion: str
    popular_items: list
