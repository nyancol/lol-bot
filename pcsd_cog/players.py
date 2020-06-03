from dataclasses import dataclass
from typing import List, Optional


FRIENDS = ["Br1seurDeReves", "Aramitz"]


@dataclass
class Spell:
    displayName: str
    rawDescription: str
    rawDisplayName: str


@dataclass
class Spells:
    summonerSpellOne: Spell
    summonerSpellTwo: Spell


@dataclass
class Scores:
    assists: int
    creepScore: int
    deaths: int
    kills: int
    wardScore: float


@dataclass
class RuneTree:
    displayName: str
    id: int
    rawDescription: str
    rawDisplayName: str


@dataclass
class Runes:
    keystone: RuneTree
    primaryRuneTree: RuneTree
    secondaryRuneTree: RuneTree


@dataclass
class Item:
    canUser: bool
    consumable: bool
    count: int
    displayName: str
    itemID: int
    price: int
    rawDescription: str
    rawDisplayName: str
    slot: int


@dataclass
class Player:
    championName: str
    isBot: bool
    isDead: bool
    items: List[Item]
    level: int
    position: str
    rawChampionName: str
    respawnTimer: float
    runes: Runes
    scores: Scores
    skinID: int
    summonerName: str
    summonerSpells: Spells
    team: str
    skinName: Optional[str] = None
    rawSkinName: Optional[str] = None
