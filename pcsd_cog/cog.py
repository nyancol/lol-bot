from redbot.core import commands
import json
import asyncio
from redbot.cogs.audio.audio_dataclasses import Query
from redbot.cogs.audio.core.commands.player import PlayerCommands
from redbot.cogs.audio.core.commands.localtracks import LocalTrackCommands

from pcsd_cog.states import StateMachine, StateLobby


class Mycog(commands.Cog):
    @commands.command()
    async def schedule(self, ctx):
        machine = StateMachine(StateLobby(ctx))
        print("Running state machine")

        async def periodic():
            while True:
                await machine.tick()
                await asyncio.sleep(1)

        await periodic()
