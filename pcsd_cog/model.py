from __future__ import annotations

from traceback import format_exc
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import List, Optional, Mapping, Tuple, Union, Callable, Any, MutableMapping, Iterable
# from mypy_extensions import VarArg, Arg
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


def getattr_rec(obj: Any, attr_list: List[str]) -> Union[List[Any], Any]:
    if not attr_list:
        return obj

    attr_list = attr_list[:]
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


class AggOperand(Enum):
    MAX = (max,)
    MIN = (min,)
    COUNT = (len,)

    def __init__(self, f):
        self._value_ = f

    def __call__(self, l, **args):
        return self.value(l, **args)


class Expression:
    def __init__(self, exp):
        self.attr: Any = exp
        regex_agg = r"(MAX|MIN|COUNT|max|min|count)\((.+)\)(.*)"
        match_agg = re.match(regex_agg, exp)
        self.agg_op: Optional[AggOperand] = None
        self.remaining: Optional[List[str]] = None

        match = re.match(regex_agg, exp)
        if match:
            self.agg_op = AggOperand[match.group(1).upper()]
            self.attr = match.group(2).split('.')
            assert self.attr != [], self.attr
            if match.group(3):
                self.remaining = [e for e in match.group(3).split('.') if e]
        else:
            path_regex = r"(\w+\.)+\w+"
            match_path = re.match(path_regex, self.attr)
            if match_path:
                self.attr = self.attr.split('.')
                assert self.attr != [], self.attr
            else:
                try:
                    self.attr = int(self.attr)
                except ValueError:
                    pass

    def resolve(self, obj) -> Any:
        value: Any = self.attr
        if isinstance(self.attr, list) and self.agg_op is None:
            value = getattr_rec(obj, self.attr)
        elif self.agg_op and self.remaining is None:
            value = self.agg_op(getattr_rec(obj, self.attr))
        elif self.agg_op and self.remaining:
            list_values = getattr(obj, self.attr[:].pop(0))
            agg_attr = self.agg_op(list_values, key=lambda v: getattr_rec(v, self.attr[1:][:]))
            value = getattr_rec(agg_attr, self.remaining)
        elif isinstance(self.attr, str):
            try:
                value = getattr(obj, self.attr)
            except AttributeError:
                # print(f"No resolution possible for {self.attr} with {obj}")
                pass
        return value


class Predicate(Enum):
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

    def __call__(self, left: Any, right: Any) -> bool:
        return self.value(left, right)

    @staticmethod
    def builder(opstr) -> Predicate:
        if opstr == "==":
            return Predicate.eq
        elif opstr == "!=":
            return Predicate.ne
        elif opstr == "!=":
            return Predicate.ne
        elif opstr == ">=":
            return Predicate.ge
        elif opstr == ">":
            return Predicate.gt
        elif opstr == "<=":
            return Predicate.le
        elif opstr == "<":
            return Predicate.lt
        elif opstr.lower() == "in":
            return Predicate.contains
        elif opstr.lower() == "like":
            return Predicate.like
        else:
            raise Exception(f"Predicate {opstr} not supported")


class Rule:
    def __init__(self):
        self._rule: List[Tuple[Expression, Predicate, Expression]] = []

    def __add__(self, cell: str) -> Rule:
        elements = cell.split(' ')
        l_exp, pred, r_exp = (Expression(elements[0]),
                              Predicate.builder(elements[1]),
                              Expression(elements[2]))
        self._rule.append((l_exp, pred, r_exp))
        return self

    @staticmethod
    def _match(rule: Tuple[Expression, Predicate, Expression], event: EventData) -> bool:
        try:
            l_value = rule[0].resolve(event)
            r_value = rule[2].resolve(event)
            if isinstance(l_value, list) and not isinstance(r_value, list):
                return any([rule[1](l, r_value) for l in l_value])
            elif not isinstance(l_value, list) and isinstance(r_value, list):
                return any([rule[1](l_value, r) for r in r_value])
            else:
                return rule[1](l_value, r_value)
        except AttributeError as exc:
            # print(f"Matching error: {exc} - {format_exc()}")
            return False

    def __mul__(self, event: EventData) -> int:
        score: int = -1

        for sub_rule in self._rule:
            if Rule._match(sub_rule, event):
                score = score + 1 if score > -1 else 1
            else:
                return -1
        return score

    def __repr__(self):
        return (self._rule.__repr__()).__repr__()


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


def parse_sfx(rows: List[List[str]]) -> Rules:
    rules = Rules()
    rules_width = 5
    link_index = 7

    for i, row in enumerate([row for row in rows if row]):
        if all([cell == "" for cell in row]):
            continue
        rule = Rule()
        for cell in [c for c in row[:rules_width] if c]:
            rule += cell
        if row[link_index].strip():
            rules += (rule, row[link_index])
    return rules


def parse_music(rows: List[List[str]]) -> Rules:
    rules = Rules()
    rules_width = 5
    link_index, priority_index = 7, 8

    for i, row in enumerate([row for row in rows if row]):
        rule = Rule()
        for cell in [c for c in row[:rules_width] if c.strip()]:
            rule += cell
        if row[link_index].strip():
            rules += (rule, Music(row[link_index], int(row[priority_index])))
    return rules
