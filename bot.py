from discord.ext import commands

import os

import utils

import youtube_dl

from dotenv import load_dotenv

from youtube_utils import YTDLSource

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = os.getenv('COMMAND_PREFIX')


class PotterCord:

    def __init__(self, bot_token, bot_prefix):
        self.bot = commands.Bot(command_prefix=bot_prefix)
        self.token = bot_token
        self.players = {}
        self.on_ready()

    def on_ready(self):

        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user.name} has connected to Discord!')

        @self.bot.command(name='play')
        async def play(ctx, *args):
            author = ctx.message.author
            voice_channel = author.voice.channel
            args_length = args.__len__()
            if voice_channel is None:
                await ctx.send("{0.mention} You Have To Be In A Voice Channel To Run This Command!")
            elif args_length == 0:
                await ctx.send("{0.mention} Invalid Command Needs To Add A Song Name Or A Song URI!!!".format(author))
            elif args_length == 1:
                if utils.youtube_url_validation(args[0]):
                    await self.play_youtube_song_by_uri(args[0], voice_channel, ctx)
            print(args)

    async def play_youtube_song_by_uri(self, uri, channel, ctx):
        if channel is None:
            return False
        else:
            print("before join voice channel")
            voice = await self.join_voice_channel(channel)
            print("after join voice channel")
            await self.play(ctx, uri)
            # server = channel.guild
            # voice_client = server.voice_client
            # print("before player creation")
            # player = await voice.create_ytdl_player(uri)
            # print("after player creation")
            # self.players[server.id] = player
            # print("before player playing")
            # player.start()
            # print("after player playing")

    async def play(self, ctx, uri):
        print(uri)
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(uri, loop=self.bot.loop)
            ctx.voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))

    async def join_voice_channel(self, channel):
        server = channel.guild
        voice_client = server.voice_client
        if voice_client is None:
            print("voice_client is None!")
        elif voice_client.is_connected() and voice_client.channel.id != channel.id:
            await self.disconnect_voice_channel(server)
        return await channel.connect()

    async def disconnect_voice_channel(self, server):
        voice_client = server.voice_client
        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()

    def run(self):
        self.bot.run(self.token)


PotterCord(TOKEN, BOT_PREFIX).run()
