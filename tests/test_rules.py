import json
import pytest

from pcsd_cog import events
from pcsd_cog import model
from pcsd_cog.events import EventChampionKill, EventDragonKill, EventIdle
from pcsd_cog.model import Music, parse_music, parse_sfx
from pcsd_cog.calculator import getattr_rec
from pcsd_cog.players import Player


@pytest.fixture
def players():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    return players


@pytest.fixture
def event_championkill(players):
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    return event


@pytest.fixture
def rules_sfx():
    rows = model.get_sheet('TEST_SFX!A2:I40')
    return parse_sfx(rows)


@pytest.fixture
def rules_music():
    rows = model.get_sheet('TEST_MUSIC!A2:I30')
    return parse_music(rows)


def test_multiple_subrules():
    rule = model.Rule()
    rule += "1 == 1"
    rule += "1 == 2"
    assert len(rule._rule) == 2

def test_match_2_rules(players):
    rules = model.Rules()
    rule = model.Rule() + "KillerName == Winner"
    rules += (rule, "ok")
    rule = model.Rule() + "KillerName == Looser"
    rules += (rule, "ko")

    event = events.EventChampionKill(players, "", 0, 0.0, "Looser", "Winner", [])
    res = rules.match(event)
    assert res == "ok"


def test_champion_in_players(players):
    rule = model.Rule() + 'Annie IN Players.championName'
    event = events.EventChampionKill(players, "", 0, 0.0, "Looser", "Winner", ["assister_a", "assister_b"])
    assert model.Rule._match(rule._rule[0], event)


def test_value_in_event(players):
    rules = model.Rules()
    rule = model.Rule() + "assister_a IN Assisters.summonerName"
    rules += (rule, "ok")
    rule = model.Rule() + "Winner IN Assisters.summonerName"
    rules += (rule, "ko")

    event = events.EventChampionKill(players, "", 0, 0.0, "Looser", "Winner", ["assister_a", "assister_b"])
    res = rules.match(event)
    assert res == "ok"


def test_sfx_matching(rules_sfx, event_championkill):
    track = rules_sfx.match(event_championkill)
    assert track == "http://success_2"


def test_music_matching_event(rules_music, event_championkill):
    music = rules_music.match(event_championkill)
    assert music == Music(name="http://success", priority=0)


def test_music_matching_idle(rules_music, players):
    event = EventIdle(Players=players, EventID=0, EventName="EventIdle", EventTime=0.0)
    music = rules_music.match(event)
    assert music == Music("https://success_2", 5)


def test_music_priorities(rules_music, event_championkill):
    music_1 = rules_music.match(event_championkill)

    # with open("tests/sample_dragonkill.json") as f:
    #     event_dragon = EventDragonKill(Players=players, **json.load(f))
    # music_2 = rules_music.match(event_dragon)
    # assert music_2 > music_1


def test_count(players):
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert model.Expression("COUNT(Assisters)").resolve(event) == 4


def test_count_assists(rules_sfx, players):
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    track = rules_sfx.match(event)
    assert track == "https://destruction"


def test_preaggregation(rules_music):
    pass


def test_music_queue(rules_music, event_championkill):
    music_1 = rules_music.match(event_championkill)
    music_1.played = True
    music_2 = rules_music.match(event_championkill)
    assert music_1.name == "http://success"
    assert music_2.name == "https://success_2"
