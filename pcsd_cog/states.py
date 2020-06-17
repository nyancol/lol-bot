from typing import List, DefaultDict, Dict
from pcsd_cog.events import *
from pcsd_cog import reader
from pcsd_cog.reader import Rule
from pcsd_cog.players import Player
from collections import defaultdict
from redbot.core.commands import Context
from pathlib import Path
import random



class State:
    def __init__(self, ctx: Context):
        self.host: str = "192.168.1.11"
        self._ctx = ctx
        self._dj = ctx.bot.cogs["Audio"]
        self._root = "/home/pi/pcsd_bot/data/cogs/Audio/localtracks/"

    async def tick(self) -> 'State':
        raise NotImplementedError

    async def play_background(self, track):
        if track.startswith("https://"):
            return await self._dj.command_play(ctx=self._ctx, query=track)
        return await self._dj.command_play(ctx=self._ctx, query=self._root + track)

    async def play_sfx(self, track):
        if track.startswith("https://"):
            return await self._dj.command_play(ctx=self._ctx, query=track)
        return await self._dj.command_play(ctx=self._ctx, query=self._root + track)

    async def stop(self):
        return await self._dj.command_stop(ctx=self._ctx)

    async def skip(self):
        return await self._dj.command_skip(ctx=self._ctx)

    def event_to_path(self, event, **argv):
        path = Path(self._root) / type(event).__name__
        for k, v in argv.items():
            path /= f"{k}={v}"
        if path.exists():
            return [f.as_posix()[len(self._root):] for f in path.iterdir() if f.is_file()]
        else:
            return []

    def builder(self, state, *argc, **argv):
        return state(self._ctx, *argc, **argv)


class StateMachine:
    def __init__(self, state: State):
        self.state = state

    async def tick(self):
        self.state = await self.state.tick()


class StateDisconnected(State):
    async def tick(self):
        raise NotImplementedError

class StateConnected(State):
    async def tick(self):
        raise NotImplementedError


class StateLobby(State):
    async def tick(self):
        return self.builder(StateGame)


class StateGame(State):
    def __init__(self, *argc, **argv):
        super().__init__(*argc, **argv)
        players = self.fetch_playerlist()
        self.players: Map[str, Player] = {p.summonerName: p for p in players}
        self.current_id: int = 0

        # cell_range = "EVENEMENTS!A36:M41"
        # values = reader.get_sheet(cell_range)
        # self.mapping: Mapping[Event, Mapping[Rule, str]] = reader.parse(values)

    def fetch_gamestats(self) -> EventGameStats:
        return requests.get("https://" + self.host + ":2999/liveclientdata/gamestats", verify=False).json()

    def fetch_playerlist(self) -> List[Player]:
        try:
            print("fetching player list")
            response = requests.get("https://" + self.host + ":2999/liveclientdata/playerlist", verify=False)
            print(response)
            response = response.json()
        except requests.exceptions.ConnectionError as exc:
            print(exc)
            return None
        except TypeError as exc:
            print(f"Error when fetching Playerlist: {response}")
            return None
        return [Player(**p) for p in response]

    @staticmethod
    def parse_gamedata(response) -> List[EventData]:
        event_list = []
        for e in response["Events"]:
            event_class_str = "Event" + e["EventName"]
            event_class = eval(event_class_str)
            try:
                event_list.append(event_class(**e))
            except Exception as exc:
                print(e)
        # with open("./eventdata.json", "a") as f:
            # f.write('\n'.join(event_list))
        return event_list

    def fetch_gamedata(self) -> List[EventData]:
        params = {"eventID": self.current_id}
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/eventdata", params=params, verify=False).json()
        except Exception as exc:
            print(exc)
            return []
        return self.parse_gamedata(response)

    async def tick(self) -> State:
        events = self.fetch_gamedata()
        if not self.is_playing():
            await self.play_background()

        for e in [e for e in events if e]:
            self.current_id = max(event.EventID, self.current_id) + 1
            track = self.eventdata_to_track(event)
            if track:
                # await self.stop()
                await self.play_sfx(track)

        if any([isinstance(e, EventGameEnd) for e in events]):
            return self.builder(StateGameEnd)
        return self

    async def play_background(self):
        pass

    async def play_sfx(self):
        pass

    def eventdata_to_track(self, event):
        track = None
        # if type(event) in self.mapping:
        #     print("Found ChampionKill")
        #     scores = {event.to_rule(self.players).distance(r): t for r, t in self.mapping[type(event)].items()}
        #     max_score = max(scores.keys())
        #     if max_score > 0:
        #         track = scores[max_score]
        #     print(f"Returning track: {track}")
        #     return track

        if isinstance(event, EventChampionKill):
            pass
            # if event.KillerName.startswith("Minion_"):
            #     team = "ORDER" if self.players[event.VictimName].team == "CHAOS" else "CHAOS"
            #     track = self.event_to_path(event, team=team)
            # elif event.KillerName.startswith("Turret_"):
            #     team = "ORDER" if self.players[event.VictimName].team == "CHAOS" else "CHAOS"
            #     track = self.event_to_path(event, team=team)
            # else:
            #     try:
            #         track = self.event_to_path(event, team=self.players[event.KillerName].team)
            #     except Exception as exc:
            #         print(f"{exc} - {event.KillerName} - {self.players}")
        elif isinstance(event, EventMultikill):
            track = self.event_to_path(event)
        elif isinstance(event, EventMinionsSpawning):
            track = self.event_to_path(event)
        elif isinstance(event, EventTurretKilled):
            if event.KillerName.startswith("Minion_"):
                pass
            else:
                # track = self._soundfx(event, team=self.players[event.KillerName].team)
                track = self.event_to_path(event)
        elif isinstance(event, EventDragonKill):
            track = self.event_to_path(event)
        elif isinstance(event, EventBaronKill):
            track = self.event_to_path(event)
        elif isinstance(event, EventHeraldKill):
            track = self.event_to_path(event)
        elif isinstance(event, EventInhibKilled):
            track = self.event_to_path(event)
        elif isinstance(event, EventGameEnd):
            track = self.event_to_path(event, Result=event.Result)
        elif isinstance(event, EventGameStart):
            track = self.event_to_path(event)
        elif isinstance(event, EventFirstBlood):
            track = self.event_to_path(event)
        elif isinstance(event, EventInhibRespawningSoon):
            pass

        if track and isinstance(track, list):
            if len(track) > 1:
                track = track[random.randint(0, len(track) - 1)]
            else:
                track = track[0]
        return track


class StateGameEnd(State):
    async def tick(self):
        return self
