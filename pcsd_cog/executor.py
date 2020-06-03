# from pcsd_cog.events import Event, EventData
from pcsd_cog.events import *
from pcsd_cog.players import Player, FRIENDS
from redbot.core.commands import Context
from pathlib import Path
import random


class Executor():
    def __init__(self, players):
        self._events = []
        self._players = {p.summonerName: p for p in players}
        self._root = "/home/pi/pcsd_bot/data/cogs/Audio/localtracks/"

    async def run_players(self, ctx: Context, players: Player):
        tracks = []
        for p in players:
            path = Path(self._root) / "Players" / ("champion=" + p.championName.lower())
            if path.exists():
                tracks.extend([t.as_posix()[len(self._root):] for t in path.iterdir()])
        if tracks:
            print(f"Found tracks {tracks}")
            track = tracks[random.randint(0, len(tracks) - 1)]
            await ctx.bot.cogs["Audio"].command_play(ctx=ctx, query=self._root + track)


    async def run_event(self, ctx: Context, event: Event):
        track = None
        if isinstance(event, EventData):
            track = self.run_eventdata(event)
        if track:
            # response = await ctx.bot.cogs["Audio"].command_stop(ctx=ctx)
            # print(f"Got a response for now {response}")
            await ctx.bot.cogs["Audio"].command_skip(ctx=ctx)
            await ctx.bot.cogs["Audio"].command_play(ctx=ctx, query=self._root + track)
        return


    def _soundfx(self, event, *argc, **argv):
        path = Path(self._root) / type(event).__name__
        for k, v in argv.items():
            path /= f"{k}={v}"
        if path.exists():
            return [f.as_posix()[len(self._root):] for f in path.iterdir() if f.is_file()]
        else:
            return []


    def run_eventdata(self, event):
        track = None
        if type(event) == EventChampionKill:
            # TODO: specific champion kill
            if event.KillerName in FRIENDS or event.VictimName in FRIENDS:
                if event.KillerName.startswith("Minion_"):
                    team = "ORDER" if self._players[event.VictimName].team == "CHAOS" else "CHAOS"
                    track = self._soundfx(event, team=team)
                elif event.KillerName.startswith("Turret_"):
                    team = "ORDER" if self._players[event.VictimName].team == "CHAOS" else "CHAOS"
                    track = self._soundfx(event, team=team)
                else:
                    track = self._soundfx(event, team=self._players[event.KillerName].team)
        elif type(event) == EventMultikill:
            track = self._soundfx(event)
        elif type(event) == EventMinionsSpawning:
            track = self._soundfx(event)
        elif type(event) == EventTurretKilled:
            if event.KillerName.startswith("Minion_"):
                pass
            else:
                # track = self._soundfx(event, team=self._players[event.KillerName].team)
                track = self._soundfx(event)
        elif type(event) == EventDragonKill:
            track = self._soundfx(event)
        elif type(event) == EventBaronKill:
            track = self._soundfx(event)
        elif type(event) == EventHeraldKill:
            track = self._soundfx(event)
        elif type(event) == EventInhibKilled:
            track = self._soundfx(event)
        elif type(event) == EventGameEnd:
            track = self._soundfx(event, Result=event.Result)
        elif type(event) == EventGameStart:
            track = self._soundfx(event)
        elif type(event) == EventFirstBlood:
            track = self._soundfx(event)
        elif type(event) == EventInhibRespawningSoon:
            pass


        if track and isinstance(track, list):
            if len(track) > 1:
                track = track[random.randint(0, len(track) - 1)]
            else:
                track = track[0]

        return track
