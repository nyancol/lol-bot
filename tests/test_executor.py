from pathlib import Path


def test_fx_kill():
    pass
    # e = EventChampionKill(0, "EventChampionKill", 0.0, "Victim 1", "Killer 2", ["Assist 3"])
    # players = [Player("ChampionName", False, False, [], 1, "", "", 0.0, None, None, 0, "Killer 2", None, "ORDER")]
    # executor = Executor(players)
    # sfx = executor._soundfx(e, **{"team": executor._players[e.KillerName].team})
    # assert sfx == [Path(executor._root) / "EventChampionKill/team=ORDER/fatality.mp3"]

def test_fx_killed():
    pass
    # e = EventChampionKill(0, "EventChampionKill", 0.0, "Victim 1", "Killer 2", ["Assist 3"])
    # players = [Player("ChampionName", False, False, [], 1, "", "", 0.0, None, None, 0, "Killer 2", None, "CHAOS")]
    # executor = Executor(players)
    # sfx = executor._soundfx(e, **{"team": executor._players[e.KillerName].team})
    # assert sfx == [Path(executor._root) / "EventChampionKill/team=CHAOS/fuckyou.mp3"]
