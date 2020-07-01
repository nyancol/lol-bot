import json
import pytest

from pcsd_cog import events
from pcsd_cog import model
from pcsd_cog.events import EventChampionKill, EventDragonKill, EventIdle
from pcsd_cog.model import Music, getattr_rec
from pcsd_cog.model import parse_music, parse_sfx, Music, getattr_rec
from pcsd_cog.players import Player


def test_multiple_subrules():
    rule = model.Rule()
    rule += "1 == 1"
    rule += "1 == 2"
    assert len(rule._rule) == 2

def test_match_2_rules():
    rules = model.Rules()
    rule = model.Rule() + "KillerName == Winner"
    rules += (rule, "ok")
    rule = model.Rule() + "KillerName == Looser"
    rules += (rule, "ko")

    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = events.EventChampionKill(players, "", 0, 0.0, "Looser", "Winner", [])
    res = rules.match(event)
    assert res == "ok"


def test_match_element_in_list():
    rules = model.Rules()
    rule = model.Rule() + "Assisters.summonerName == assister_a"
    rules += (rule, "ok")
    rule = model.Rule() + "Assisters.summonerName == Winner"
    rules += (rule, "ko")

    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = events.EventChampionKill(players, "", 0, 0.0, "Looser", "Winner", ["assister_a", "assister_b"])
    res = rules.match(event)
    assert res == "ok"



@pytest.fixture
def rules_sfx():
    rows = model.get_sheet('TEST_SFX!A2:I40')
    return parse_sfx(rows)


@pytest.fixture
def rules_music():
    rows = model.get_sheet('TEST_MUSIC!A2:I30')
    return parse_music(rows)


def test_sfx_matching(rules_sfx):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    track = rules_sfx.match(event)
    assert track == "http://success_2"


def test_music_matching_event(rules_music):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    music = rules_music.match(event)
    assert music == Music(name="http://success", priority=0)


def test_music_matching_idle(rules_music):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventIdle(Players=players, EventID=0, EventName="EventIdle", EventTime=0.0)
    music = rules_music.match(event)
    assert music == Music("https://success_2", 5)


def test_music_priorities(rules_music):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event_champion = EventChampionKill(Players=players, **json.load(f))
    music_1 = rules_music.match(event_champion)

    # with open("tests/sample_dragonkill.json") as f:
    #     event_dragon = EventDragonKill(Players=players, **json.load(f))
    # music_2 = rules_music.match(event_dragon)
    # assert music_2 > music_1


def test_count():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert model.Expression("COUNT(Assisters)").resolve(event) == 4


def test_count_assists(rules_sfx):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    track = rules_sfx.match(event)
    assert track == "https://destruction"


def test_preaggregation(rules_music):
    pass


def test_music_queue(rules_music):
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    music_1 = rules_music.match(event)
    music_2 = rules_music.match(event)
    assert music_1.name == "http://success"
    assert music_2.name == "https://success_2"
