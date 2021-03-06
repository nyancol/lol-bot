from __future__ import annotations

import asyncio
from pathlib import Path
from redbot.core.commands import Context
from typing import List, DefaultDict, Dict, Optional, Mapping
import random
import lavalink
import requests

from pcsd_cog.events import * # EventData, EventIdle, EventGameStart, EventGameEnd, EventMinionsS
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
    def __init__(self, player):
        self.host: str = "192.168.1.11"
        self.author = "Le Prophète#7328"
        self._player = player
        self._root: str = "/home/pi/pcsd_bot/data/cogs/Audio/localtracks/"
        self.current_music: Optional[Music] = None

    def refresh(self) -> None:
        rows_sfx: List[List[str]] = model.get_sheet('SFX!B52:I68')
        self.rules_sfx = model.parse_sfx(rows_sfx)
        rows_music: List[List[str]] = model.get_sheet('MUSIC!A15:I260')
        self.rules_music = model.parse_music(rows_music)

    async def tick(self) -> State:
        raise NotImplementedError

    async def stop_music(self) -> None:
        await self._player.stop()

    async def play_music(self, track: Music) -> None:
        print(f"Loading music track: {track.name}")
        try:
            track_obj = (await self._player.load_tracks(track.name)).tracks[0]
        except IndexError:
            print(f"No tracks found for: {track.name}")
            return
        if self._player.current is None or self.current_music is None or self.current_music < track:
            print(f"Playing music {track}")
            self.current_music = track
            if self._player.current:
                await self._player.stop()
            self._player.add(self.author, track_obj)
            track.played = True
            await self._player.play()
            while self._player.current is None:
                await asyncio.sleep(1)
        else:
            print(f"Not playing music {track}")

    async def play_sfx(self, track: str):
        print(f"Loading sfx track: {track}")
        track_sfx = (await self._player.load_tracks(track)).tracks[0]
        if self._player.current:
            self._player.add(self.author, track_sfx)
            track_music = self._player.current
            track_music.start_timestamp = self._player.position
            track_music.seekable = True
            self._player.add(self.author, track_music)
            await self._player.skip()
        else:
            self._player.add(self.author, track_sfx)
            await self._player.play()

    def builder(self, state, *argc, **argv) -> State:
        return state(self._player, *argc, **argv)


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
    def __init__(self, *argc, **argv):
        super().__init__(*argc, **argv)
        self.refresh()

    async def tick(self) -> State:
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/playerlist", verify=False, timeout=1)
            response.json()
            if response.status_code != 404:
                print(response.json())
                print("Moving to StateGame")
                await self.stop_music()
                return self.builder(StateGame)
        except Exception as exc:
            print(exc)
            pass
        track_music: Optional[Music] = self.rules_music.match(EventLobby())
        if track_music:
            await self.play_music(track_music)
        print("Staying in Lobby")
        return self


class StateGame(State):
    def __init__(self, *argc, **argv):
        super().__init__(*argc, **argv)
        self.current_id: int = 0
        self.refresh()
        self.sfx_manager = SFXEnabled()

    def fetch_gamestats(self) -> EventGameStats:
        return requests.get("https://" + self.host + ":2999/liveclientdata/gamestats", verify=False).json()

    def fetch_playerlist(self) -> List[Player]:
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/playerlist", verify=False)
            playerlist = response.json()
        except requests.exceptions.ConnectionError as exc:
            # raise Exception(f"Failed requesting playerlist: {exc}")
            print(f"Failed requesting players list {exc}")
            return []
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

        event_list: List[EventData] = [EventIdle(players, "Idle", 0, 0.0)]
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
            if e.EventName != "Idle":
                self.current_id = max(e.EventID, self.current_id) + 1
            if e.EventName == "GameEnd":
                print("Game End", e)
            else:
                print(e)
            track_sfx: Optional[str] = self.rules_sfx.match(e)
            track_music: Optional[Music] = self.rules_music.match(e)
            print(f"SFX: {track_sfx}, MUSIC: {track_music} - {self._player.is_playing} - {self._player.current}")

            if track_sfx and self.sfx_manager.enabled:
                print("Playing sfx")
                await self.play_sfx(track_sfx)

            if track_music:
                await self.play_music(track_music)

        if any([isinstance(e, EventGameEnd) for e in events]):
            return self.builder(StateGameEnd)
        return self


class StateGameEnd(State):
    async def tick(self) -> State:
        # wait 30 s of music then move to lobby
        await asyncio.sleep(30)
        return self.builder(StateLobby)
