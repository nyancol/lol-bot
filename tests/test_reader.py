from pcsd_cog.model import parse_music, parse_sfx
import json
from pcsd_cog.events import EventChampionKill, EventDragonKill, EventIdle
from pcsd_cog.players import Player
from pcsd_cog.model import Music, getattr_rec
import pytest


@pytest.fixture
def rules_sfx():
    range_sfx = 'TEST_SFX!A2:I40'
    return parse_sfx(range_sfx)


@pytest.fixture
def rules_music():
    range_music = 'TEST_MUSIC!A2:I30'
    return parse_music(range_music)


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
        event = EventChampionKill(Players=players, **json.load(f))
    music_1 = rules_music.match(event)

    with open("tests/sample_dragonkill.json") as f:
        event = EventDragonKill(Players=players, **json.load(f))
    music_2 = rules_music.match(event)
    assert music_2 > music_1


def test_count():
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill_2.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    assert getattr_rec(event, ["COUNT(Assisters)"]) == 4


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
    pass
