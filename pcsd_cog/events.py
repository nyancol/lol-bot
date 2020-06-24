from enum import Enum
from typing import List, Optional, Mapping, Union
from pcsd_cog.players import Player
import dataclasses
from dataclasses import dataclass, make_dataclass



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

    def __post_init__(self):
        self.Champion = make_dataclass("Champion", [(p.championName, Player) for p in self.Players])(**{p.championName: p for p in self.Players})
        self.Summoner = make_dataclass("Summoner", [(p.summonerName, Player) for p in self.Players])(**{p.summonerName: p for p in self.Players})


class EventGameStart(EventData):
    pass


@dataclass
class EventAce(EventData):
    Acer: str
    AcingTeam: str

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Acer = players[self.Acer]


@dataclass
class EventFirstBlood(EventData):
    Recipient: str

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Recipient = self.Players[self.Recipient]


@dataclass
class EventFirstBrick(EventData):
    KillerName: str

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]


class EventMinionsSpawning(EventData):
    pass


@dataclass
class EventTurretKilled(EventData):
    TurretKilled: str
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]


@dataclass
class EventDragonKill(EventData):
    DragonType: str
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        players = {p.summonerName: p for p in self.Players}
        super().__post_init__()
        self.Killer = players[self.KillerName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]

@dataclass
class EventBaronKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]


@dataclass
class EventHeraldKill(EventData):
    Stolen: bool
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]


@dataclass
class EventChampionKill(EventData):
    VictimName: str
    KillerName: str
    Assisters: List[Union[str, Player]]
    Killer: Optional[Player] = None
    Victim: Optional[Player] = None

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]
        self.Victim = players[self.VictimName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]


@dataclass
class EventMultikill(EventData):
    KillerName: str
    KillStreak: int

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]


@dataclass
class EventInhibRespawned(EventData):
    pass


@dataclass
class EventInhibKilled(EventData):
    InhibKilled: str
    KillerName: str
    Assisters: List[str]

    def __post_init__(self):
        super().__post_init__()
        players = {p.summonerName: p for p in self.Players}
        self.Killer = players[self.KillerName]
        self.Assisters = [player for name, player in players.items() if name in self.Assisters]


@dataclass
class EventInhibRespawningSoon(EventData):
    pass


@dataclass
class EventGameEnd(EventData):
    Result: str


class EventIdle(EventData):
    pass
