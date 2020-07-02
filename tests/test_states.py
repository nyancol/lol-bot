from pcsd_cog.states import StateMachine, StateLobby, StateGame
from pcsd_cog.players import Player
from pcsd_cog import model
from pcsd_cog.events import EventChampionKill
from redbot.core.bot import Red
import pytest
from unittest.mock import MagicMock, AsyncMock, patch, call
import json
from copy import deepcopy

from time import sleep


@pytest.fixture
def player():
    m_player = MagicMock()
    m_player.play = AsyncMock()
    m_player.stop = AsyncMock()
    m_player.skip = AsyncMock()
    m_player.connect = AsyncMock()
    m_player.load_tracks = AsyncMock()
    m_player.is_playing = False
    m_player.current = None
    return m_player


@pytest.fixture
def rules_sfx():
    rows = model.get_sheet('TEST_SFX!A2:I40')
    return model.parse_sfx(rows)


@pytest.fixture
def rules_music():
    rows = model.get_sheet('TEST_MUSIC!A2:I30')
    return model.parse_music(rows)


@pytest.fixture
def players():
    with open("tests/sample_players.json") as f:
        player_list = [Player(**p) for p in json.load(f)]
    return player_list


@pytest.fixture
def event_championkill(players):
    with open("tests/sample_championkill.json") as f:
        event = EventChampionKill(Players=players, **json.load(f))
    return event


@pytest.fixture
def state_game(player, rules_music, rules_sfx):
    machine = StateMachine(StateGame(player))
    machine.state.rules_sfx = rules_sfx
    machine.state.rules_music = rules_music
    return machine.state


@pytest.mark.asyncio
async def test_lobby_to_game(player):
    machine = StateMachine(StateLobby(player))
    await machine.tick()
    assert isinstance(machine.state, StateGame)


@pytest.mark.asyncio
async def test_music_idleevent(state_game, players):
    state_game.fetch_playerlist = lambda: players
    state_game.current_id = 5
    m_requests = MagicMock()
    m_requests["Events"] = []

    with patch("requests.get", m_requests):
        events = state_game.fetch_gamedata()
    assert len(events) == 1
    track_music = state_game.rules_music.match(events[0])
    assert track_music == model.Music("https://success_2", 5)
    assert state_game.current_id == 5


@pytest.mark.asyncio
async def test_currentid_increment(state_game, players, event_championkill):
    state_game.fetch_playerlist = lambda: players

    events = [deepcopy(event_championkill) for _ in range(10)]
    for i, e in enumerate(events):
        e.EventID = i

    state_game.fetch_gamedata = lambda: events
    assert state_game.current_id == 0
    await state_game.tick()
    assert state_game.current_id == 10


@pytest.mark.asyncio
async def test_play_on_championkill(state_game, players, event_championkill):
    state_game.fetch_playerlist = lambda: players
    state_game.fetch_gamedata = lambda: [event_championkill]
    state_game.play_sfx = AsyncMock()
    state_game.play_music = AsyncMock()

    await state_game.tick()
    state_game.play_sfx.assert_called_once_with("http://success_2")
    state_game.play_music.assert_called_once_with(model.Music("http://success", 0))


@pytest.mark.asyncio
async def test_play_sfx_once(state_game, players, event_championkill):
    state_game.fetch_playerlist = lambda: players
    state_game.fetch_gamedata = lambda: [event_championkill]
    state_game.play_sfx = AsyncMock()
    state_game.play_music = AsyncMock()

    await state_game.tick()
    assert state_game.sfx_manager.enabled == False
    await state_game.tick()
    state_game.play_sfx.assert_called_once_with("http://success_2")
