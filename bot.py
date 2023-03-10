import discord
from discord import Colour
import random
from discord.ext import commands
import asyncio
from discord.utils import get
import yt_dlp
import aiohttp

# NzQ
token = "xODU1NTQxMTQzMjczNTky.GwvoFM.FD2BjHE8-JcKS-52-rwvRLYOwuZezZ2x_BzKnI"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

colours = [Colour.blue(), Colour.blurple(), Colour.dark_blue(), Colour.dark_gold(), Colour.dark_orange(
), Colour.dark_red(), Colour.green(), Colour.magenta(), Colour.orange(), Colour.purple(), Colour.red(), Colour.teal()]


queue = []
is_playing = False
player = None
current_song = None


async def ytbettersearch(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    index = html.find('watch?v')
    url = ""
    while True:
        char = html[index]
        if char == '"':
            break
        url += char
        index += 1
    url = f"https://www.youtube.com/{url}"
    return url


@bot.event
async def on_ready():  # checks when bot is ready
    print("Bot is ready")

@bot.command()
async def help(ctx):
    async with ctx.typing():
        n = random.randint(0, len(colours)-1)
        embed = discord.Embed(title="Music Bot by Rishabh",
                              description="Bot Commands :", colour=colours[n])
        embed.add_field(
            name="`$join`", value="Use this command to makes bot join the discord channel")
        embed.add_field(name="`$leave`", value="Leave Voice Chat")
        embed.add_field(name="`$play`", value="Play songs")
        embed.add_field(name="`$stop`", value="stops currently playing music")
        embed.add_field(name="`$resume`", value="Resumes the Queue")
        embed.add_field(name="`$pause`", value="Pauses the music")
        embed.add_field(name="`$volume`", value="Set Volume")
        embed.add_field(name="`$now_playing`", value="info about currently playing song")
        embed.add_field(name="`$clear`", value="Deleted messages")
    await ctx.send(embed=embed)


@bot.command()
async def clear(ctx, *, n: int):
    try:
        if n < 10001:
            count = n//100
            rem = n % 100
            for i in range(count):
                messages = []
                async for message in ctx.channel.history(limit=100):
                    messages.append(message)
                await ctx.channel.delete_messages(messages)
                await asyncio.sleep(1.2)
            messages = []
            async for message in ctx.channel.history(limit=(rem+1)):
                messages.append(message)
            await ctx.channel.delete_messages(messages)
            k = str(ctx.message.author)+' deleted '+str(n)+' messages.'
            async with ctx.typing():
                num = random.randint(0, len(colours)-1)
                embed = discord.Embed(
                    title="Clear", description=k, colour=colours[num])
            m = await ctx.send(embed=embed)
            await asyncio.sleep(3)
            await ctx.channel.delete_messages([m])
        else:
            async with ctx.typing():
                n = random.randint(0, len(colours)-1)
                embed = discord.Embed(
                    title="Error", description='Cannot clear more than 10,000 msgs at once.', colour=colours[n])
            await ctx.send(embed=embed)
    except:
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Error", description='Permission Error.', colour=colours[n])
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def join(ctx):
    if not ctx.message.author.voice:
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Error", description="You are not connected to a voice channel", colour=colours[n])
        await ctx.send(embed=embed)
        return
    await ctx.author.voice.channel.connect()


@bot.command()
async def play(ctx, *, url: str):
    global player, current_song
    voice = get(bot.voice_clients, guild=ctx.guild)
    if (voice and voice.is_paused()) or (voice and voice.is_playing()):
        voice.stop()
        current_song=None
    try:
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
    except:
        pass
    url = await ytbettersearch(url)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        current_song = info
        url = info['url']
        title = info['title']
    player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url))
    voice = ctx.voice_client
    voice.play(player)
    async with ctx.typing():
        n = random.randint(0, len(colours)-1)
        embed = discord.Embed(title="Now Playing", description=f"Playing {title}"+" | <@"+str(
            ctx.message.author.id)+">", colour=colours[n])
        embed.set_thumbnail(url=current_song["thumbnail"])
    await ctx.send(embed=embed)


@bot.command(aliases=['pau'])
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        voice.pause()
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="Music Paused!", colour=colours[n])
        await ctx.send(embed=embed)
    else:
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="No music Playing or some error occured.", colour=colours[n])
        await ctx.send(embed=embed)


@bot.command(aliases=['res'])
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        voice.resume()
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="Music Resumed!", colour=colours[n])
        await ctx.send(embed=embed)
    else:
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="No music Paused or some error occured.", colour=colours[n])
        await ctx.send(embed=embed)


@bot.command(aliases=['lev'])
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()


@bot.command()
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if (voice and voice.is_paused()) or (voice and voice.is_playing()):
        voice.stop()
        current_song = None
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="Current Music Stopped and Removed from queue!", colour=colours[n])
        await ctx.send(embed=embed)
    else:
        async with ctx.typing():
            n = random.randint(0, len(colours)-1)
            embed = discord.Embed(
                title="Voice", description="No music Paused or Playing or some error occured.", colour=colours[n])
        await ctx.send(embed=embed)


@bot.command(aliases=['vol'])
async def volume(ctx, vol: float):
    global player
    voice = ctx.voice_client
    voice.source.volume = (vol/100)
    async with ctx.typing():
        author = ctx.message.author.id
        # volume should be a float between 0 to 1
        n = random.randint(0, len(colours)-1)
        embed = discord.Embed(
            title="Volume", description=f"Changed volume to {voice.source.volume*100}%"+" | <@"+str(author)+">", colour=colours[n])
    await ctx.send(embed=embed)

def generate_progress_bar(song):
    total_time = song.duration.total_seconds()
    current_time = song.player.progress().total_seconds()
    progress_percent = current_time / total_time
    
    progress_bar_length = 20
    filled_length = round(progress_percent * progress_bar_length)
    empty_length = progress_bar_length - filled_length
    
    return "▬" * filled_length + "🔘" + "▬" * empty_length

@bot.command()
async def now_playing(ctx):
    if not player:
        current_song = None
        return await ctx.send("There is no music playing right now.")
    title = current_song["title"]
    embed = discord.Embed(title=f"Now Playing: {title}",
                            color=discord.Color.green())
    embed.set_thumbnail(url=current_song["thumbnail"])
    await ctx.send(embed=embed)

bot.run(token)
