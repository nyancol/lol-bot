import pytest
import json
from pcsd_cog.events import *
from pcsd_cog.states import StateGame


@pytest.fixture()
def eventdata():
    with open("tests/sample_eventdata.json") as f:
        data = json.load(f)
    return data


def test_parse_events(eventdata):
    events = StateGame.parse_gamedata(eventdata)
    expected_events = [
        EventGameStart(0, "GameStart", 0.0),
        EventMinionsSpawning(0, "MinionsSpawning", 0.0),
        EventFirstBrick(0, "FirstBrick", 0.0, "Riot Tuxedo"),
        EventTurretKilled(0, "TurretKilled", 0.0, "Turret_T2_L_03_A", "Riot Tuxedo", ["Player 1"]),
        EventInhibKilled(0, "InhibKilled", 0.0, "Barracks_T2_R1", "Riot Tuxedo", ["Player 1"]),
        EventDragonKill(0, "DragonKill", 0.0, "Earth", "False", "Riot Tuxedo", ["Player 1"]),
        EventDragonKill(0, "DragonKill", 0.0, "Elder", "True", "Riot Tuxedo", ["Player 1"]),
        EventHeraldKill(0, "HeraldKill", 0.0, "False", "Riot Tuxedo", ["Player 1"]),
        EventBaronKill(0, "BaronKill", 0.0, "False", "Riot Tuxedo", ["Player 1"]),
        EventChampionKill(0, "ChampionKill", 0.0, "Riot Gene", "Riot Tuxedo", ["Player 1"]),
        EventMultikill(0, "Multikill", 0.0, "Riot Tuxedo", 2),
        EventMultikill(0, "Multikill", 0.0, "Riot Tuxedo", 3),
        EventMultikill(0, "Multikill", 0.0, "Riot Tuxedo", 4),
        EventMultikill(0, "Multikill", 0.0, "Riot Tuxedo", 5),
        EventAce(0, "Ace", 0.0, "Riot Tuxedo", "ORDER"),
    ]

    assert events == expected_events
