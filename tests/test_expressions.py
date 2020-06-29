import json
from pcsd_cog import model
from pcsd_cog.players import Player
from pcsd_cog.events import EventData, EventChampionKill


## EQ
def test_1_eq_1():
    rule = model.Rule() + "1 == 1"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_aa_eq_aa():
    rule = model.Rule() + "aa == aa"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_1_eq_2():
    rule = model.Rule() + "1 == 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False


## NE
def test_1_ne_2():
    rule = model.Rule() + "1 != 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))

def test_2_ne_2():
    rule = model.Rule() + "2 != 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False

## LT
def test_1_lt_2():
    rule = model.Rule() + "1 < 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


## LE
def test_2_le_2():
    rule = model.Rule() + "2 <= 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


## GT
def test_2_gt_1():
    rule = model.Rule() + "2 > 1"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


# GE
def test_2_ge_2():
    rule = model.Rule() + "2 >= 2"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


# LIKE
def test_aaa_like_aa():
    rule = model.Rule() + "aa LIKE aa.*"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", ""))


def test_baa_notlike_aa():
    rule = model.Rule() + "ba LIKE aa.*"
    assert model.Rule._match(rule._rule[0], EventData("", "", "", "")) == False


## EVENTS
def test_players_eq():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    rule = (model.Rule() + "Players.championName == Annie")
    assert model.Rule._match(rule._rule[0], event)
    rule = (model.Rule() + "Players.summonerName == Winner")
    assert model.Rule._match(rule._rule[0], event)
    rule = (model.Rule() + "Players.summonerName == asdf")
    assert model.Rule._match(rule._rule[0], event) == False


def test_players_count_1():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    rule = (model.Rule() + "COUNT(Assisters) == 1")
    assert model.Rule._match(rule._rule[0], event)


def test_players_count_4():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    rule = (model.Rule() + "COUNT(Assisters) == 4")
    assert model.Rule._match(rule._rule[0], event)


def test_players_max_champname():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventData(players, "", "", "")
    rule = (model.Rule() + "MAX(Players.scores.kills).championName == Annie")
    assert model.Rule._match(rule._rule[0], event)


def test_players_max_kills():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventData(players, "", "", "")
    rule = (model.Rule() + "MAX(Players.scores.kills).scores.kills == 3")
    assert model.Rule._match(rule._rule[0], event)


def test_invalid_path():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    rule = (model.Rule() + "TurretKilled == asdf")
    assert model.Rule._match(rule._rule[0], event) == False