from enum import Enum
from typing import List
from dataclasses import dataclass


class EventID(Enum):
    GameStart = 0
    MinionsSpawning = 1
    FirstBrick = 2
    TurretKilled = 3
    InhibKilled = 4
    DragonKill = 5
    HeraldKill = 6
    BaronKill = 7
    ChampionKill = 8
    Multikill = 9
    Ace = 10


class Event():
    pass

@dataclass
class EventData(Event):
    EventID: int
    EventName: str
    EventTime: float


class EventGameStart(EventData):
    pass


@dataclass
class EventAce(EventData):
    Acer: str
    AcingTeam: str


@dataclass
class EventFirstBlood(EventData):
    Recipient: str


@dataclass
class EventFirstBrick(EventData):
    KillerName: str

class EventMinionsSpawning(EventData):
    pass

@dataclass
class EventTurretKilled(EventData):
    TurretKilled: str
    KillerName: str
    Assisters: List[str]


@dataclass
class EventDragonKill(EventData):
    DragonType: str
    Stolen: bool
    KillerName: str
    Assisters: List[str]


@dataclass
class EventBaronKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]


@dataclass
class EventHeraldKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]


@dataclass
class EventChampionKill(EventData):
    VictimName: str
    KillerName: str
    Assisters: List[str]


@dataclass
class EventMultikill(EventData):
    KillerName: str
    KillStreak: int


@dataclass
class EventInhibKilled(EventData):
    InhibKilled: str
    KillerName: str
    Assisters: List[str]


@dataclass
class EventInhibRespawningSoon(EventData):
    pass

@dataclass
class EventGameEnd(EventData):
    Result: str
