from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Optional, Mapping, Tuple, Union, Callable, Any, MutableMapping
from mypy_extensions import VarArg
import os.path
import pickle
import re
from enum import Enum
from dataclasses import dataclass

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
    eq = 0
    ne = 1
    ge = 2
    gt = 3
    le = 4
    lt = 5
    contains = 6

    def apply(self, left: Union[List[Any], Any], right: Any) -> bool:
        if isinstance(right, list):
            return any([getattr(l, f"__{self.name}__")(right) for l in left])
        return getattr(left, f"__{self.name}__")(right)

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
        elif opstr == "in":
            return Operand.contains
        else:
            raise Exception(f"Operand {opstr} not supported")


def getattr_rec(obj: Any, attr_list: List[str]) -> Union[List[Any], Any]:
    attr = attr_list.pop(0)
    if isinstance(getattr(obj, attr), list):
        obj_elements = getattr(obj, attr)
        attr = attr_list.pop(0)
        return [getattr_rec(getattr(e, attr), attr_list) for e in obj_elements]
    return getattr_rec(getattr(obj, attr), attr_list)


class OperandAgg(Enum):
    MIN = 0
    MAX = 1

    def apply(self, players: List[Player], attr: List[str]) -> Player:
        return max(players, key=lambda p: getattr_rec(p, attr))

    @staticmethod
    def builder(opstr: str) -> OperandAgg:
        if opstr == "MAX":
            return OperandAgg.MAX
        elif opstr == "MIN":
            return OperandAgg.MIN
        else:
            raise Exception(f"Unknown operand: {opstr}")


class Rule:
    def __init__(self,
                 rule: Optional[Tuple[List[str], Operand, str]] = None,
                 agg: Optional[Tuple[List[str], OperandAgg]] = None):
        self._rule: List[Tuple[List[str], Operand, str]] = [rule] if rule else []
        self._agg: Optional[Tuple[List[str], OperandAgg]] = agg

    def __add__(self, other: Tuple[List[str], Operand, str]) -> Rule:
        self._rule.append(other)
        return self

    def __mul__(self, event: EventData) -> int:
        score = 0

        # Pre Aggregation
        if self._agg:
            event.Players = [self._agg[1].apply(event.Players, self._agg[0])]

        # Filtering
        for rule, op, value in self._rule:
            if op.apply(getattr_rec(event, rule), value):
                score += 1
            else:
                score = 0
        return score


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
        res = None
        for rule, track in self._rules.items():
            r_score = rule * event
            if r_score > score:
                res = track
                score = r_score
        return res


def get_sheet(cell_range):
    SPREADSHEET_ID = "1we_1P6c7dxkJ-x5ORuDBtQusOkrjMLmfgQdTJweNNgc"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=cell_range).execute()
    return result.get('values', [])


def _parse_section(rows) -> Rules:
    event = getattr(events, rows[0][0])
    rules: Rules = Rules()
    for row in rows:
        music = None
        rule = Rule((["event"], Operand.eq, event))
        for i, (cell1, cell2) in enumerate(zip(row[1:], row[2:])):
            rule += (cell1.split('=')[0].split('.'), Operand.eq, cell1.split('=')[1])
            if i+3 == len(row):
                music = cell2
        if not music:
            raise Exception(f"Music not found at line: {row}")
        rules += (rule, music)
    return rules


def parse_music(rows) -> Rules:
    sections = []
    current_section = []
    rules = Rules()
    for i, row in enumerate(rows):
        if any([v != '' for v in row]):
            current_section.append(row)
        if all([v == '' for v in row]) and current_section != [] or i+1 == len(rows):
            sections.append(current_section)
            current_section = []

    for section in sections:
        rules.extend(_parse_section(section))
    return rules


def parse_sfx(rows) -> Rules:
    sections = []
    current_section = []
    rules = Rules()
    for i, row in enumerate(rows):
        if any([v != '' for v in row]):
            current_section.append(row)
        if all([v == '' for v in row]) and current_section != [] or i+1 == len(rows):
            sections.append(current_section)
            current_section = []

    for section in sections:
        rules.extend(_parse_section(section))
    return rules
