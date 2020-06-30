from redbot.core import commands
import json
import asyncio
from redbot.cogs.audio.core.commands.player import PlayerCommands
from redbot.cogs.audio.core.commands.localtracks import LocalTrackCommands
from redbot.cogs.audio.audio_dataclasses import Query


from time import sleep
import lavalink

from pcsd_cog.states import StateMachine, StateLobby


class Mycog(commands.Cog):
    @commands.command()
    async def schedule(self, ctx):
        # player = await lavalink.connect(ctx.author.voice.channel)
        await lavalink.connect(ctx.author.voice.channel)
        player = lavalink.get_player(ctx.guild.id)
        await player.wait_until_ready()
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        self.machine = StateMachine(StateLobby(player))
        print("Running state machine")

        async def periodic():
            while True:
                await self.machine.tick()
                await asyncio.sleep(1)

        await periodic()

    @commands.command()
    async def data_refresh(self, ctx):
        self.machine.refresh()

    @commands.command()
    async def test(self, ctx):
        # print(f"Guild id: {ctx.guild.id} - {type(ctx.guild.id)}")
        # print(f"Channel id: {ctx.channel.id} - {type(ctx.channel.id)}")
        # player = lavalink.get_player(ctx.guild_id)
        # from discord.channel import VoiceChannel
        # channel = VoiceChannel
        # player = await lavalink.connect(ctx.author.voice.channel)
        await lavalink.connect(ctx.author.voice.channel)
        player = lavalink.get_player(ctx.guild.id)
        await player.wait_until_ready()
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        results = await player.load_tracks("https://youtu.be/KMTRqAgLw04")
        player.add(ctx.author, results.tracks[0])
        await player.play()
        # print("Music is now playing")
        # await asyncio.sleep(30)

        # game_over = "https://www.youtube.com/watch?v=1_oTEFNA_-0"
        # result, called_api = await ctx.bot.cogs["Audio"].api_interface.fetch_track(ctx, player, Query.process_input(game_over, None))
        # track_sfx = result.tracks[0]

        # player.add(ctx.author, track_sfx)
        # player.add(ctx.author, track_music)
        # current_postition = player.position
        # await player.skip()
        # print("Starting sfx")
        # while len(player.queue) != 0:
        #     await asyncio.sleep(1)
        # await player.seek(current_postition)
        # await player.play()
        # query = Query.process_input("https://www.youtube.com/watch?v=X0DeIqJm4vM", None)
        # player.add(ctx.author, "https://www.youtube.com/watch?v=Y_Vq0SPu6y8")
        # await machine.state.play_background("https://www.youtube.com/watch?v=Y_Vq0SPu6y8")
        # player.play()
        # await machine.state.stop()
