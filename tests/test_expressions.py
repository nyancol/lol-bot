import pytest
import json
from pcsd_cog import model
from pcsd_cog.players import Player
from pcsd_cog.events import EventData, EventChampionKill, EventIdle
from pcsd_cog.calculator import Expression


@pytest.fixture
def event():
    return EventIdle("", EventID=0, EventName="EventIdle", EventTime=0.0)


@pytest.fixture
def event_players():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    return EventIdle(Players=players, EventID=0, EventName="EventIdle", EventTime=0.0)


def test_int(event):
    assert Expression("1").resolve(event) == 1
    assert Expression("11").resolve(event) == 11
    assert Expression("1 + 1").resolve(event) == 2


def test_float(event):
    assert Expression("1.1").resolve(event) == 1.1
    assert Expression("42.0 + 2.2").resolve(event) == 44.2


def test_str(event):
    assert Expression("asdf").resolve(event) == "asdf"
    assert Expression("a.sdf").resolve(event) == "a.sdf"
    assert Expression("a.s+df").resolve(event) == "a.sdf"


def test_bool(event):
    assert Expression("true").resolve(event) == True
    assert Expression("false").resolve(event) == False

## Music
def test_compare_priorities():
    m1 = model.Music("a", 0)
    m2 = model.Music("b", 1)

    assert m1 < m2
    assert m1 <= m2
    assert m2 >= m1
    assert m2 > m1
    assert m1 >= m1
    assert m1 <= m1

## EQ
def test_1_eq_1(event):
    rule = model.Rule() + "1 == 1"
    assert model.Rule._match(rule._rule[0], event)


def test_aa_eq_aa(event):
    rule = model.Rule() + "aa == aa"
    assert model.Rule._match(rule._rule[0], event)


def test_1_eq_2(event):
    rule = model.Rule() + "1 == 2"
    assert model.Rule._match(rule._rule[0], event) == False


## NE
def test_1_ne_2(event):
    rule = model.Rule() + "1 != 2"
    assert model.Rule._match(rule._rule[0], event)

def test_2_ne_2(event):
    rule = model.Rule() + "2 != 2"
    assert model.Rule._match(rule._rule[0], event) == False

## LT
def test_1_lt_2(event):
    rule = model.Rule() + "1 < 2"
    assert model.Rule._match(rule._rule[0], event)


## LE
def test_2_le_2(event):
    rule = model.Rule() + "2 <= 2"
    assert model.Rule._match(rule._rule[0], event)


## GT
def test_2_gt_1(event):
    rule = model.Rule() + "2 > 1"
    assert model.Rule._match(rule._rule[0], event)


# GE
def test_2_ge_2(event):
    rule = model.Rule() + "2 >= 2"
    assert model.Rule._match(rule._rule[0], event)


# LIKE
def test_aaa_like_aa(event):
    event = EventData("", "", "", "")
    rule = model.Rule() + "aa LIKE aa.*"
    assert model.Rule._match(rule._rule[0], event)


def test_baa_notlike_aa(event):
    rule = model.Rule() + "ba LIKE aa.*"
    assert model.Rule._match(rule._rule[0], event) == False


# COUNT
def test_count_list(event):
    assert Expression("COUNT([2])").resolve(event) == 1
    assert Expression("COUNT([1,2])").resolve(event) == 2
    assert Expression("COUNT([ 1 , 2 ,3])").resolve(event) == 3

# MAX
def test_max_list(event):
    assert Expression("MAX([2])").resolve(event) == 2
    assert Expression("MAX([1,2])").resolve(event) == 2
    assert Expression("MAX([ 1 , 3, 2])").resolve(event) == 3


# MIN
def test_min_list(event):
    assert Expression("MIN([2])").resolve(event) == 2
    assert Expression("MIN([1,2])").resolve(event) == 1
    assert Expression("MIN([ 3, 1, 2])").resolve(event) == 1


# SUM
def test_sum_list(event):
    assert Expression("SUM([2])").resolve(event) == 2
    assert Expression("SUM([1,2])").resolve(event) == 3
    assert Expression("SUM([ 1 , 2 ,3])").resolve(event) == 6


# SUM - Event
def test_sum_simple(event_players):
    assert Expression("SUM(Players.scores.kills)").resolve(event_players) == 3


# SUM - Event + remain
def test_sum_complex(event_players):
    assert Expression("MAX(Players.scores.kills).championName").resolve(event_players) == "Annie"


# ADD - Event + int
def test_add_event_int(event_players):
    assert Expression("COUNT(Players) + 4").resolve(event_players) == 10


# MUL - Event + int
def test_mult_event_int(event_players):
    assert Expression("SUM(Players.scores.kills) * 4").resolve(event_players) == 12


## EVENTS
def test_players_eq():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert "Annie" in Expression("Players.championName").resolve(event)
    assert "Winner" in Expression("Players.summonerName").resolve(event)
    assert "asdf" not in Expression("Players.summonerName").resolve(event)


def test_players_count_1():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert Expression("COUNT(Assisters)").resolve(event) == 1


def test_players_count_4():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert Expression("COUNT(Assisters)").resolve(event) == 4


def test_players_max_champname():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventData(players, "", "", "")
    assert Expression("MAX(Players.scores.kills).championName").resolve(event) == "Annie"


def test_players_max_kills():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventData(players, "", "", "")
    assert Expression("MAX(Players.scores.kills).scores.kills").resolve(event) == 3


def test_invalid_path():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    rule = (model.Rule() + "TurretKilled == asdf")
    assert model.Rule._match(rule._rule[0], event) == False


def test_compare_list():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
        for p in [p for p in players if p.team == "ORDER"]:
            p.isDead = True

    event = EventData(players, "", "", "")
    rule = (model.Rule() + "Order.isDead == [true,true,true,true,true]")
    assert model.Rule._match(rule._rule[0], event) == True
    rule = (model.Rule() + "Order.isDead == [false,true,true,true,true]")
    assert model.Rule._match(rule._rule[0], event) == False
