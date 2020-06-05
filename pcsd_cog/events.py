from enum import Enum
import requests
from typing import List, Optional
from pcsd_cog.players import Player
from dataclasses import dataclass


class Event:
    pass


class EventActiveplayer(Event):
    pass


class EventConnected(Event):
    pass


class EventFriendConnected(Event):
    pass


class EventInvalid(Event):
    pass


class EventChampionSelect(Event):
    pass


class EventGameStats(Event):
    pass


class EventEndGameStats(Event):
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
