from pcsd_cog.model import parse_music, parse_sfx
import json
from pcsd_cog.events import EventChampionKill, EventDragonKill, EventIdle
from pcsd_cog.players import Player
from pcsd_cog.model import Music


def test_parse_music():
    print(parse_music())


def test_parse_sfx():
    print(parse_sfx())


def test_sfx_matching():
    rules = parse_sfx()
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    track = rules.match(event)
    assert track == "http://success_2"


def test_music_matching_event():
    rules = parse_music()
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    music = rules.match(event)
    assert music == Music(name="http://success", priority=0)


def test_music_matching_idle():
    rules = parse_music()
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    event = EventIdle(Players=players, EventID=0, EventName="EventIdle", EventTime=0.0)
    music = rules.match(event)
    assert music == Music("https://success_2", 5)


def test_music_priorities():
    rules = parse_music()
    with open("tests/sample_players.json") as f:
        players = [Player(**p) for p in json.load(f)]
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    music_1 = rules.match(event)

    with open("tests/sample_dragonkill.json") as f:
        event = EventDragonKill(Players=players, **json.load(f))
    music_2 = rules.match(event)
    assert music_2 > music_1
