from enum import Enum
import requests
from typing import List, Optional, Mapping
from pcsd_cog.players import Player
from dataclasses import dataclass


class Rule:
    def __init__(self, rule):
        self._rule: Mapping[str, str] = rule

    def __equal__(self, other: Mapping[str, str]):
        return self._rule.items() <= other.items()

    def __repr__(self):
        return str(self._rule)

    def distance(self, rule):
        score = 0
        for k, v in {k: v for k, v in rule._rule.items() if k in self._rule}.items():
            if self._rule[k] == v:
                score += 1
            else:
                return 0
        return score


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

    def to_rule(self, players: List[Player]) -> Rule:
        raise NotImplementedError


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

    def to_rule(self, players: Mapping[str, Player]) -> Rule:
        rule = {"team": players[self.VictimName].team}
        rule["championVictim"] = players[self.VictimName].championName
        if players[self.VictimName].position:
            rule["killerPosition"] = players[self.VictimName].position
        if self.KillerName in players and players[self.KillerName].position:
            rule["victimPosition"] = players[self.VictimName].position
        if any([self.KillerName.startswith(e) for e in ["Minion_", "Turret_", "Dragon", "Herald_", "Baron_", "SRU_Baron"]]):
            rule["killer"] = self.KillerName.split('_')[0]
        else:
            rule["championKiller"] = players[self.KillerName].championName
        return Rule(rule)

@dataclass
class EventMultikill(EventData):
    KillerName: str
    KillStreak: int


@dataclass
class EventInhibRespawned(EventData):
    pass

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
