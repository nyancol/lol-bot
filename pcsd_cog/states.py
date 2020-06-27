from __future__ import annotations

from pathlib import Path
from redbot.core.commands import Context
from typing import List, DefaultDict, Dict, Optional, Mapping
import random
import lavalink
import requests

from pcsd_cog.events import EventData, EventIdle, EventGameStats, EventGameEnd
from pcsd_cog.players import Player
from pcsd_cog import model
from pcsd_cog.model import Music, Rule
from datetime import datetime, timedelta


class SFXEnabled:
    def __init__(self):
        self.last: Optional[datetime] = None

    @property
    def enabled(self):
        if self.last is None or datetime.now() - self.last > timedelta(minutes=1):
            self.last = datetime.now()
            return True
        return False


class State:
    def __init__(self, ctx: Context):
        self.host: str = "192.168.1.11"
        self._ctx: Context = ctx
        self._player: lavalink.player_manager.Player = lavalink.get_player(ctx.guild.id).connect()
        # await self._player.wait_until_ready()
        self._root: str = "/home/pi/pcsd_bot/data/cogs/Audio/localtracks/"
        self.current_music: Optional[Music] = None

    async def tick(self) -> State:
        raise NotImplementedError

    def refresh(self) -> None:
        pass

    async def play_music(self, track: Music) -> None:
        track_obj: lavalink.rest_api.Track = (await self._player.search_yt(track.name))[0]
        if not self._player.is_playing() or self.current_music is None or self.current_music < track:
            self.current_music = track
            await self._player.stop()
            self._player.add(self._ctx.author, track_obj)
            await self._player.play()

    async def play_sfx(self, track: str):
        track_sfx: lavalink.read_api.Track = (await self._player.search_yt(track))[0]
        if self._player.is_playing():
            self._player.add(self._ctx.author, track_sfx)
            track_music = self._player.current
            track_music.start_timestamp(self._player.position)
            track_music.seekable = True
            self._player.add(self._ctx.author, track_music)
            await self._player.skip()
        else:
            self._player.add(self._ctx.author, track_sfx)

    def builder(self, state, *argc, **argv) -> State:
        return state(self._ctx, *argc, **argv)


class StateMachine:
    def __init__(self, state: State):
        self.state = state

    def refresh(self) -> None:
        self.state.refresh()

    async def tick(self) -> None:
        self.state = await self.state.tick()


class StateDisconnected(State):
    async def tick(self) -> State:
        raise NotImplementedError

class StateConnected(State):
    async def tick(self) -> State:
        raise NotImplementedError


class StateLobby(State):
    async def tick(self) -> State:
        return self.builder(StateGame)


class StateGame(State):
    def __init__(self, *argc, **argv):
        super().__init__(*argc, **argv)
        self.current_id: int = 0
        rows: List[List[str]] = model.get_sheet('SFX!A2:I30')
        self.rules_sfx: Rules = model.parse_sfx(rows)

        rows: List[List[str]] = model.get_sheet('MUSIC!A2:I30')
        self.rules_music: Rules = model.parse_music(rows)
        self.sfx_manager = SFXEnabled()

    def refresh(self) -> None:
        rows_sfx: List[List[str]] = model.get_sheet('SFX!A2:I30')
        self.rules_sfx = model.parse_sfx(rows_sfx)
        rows_music: List[List[str]] = model.get_sheet('MUSIC!A2:I30')
        self.rules_music = model.parse_music(rows_music)

    def fetch_gamestats(self) -> EventGameStats:
        return requests.get("https://" + self.host + ":2999/liveclientdata/gamestats", verify=False).json()

    def fetch_playerlist(self) -> List[Player]:
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/playerlist", verify=False)
            playerlist = response.json()
        except requests.exceptions.ConnectionError as exc:
            raise Exception(f"Failed requesting playerlist: {exc}")
        except TypeError as exc:
            raise Exception(f"Failed requesting playerlist: {exc}")
        return [Player(**p) for p in playerlist]

    def fetch_gamedata(self) -> List[EventData]:
        players: List[Player] = self.fetch_playerlist()
        params = {"eventID": self.current_id}
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/eventdata", params=params, verify=False).json()
        except Exception as exc:
            print(exc)
            return []

        event_list: List[EventData] = [EventIdle(players, "EventIdle", self.current_id - 1, 0.0)]
        for e in response["Events"]:
            event_class_str = "Event" + e["EventName"]
            event_class = eval(event_class_str)
            try:
                event_list.append(event_class(**{"Players": players, **e}))
            except Exception as exc:
                print(e)
        return event_list

    async def tick(self) -> State:
        events: List[EventData] = self.fetch_gamedata()
        for e in events:
            self.current_id = max(e.EventID, self.current_id) + 1
            track_sfx: str = self.rules_sfx.match(e)
            track_music: Music = self.rules_music.match(e)

            if track_sfx and self.sfx_manager.enabled():
                await self.play_sfx(track_sfx)

            if track_music:
                await self.play_music(track_music)

        if any([isinstance(e, EventGameEnd) for e in events]):
            return self.builder(StateGameEnd)
        return self


class StateGameEnd(State):
    async def tick(self) -> State:
        return self
