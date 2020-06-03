from redbot.core import commands
import json
import asyncio
from redbot.cogs.audio.audio_dataclasses import Query
from redbot.cogs.audio.core.commands.player import PlayerCommands
from redbot.cogs.audio.core.commands.localtracks import LocalTrackCommands

from pcsd_cog import events
from pcsd_cog.executor import Executor
from pcsd_cog.fetcher import Fetcher


class Mycog(commands.Cog):
    @commands.command()
    async def schedule(self, ctx):
        fetcher = Fetcher()

        players = fetcher.playerlist()
        while not players:
            players = fetcher.playerlist()
            await asyncio.sleep(10)

        print(f"Found players list {players}")
        executor = Executor(players)
        await executor.run_players(ctx, players)
        async def periodic():
            while True:
                for e in fetcher.eventdata():
                    await executor.run_event(ctx, e)
                await asyncio.sleep(1)
        await periodic()
