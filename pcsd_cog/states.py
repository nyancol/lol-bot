from typing import List, DefaultDict, Dict
from pcsd_cog.events import *
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

    async def play(self, track):
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

    async def fetch_gamestats(self) -> EventGameStats:
        return requests.get("https://" + self.host + ":2999/liveclientdata/gamestats", verify=False).json()

    def fetch_playerlist(self) -> List[Player]:
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/playerlist", verify=False).json()
        except requests.exceptions.ConnectionError:
            return None
        except TypeError as exc:
            print(f"Error when fetching Playerlist: {response}")
            return None
        return [Player(**p) for p in response]

    async def fetch_gamedata(self) -> List[EventData]:
        params = {"eventID": self.current_id}
        try:
            response = requests.get("https://" + self.host + ":2999/liveclientdata/eventdata", params=params, verify=False).json()
        except Exception as exc:
            print(exc)
            return []

        event_list = []
        for e in response["Events"]:
            event_class_str = "Event" + e["EventName"]
            event_class = eval(event_class_str)
            try:
                event_list.append(event_class(**e))
            except Exception as exc:
                print(e)
        with open("./eventdata.json", "a") as f:
            f.write('\n'.join(event_list))
        return event_list

    async def tick(self) -> State:
        events = await self.fetch_gamedata()
        for e in events:
            await self.on(e)

        if any([isinstance(e, EventGameEnd) for e in events]):
            return self.builder(StateGameEnd)
        return self

    async def on(self, event: EventData):
        if event is None:
            return
        self.current_id = max(event.EventID, self.current_id) + 1
        track = self.eventdata_to_track(event)
        if track:
            await self.stop()
            await self.play(track)

    def eventdata_to_track(self, event):
        track = None
        if isinstance(event, EventChampionKill):
            if event.KillerName.startswith("Minion_"):
                team = "ORDER" if self.players[event.VictimName].team == "CHAOS" else "CHAOS"
                track = self.event_to_path(event, team=team)
            elif event.KillerName.startswith("Turret_"):
                team = "ORDER" if self.players[event.VictimName].team == "CHAOS" else "CHAOS"
                track = self.event_to_path(event, team=team)
            else:
                track = self.event_to_path(event, team=self.players[event.KillerName].team)
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
        raise NotImplementedError
