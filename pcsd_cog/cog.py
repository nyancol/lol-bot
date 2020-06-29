from redbot.core import commands
import json
import asyncio
from redbot.cogs.audio.audio_dataclasses import Query
from redbot.cogs.audio.core.commands.player import PlayerCommands
from redbot.cogs.audio.core.commands.localtracks import LocalTrackCommands

from time import sleep
import lavalink

from pcsd_cog.states import StateMachine, StateLobby


class Mycog(commands.Cog):
    @commands.command()
    async def schedule(self, ctx):
        player = await lavalink.connect(ctx.author.voice.channel)
        await player.wait_until_ready()
        self.machine = StateMachine(StateLobby(ctx))
        print("Running state machine")

        async def periodic():
            while True:
                await self.machine.tick()
                await asyncio.sleep(5)

        await periodic()

    @commands.command()
    async def data_refresh(self, ctx):
        self.machine.refresh()

    @commands.command()
    async def test(self, ctx):
        machine = StateMachine(StateLobby(ctx))
        player = lavalink.get_player(ctx.guild.id)
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        query = Query.process_input("https://www.youtube.com/watch?v=Y_Vq0SPu6y8", None)

        result, called_api = await ctx.bot.cogs["Audio"].api_interface.fetch_track(ctx, player, query)
        track_music = result.tracks[0]
        player.add(ctx.author, track_music)
        await player.play()
        print("Music is now playing")
        await asyncio.sleep(30)

        game_over = "https://www.youtube.com/watch?v=1_oTEFNA_-0"
        result, called_api = await ctx.bot.cogs["Audio"].api_interface.fetch_track(ctx, player, Query.process_input(game_over, None))
        track_sfx = result.tracks[0]

        player.add(ctx.author, track_sfx)
        player.add(ctx.author, track_music)
        current_postition = player.position
        await player.skip()
        print("Starting sfx")
        while len(player.queue) != 0:
            await asyncio.sleep(1)
        await player.seek(current_postition)
        # await player.play()
        # query = Query.process_input("https://www.youtube.com/watch?v=X0DeIqJm4vM", None)
        # player.add(ctx.author, "https://www.youtube.com/watch?v=Y_Vq0SPu6y8")
        # await machine.state.play_background("https://www.youtube.com/watch?v=Y_Vq0SPu6y8")
        # player.play()
        # await machine.state.stop()
