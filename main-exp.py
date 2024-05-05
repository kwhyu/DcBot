import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import youtube_dl

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ALLOWED_SERVER_ID = int(os.getenv('YOUR_SERVER_ID'))
ALLOWED_PERMISSIONS = 8

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.members = True
intents.presences = True
intents.voice_states = True
intents.dm_messages = True
intents.typing = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    print(bot.guilds)
    # Menemukan server dengan ID yang ditentukan
    server = discord.utils.get(bot.guilds, id=ALLOWED_SERVER_ID)
    # Memberi tahu bahwa bot telah terhubung ke server
    if server:
        print(f'{bot.user.name} is now connected to the server {server.name}!')

@bot.event
async def on_message(message):
    # Memastikan bot tidak merespons pesan yang dikirim oleh dirinya sendiri
    if message.author == bot.user:
        return

    # Memastikan pesan yang diterima dari saluran (channel) server, bukan DM (Direct Message)
    if isinstance(message.channel, discord.TextChannel):
        # Memeriksa izin pengguna untuk mengirim pesan
        if message.author.guild_permissions.value & ALLOWED_PERMISSIONS:
            # Memastikan pesan tidak kosong atau hanya berisi spasi
            if message.content.strip():
                # Cetak informasi lengkap pesan yang diterima ke log terminal
                print(f"Received message: '{message.content}' from user '{message.author.name}' in server '{message.guild.name}'")
            
            # Tambahkan logika untuk menanggapi pesan dengan awalan '!ey'
            if message.content.startswith('!ey'):
                await message.channel.send('Hello!')
        else:
            await message.channel.send('Anda tidak memiliki izin untuk menggunakan perintah ini!')

    # Meneruskan pesan ke command handler jika dimulai dengan prefix
    await bot.process_commands(message)

@bot.command(name='hello', help='Says hello to the user')
async def hello(ctx):
    responses = ["Hello!", "Hi there!", "Hey!"]
    response = random.choice(responses)
    await ctx.send(response)

@bot.command(name='goodbye', help='Says goodbye to the user')
async def goodbye(ctx):
    responses = ["Goodbye!", "See you later!", "Bye bye!"]
    response = random.choice(responses)
    await ctx.send(response)

@bot.command(name='roll_dice', help='Rolls a dice')
async def roll_dice(ctx):
    dice_sides = 6
    dice_roll = random.randint(1, dice_sides)
    await ctx.send(f"The dice rolled a {dice_roll}!")

@bot.command(name='coin_flip', help='Flips a coin')
async def coin_flip(ctx):
    outcomes = ["Heads", "Tails"]
    outcome = random.choice(outcomes)
    await ctx.send(f"The coin landed on {outcome}!")

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    await ctx.send(":thumbsup:")
    await ctx.send(file=discord.File("aaa.png"))

@bot.command(name='play', help='Plays music in a voice channel')
async def play(ctx, url: str):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    voice_channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()
    else:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: print('done', e))

@bot.command(name='invite', help='Invites the bot to join a voice channel')
async def invite(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return

    voice_channel = ctx.message.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await voice_channel.connect()
    else:
        if voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

bot.run(TOKEN)
