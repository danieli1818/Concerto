from discord.ext import commands

import os

import utils

import youtube_dl

from youtube_search import YoutubeSearch

from dotenv import load_dotenv

from youtube_utils import YTDLSource

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = os.getenv('COMMAND_PREFIX')
YOUTUBE_URI = os.getenv('YOUTUBE_URI')


class PotterCord:

    def __init__(self, bot_token, bot_prefix):
        self.bot = commands.Bot(command_prefix=bot_prefix)
        self.token = bot_token
        self.players = {}
        self.music_queues = {}
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
            elif args_length >= 1:
                song = " ".join(args)
                song_uri = None
                if utils.youtube_url_validation(song):
                    # URI
                    song_uri = song
                else:
                    results = YoutubeSearch(song, 1).to_dict()
                    if len(results) > 0:
                        song_uri = YOUTUBE_URI + results[0]["url_suffix"]
                if song_uri is not None:
                    await self.play_youtube_song_by_uri(song_uri, voice_channel, ctx)
                else:
                    await ctx.send(
                        "{0.mention} Didn't find song {1}!!!".format(author, song))
            print(args)

    async def play_youtube_song_by_uri(self, uri, channel, ctx):
        if channel is None:
            return False
        else:
            print("before join voice channel")
            voice = await self.join_voice_channel(channel)
            print("after join voice channel")
            await self.play(ctx, uri, voice)
            # server = channel.guild
            # voice_client = server.voice_client
            # print("before player creation")
            # player = await voice.create_ytdl_player(uri)
            # print("after player creation")
            # self.players[server.id] = player
            # print("before player playing")
            # player.start()
            # print("after player playing")

    async def play(self, ctx, uri, voice):

        async def play_next_song(e=None):
            print("yay")
            if e:
                print('Player error: %s' % e)
                return
            if not self.music_queues[server.id]:
                return
            async with ctx.typing():
                player = await YTDLSource.from_url(self.music_queues[server.id].pop(0), loop=self.bot.loop)
                # after=lambda e: print('Player error: %s' % e) if e else await play_next_song()
                voice.play(player, after=await play_next_song())
            await ctx.send('Now playing: {0}\nhttps://{1}'.format(player.title, uri))

        print(uri)
        server = ctx.message.guild
        voice_client = server.voice_client

        if server.id not in self.music_queues.keys():
            self.music_queues[server.id] = []
        self.music_queues[server.id].append(uri)

        if not voice_client.is_playing():
            print("check")
            await play_next_song()



    async def join_voice_channel(self, channel):
        server = channel.guild
        voice_client = server.voice_client
        if voice_client is None:
            print("voice_client is None!")
        elif voice_client.is_connected():
            if voice_client.channel.id != channel.id:
                await self.disconnect_voice_channel(server)
            else:
                return True
        return await channel.connect()

    async def disconnect_voice_channel(self, server):
        voice_client = server.voice_client
        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()

    def run(self):
        self.bot.run(self.token)


PotterCord(TOKEN, BOT_PREFIX).run()
