from enum import Enum
from typing import List, Optional, Mapping
from pcsd_cog.players import Player
import dataclasses
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
    Players: List[Player]
    EventName: str
    EventID: int
    EventTime: float


class EventGameStart(EventData):
    pass


@dataclass
class EventAce(EventData):
    Acer: str
    AcingTeam: str

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "Acer." + attr, getattr(players[self.Acer], attr))


@dataclass
class EventFirstBlood(EventData):
    Recipient: str

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "Recipient." + attr, getattr(players[self.Recipient], attr))


@dataclass
class EventFirstBrick(EventData):
    KillerName: str

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))


class EventMinionsSpawning(EventData):
    pass


@dataclass
class EventTurretKilled(EventData):
    TurretKilled: str
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])


@dataclass
class EventDragonKill(EventData):
    DragonType: str
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])

@dataclass
class EventBaronKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])


@dataclass
class EventHeraldKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])

@dataclass
class EventChampionKill(EventData):
    VictimName: str
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "VictimName." + attr, getattr(players[self.VictimName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])


@dataclass
class EventMultikill(EventData):
    KillerName: str
    KillStreak: int

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))


@dataclass
class EventInhibRespawned(EventData):
    pass


@dataclass
class EventInhibKilled(EventData):
    InhibKilled: str
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = self.Players
        for attr in Player.__annotations__:
            setattr(self, "KillerName." + attr, getattr(players[self.KillerName], attr))
            setattr(self, "Assisters." + attr, [getattr(players[a], attr) for a in self.Assisters])


@dataclass
class EventInhibRespawningSoon(EventData):
    pass


@dataclass
class EventGameEnd(EventData):
    Result: str


class EventIdle(EventData):
    pass
