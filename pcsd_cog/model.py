from __future__ import annotations

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Optional, Mapping, Tuple, Union, Callable, Any, MutableMapping, Iterable
from mypy_extensions import VarArg, Arg
import os.path
import pickle
import re
from enum import Enum
from dataclasses import dataclass
import random


from pcsd_cog import events
from pcsd_cog.events import Event, EventData
from pcsd_cog.players import Player


@dataclass
class Music:
    name: str
    priority: int

    def __le__(self, other: Music) -> bool:
        return self.priority <= other.priority
    def __lt__(self, other: Music) -> bool:
        return self.priority < other.priority
    def __gt__(self, other: Music) -> bool:
        return self.priority > other.priority
    def __ge__(self, other: Music) -> bool:
        return self.priority >= other.priority


class Operand(Enum):
    eq = (lambda l, r: l == r,)
    ne = (lambda l, r: l != r,)
    ge = (lambda l, r: l >= r,)
    gt = (lambda l, r: l > r,)
    le = (lambda l, r: l <= r,)
    lt = (lambda l, r: l < r,)
    like = (lambda l, r: re.match(r, l) is not None,)
    contains = (lambda l, r: l in r,)

    def __init__(self, f):
        self._value_ = f

    def __call__(self, left: Union[List[Any], Any], right: Any) -> bool:
        if isinstance(left, list):
            return any([self.value(l, right) for l in left])
        return self.value(left, right)

    @staticmethod
    def builder(opstr) -> Operand:
        if opstr == "==":
            return Operand.eq
        elif opstr == "!=":
            return Operand.ne
        elif opstr == "!=":
            return Operand.ne
        elif opstr == ">=":
            return Operand.ge
        elif opstr == ">":
            return Operand.gt
        elif opstr == "<=":
            return Operand.le
        elif opstr == "<":
            return Operand.lt
        elif opstr.lower() == "in":
            return Operand.contains
        elif opstr.lower() == "like":
            return Operand.like
        else:
            raise Exception(f"Operand {opstr} not supported")


def getattr_rec(obj: Any, attr_list: List[str]) -> Union[List[Any], Any]:
    if not attr_list:
        return obj

    attr: str = attr_list.pop(0)
    count_re = r"COUNT\((.+)\)"
    match = re.match(count_re, attr)
    if match:
        attr = match.groups()[0]
        return len(getattr(obj, attr))
    elif isinstance(getattr(obj, attr), list):
        obj_elements = getattr(obj, attr)
        return [getattr_rec(e, attr_list) for e in obj_elements]
    return getattr_rec(getattr(obj, attr), attr_list)


class OperandAgg(Enum):
    MIN = (lambda players, key: max(players, key=key),)
    MAX = (lambda players, key: min(players, key=key),)

    def __init__(self, f):
        self._value_ = f

    def __call__(self, players: Iterable[Player], attr: List[str]) -> Player:
        return self.value(players, lambda p: getattr_rec(p, attr[:]))

    @staticmethod
    def builder(opstr: str) -> OperandAgg:
        if opstr == "MAX":
            return OperandAgg.MAX
        elif opstr == "MIN":
            return OperandAgg.MIN
        else:
            raise Exception(f"Unknown operand: {opstr}")


class Rule:
    def __init__(self, agg: Optional[Tuple[List[str], OperandAgg]] = None):
        self._agg: Optional[Tuple[List[str], OperandAgg]] = agg if agg else None
        self._rule: List[Tuple[List[str], Operand, str]] = []

    def __add__(self, other: Tuple[List[str], Operand, str]) -> Rule:
        self._rule.append(other)
        return self

    def __mul__(self, event: EventData) -> int:
        score = -1

        # Pre Aggregation
        if self._agg:
            assert self._agg[0][0] == "Players"
            event.Players = [self._agg[1](event.Players, self._agg[0][1:][:])]

        # Filtering
        for rule, op, value in self._rule:
            # print(f"Rule {rule}, {op}, {value}, {event}")
            try:
                if op(getattr_rec(event, rule[:]), value):
                    score = score + 1 if score > -1 else 1
                else:
                    return -1
            except AttributeError as exc:
                return -1
        return score

    def __repr__(self):
        return (self._rule.__repr__(), self._agg.__repr__()).__repr__()


class Rules:
    def __init__(self):
        self._rules: MutableMapping[Rule, Union[str, Music]] = dict()

    def __add__(self, other: Tuple[Rule, Union[str, Music]]) -> Rules:
        self._rules[other[0]] = other[1]
        return self

    def extend(self, other: Rules) -> None:
        self._rules.update(other._rules)

    def match(self, event: EventData) -> Optional[Union[str, Music]]:
        score = 0
        res: List[Tuple[Rule, Union[str, Music]]] = []
        for rule, track in self._rules.items():
            r_score = rule * event
            if r_score > score:
                res = [(rule, track)]
                score = r_score
            elif r_score == score:
                res.append((rule, track))
        if res:
            random.shuffle(res)
            rule = res[0][0]
            track = res[0][1]
            if isinstance(track, Music):
                del self._rules[rule]
            return track
        return None

    def __repr__(self):
        return self._rules.__repr__()

def gauth():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_sheet(cell_range):
    SPREADSHEET_ID = "1we_1P6c7dxkJ-x5ORuDBtQusOkrjMLmfgQdTJweNNgc"
    service = build('sheets', 'v4', credentials=gauth())
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=cell_range).execute()
    return result.get('values', [])


def parse_sfx(cell_range) -> Rules:
    rows = get_sheet(cell_range)
    rules = Rules()
    rules_width = 5
    link_index = 7

    for i, row in enumerate([row for row in rows if row]):
        rule = Rule()
        for cell in [c for c in row[:rules_width] if c]:
            elements = cell.split(' ')
            value = elements[2]
            try:
                value = int(value)
            except:
                pass
            rule += (elements[0].split('.'), Operand.builder(elements[1]), value)
        rules += (rule, row[link_index])
    return rules


def parse_music(cell_range) -> Rules:
    rows = get_sheet(cell_range)
    rules = Rules()
    rules_width = 5
    agg_index, link_index, priority_index = 6, 7, 8

    agg_values = '|'.join([f"({agg.name})" for agg in OperandAgg])
    agg_re = rf"({agg_values})\((.+)\)"

    for i, row in enumerate([row for row in rows if row]):
        match = re.match(agg_re, row[agg_index])
        if match:
            elements = match.groups()
            rule = Rule((elements[3].split('.'), OperandAgg.builder(elements[0])))
        else:
            rule = Rule()
        for cell in [c for c in row[:rules_width] if c]:
            elements = cell.split(' ')
            value = elements[2]
            try:
                value = int(value)
            except:
                pass
            rule += (elements[0].split('.'), Operand.builder(elements[1]), value)
        rules += (rule, Music(row[link_index], int(row[priority_index])))
    return rules
