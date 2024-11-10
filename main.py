from typing import Final
import os
from dotenv import load_dotenv
import discord
from discord import Intents, Client, Message, Embed, VoiceChannel, Guild, Member, File, Activity, ActivityType, ButtonStyle
from discord.ext import commands
from discord import FFmpegPCMAudio
import random
from easy_pil import Editor, load_image_async, Font
from responses import get_response
import openai
import random
import asyncio
from discord.ui import Button, View
import yt_dlp
import urllib.parse, urllib.request
import re
from pymongo import MongoClient
import math
import time
import requests

# Memuat token dari file .env
#load_dotenv()
#TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Game Items
ITEMS = {
    "🌱": "Seed",           # Level 1
    "🌾": "Plant",          # Level 2
    "🍎": "Fruit",          # Level 3
    "🧺": "Basket",         # Level 4
    "🥖": "Bread"           # Level 5
}

# Define merging rules
MERGE_RULES = {
    "🌱🌱": "🌾",  # Two Seeds make a Plant
    "🌾🌾": "🍎",  # Two Plants make a Fruit
    "🍎🍎": "🧺",  # Two Fruits make a Basket
    "🧺🧺": "🥖"   # Two Baskets make Bread
}

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CUSTOM_ACTIVITY_ID = os.getenv('CUSTOM_ACTIVITY_ID')

#Mongo DB
MONGO_URL = os.getenv('MONGO_URL')

#API
API_URL_POST = os.getenv("API_URL_POST")
API_URL_UPDATE = os.getenv("API_URL_UPDATE")
API_URL_DELETE = os.getenv("API_URL_DELETE")

# Ensure the variables are correctly loaded
if not MONGO_URL:
    raise ValueError("MongoDB URL is not set in the environment variables.")
if not TOKEN:
    raise ValueError("Discord token is not set in the environment variables.")
    
try:
    client_mongo = MongoClient(MONGO_URL)
    db = client_mongo['db_nais']
    user_collection = db['user_chat_data']
    print("MongoDB connection established.")
except Exception as e:
    raise Exception("Error connecting to MongoDB: ", e)

# Pengaturan bot
intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)

class Player:
    def __init__(self, member):
        self.member = member
        self.inventory = {
            "🌱": 2,  # Start with two seeds
            "🌾": 0,
            "🍎": 0,
            "🧺": 0,
            "🥖": 0
        }

    def get_inventory(self):
        return "\n".join([f"{emoji}: {count}" for emoji, count in self.inventory.items() if count > 0])

    def merge_items(self, item1, item2):
        key = f"{item1}{item2}"
        if key in MERGE_RULES:
            new_item = MERGE_RULES[key]
            self.inventory[item1] -= 1
            self.inventory[item2] -= 1
            self.inventory[new_item] += 1
            return new_item
        return None

# Store players in an active game
active_games = {}

openai.api_key = OPENAI_API_KEY

playlist = ['Kerusu/Kerusu1.mp3', 'Kerusu/Kerusu2.mp3', 'Kerusu/Kerusu3.mp3',
            'Kerusu/Kerusu4.mp3', 'Kerusu/Kerusu5.mp3', 'Kerusu/Kerusu6.mp3',
            'Kerusu/Kerusu7.mp3', 'Kerusu/Kerusu8.mp3', 'Kerusu/Kerusu9.mp3',
            'Kerusu/Kerusu10.mp3', 'Kerusu/Kerusu11.mp3', 'Kerusu/Kerusu12.mp3',
            'Kerusu/Kerusu13.mp3', 'Kerusu/Kerusu14.mp3', 'Kerusu/Kerusu15.mp3']
afrojack =['Kerusu/Kerusu1.mp3']


ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"',
    'executable': 'C:\FFmpeg\bin' 
}

# ID saluran sambutan
WELCOME_CHANNEL_ID: Final[int] = 1227942494684057705
WELCOME_CHANNEL_ID2: Final[int] = 916557804150591492

WELCOME_IMAGE: Final[str] = "pic1.jpg"

async def send_welcome_message(channel_id: int, member: Member):
    channel = member.guild.get_channel(channel_id)
    if channel is not None:
        background = Editor(WELCOME_IMAGE)
        profile_image = await load_image_async(str(member.display_avatar.url))

        profile = Editor(profile_image).resize((150, 150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")
        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)
        background.text((400, 260), f"WELCOME to {member.guild.name}", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}#{member.discriminator}", color="white", font=poppins_small, align="center")

        file = File(fp=background.image_bytes, filename="welcome.jpg")
        await channel.send(f"Hello {member.mention}! Welcome to **{member.guild.name}**. For more information, go to #get-roles.")
        await channel.send(file=file)
    else:
        print(f"Channel with ID {channel_id} not found.")

@client.event
async def on_member_join(member: Member):
    await send_welcome_message(WELCOME_CHANNEL_ID, member)
    await send_welcome_message(WELCOME_CHANNEL_ID2, member)

# @client.tree.command(name="help", description="List of available commands and their descriptions")
# async def help_command(interaction: discord.Interaction):
#     embed = discord.Embed(title="Bot Commands", description="Here is a list of commands you can use:", color=discord.Color.blue())
    
#     embed.add_field(name="/ping", value="Check bot's latency.", inline=False)
#     embed.add_field(name="/kwhy", value="Just a fun greeting command.", inline=False)
#     embed.add_field(name="/play-music", value="Play music in the voice channel.", inline=False)
#     embed.add_field(name="/leave-voice", value="Bot leaves the voice channel.", inline=False)
#     embed.add_field(name="/join-voice", value="Invite bot to your current voice channel.", inline=False)
#     embed.add_field(name="/marketplace", value="Access the marketplace.", inline=False)
#     embed.add_field(name="/roll-dice", value="Roll a six-sided die.", inline=False)
#     embed.add_field(name="/chatgpt", value="Send a prompt to ChatGPT.", inline=False)
#     embed.add_field(name="/start-merge-game", value="Start a merge game.", inline=False)
#     embed.add_field(name="/inventory", value="Check your inventory in the merge game.", inline=False)
#     embed.add_field(name="/merge", value="Merge two items in the merge game.", inline=False)
#     embed.add_field(name="/end-merge-game", value="End the merge game.", inline=False)
#     embed.add_field(name="/launch-custom-activity", value="Launch a custom activity in a voice channel.", inline=False)
#     embed.add_field(name="/echo", value="Send an anonymous message.", inline=False)
#     embed.add_field(name="/random", value="Get a random selection from a list.", inline=False)
#     embed.add_field(name="/settings", value="Open the dashboard to configure the bot.", inline=False)
#     embed.add_field(name="/snake-game", value="Play snake game.", inline=False)
#     embed.add_field(name="/play", value="Play youtube", inline=False)
#     embed.add_field(name="/play", value="Stop youtube", inline=False)



#     await interaction.response.send_message(embed=embed)

@client.tree.command(name="help", description="List of available commands and their descriptions")
async def help_command(interaction: discord.Interaction):
    # Embed untuk tampilan yang rapi
    embed = discord.Embed(
        title="Bot Commands",
        description="Here is a list of commands you can use:",
        color=discord.Color.blue()  # Warna biru untuk embed
    )

    # Menambahkan field untuk setiap command dengan deskripsinya
    embed.add_field(name="/ping", value="Check the bot's latency.", inline=False)
    embed.add_field(name="/kwhy", value="Just a fun greeting command.", inline=False)
    embed.add_field(name="/play-music", value="Play music in the voice channel.", inline=False)
    embed.add_field(name="/leave-voice", value="Bot leaves the voice channel.", inline=False)
    embed.add_field(name="/join-voice", value="Invite bot to your current voice channel.", inline=False)
    embed.add_field(name="/marketplace", value="Access the marketplace.", inline=False)
    embed.add_field(name="/roll-dice", value="Roll a six-sided die.", inline=False)
    embed.add_field(name="/chatgpt", value="Send a prompt to ChatGPT.", inline=False)
    embed.add_field(name="/start-merge-game", value="Start a merge game.", inline=False)
    embed.add_field(name="/inventory", value="Check your inventory in the merge game.", inline=False)
    embed.add_field(name="/merge", value="Merge two items in the merge game.", inline=False)
    embed.add_field(name="/end-merge-game", value="End the merge game.", inline=False)
    embed.add_field(name="/launch-custom-activity", value="Launch a custom activity in a voice channel.", inline=False)
    embed.add_field(name="/echo", value="Send an anonymous message.", inline=False)
    embed.add_field(name="/random", value="Get a random selection from a list.", inline=False)
    embed.add_field(name="/settings", value="Open the dashboard to configure the bot.", inline=False)

    # Membuat button untuk /help
    button = discord.ui.Button(label="Get Help", style=discord.ButtonStyle.primary)

    # Fungsi callback saat tombol ditekan
    async def button_callback(interaction: discord.Interaction):
        await interaction.response.send_message(embed=embed)

    # Menetapkan callback ke tombol
    button.callback = button_callback

    # Membuat view untuk tombol
    view = discord.ui.View()
    view.add_item(button)

    # Kirim embed dengan view (tombol)
    await interaction.response.send_message(embed=embed, view=view)
    
@client.tree.command(name="settings", description="Open the bot's settings dashboard")
async def settings_command(interaction: discord.Interaction):
    dashboard_url = "https://puffy-hazel-freckle.glitch.me/"  # Ganti dengan URL yang sesuai
    await interaction.response.send_message(f"You can configure the bot's settings here: [Dashboard]({dashboard_url})")

@client.tree.command(name="ping", description="Cek latensi bot")
async def ping_command(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong! Latensi: {latency} ms")

@client.tree.command(name="kwhy", description="Kwhy is good")
async def kwhy_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello Minna sama")

@client.tree.command(name="play-music", description="Play music in the voice channel")
async def play_music_command(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("I'm not connected to a voice channel. Use /join-voice to invite me.")
        return
    if voice_client.is_playing():
        await interaction.response.send_message("I'm already playing music.")
        return

    # Define a function to play the audio source and loop through the playlist
    def play_audio_source(error):
        if error:
            print(f'Player error: {error}')
            return

        # Get the next song in the playlist
        next_song = playlist.pop(0)
        playlist.append(next_song)

        audio_source = FFmpegPCMAudio(next_song)
        voice_client.play(audio_source, after=play_audio_source)

    # Start playing the first song in the playlist
    first_song = playlist.pop(0)
    playlist.append(first_song)
    audio_source = FFmpegPCMAudio(first_song)
    voice_client.play(audio_source, after=play_audio_source)

    await interaction.response.send_message("Now playing music on loop!")


@client.tree.command(name="leave-voice", description="Leave the voice channel")
async def leave_voice_command(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.response.send_message("Bot has left the voice channel.")
    else:
        await interaction.response.send_message("Bot is not connected to a voice channel.")

@client.tree.command(name="join-voice", description="Invite Kwhy to Voice Channel")
async def join_voice_command(interaction: discord.Interaction):
    member = interaction.user
    if member.voice and member.voice.channel:
        voice_channel = member.voice.channel
        await voice_channel.connect()
        await interaction.response.send_message("Bot has been invited to the voice channel.")
    else:
        await interaction.response.send_message("You must be connected to a voice channel to invite the bot.")

@client.tree.command(name="marketplace", description="Access the marketplace")
async def marketplace_command(interaction: discord.Interaction):
    items = [
        {'name': 'Item 1', 'price': 10, 'emoji': '⚔️'},
        {'name': 'Item 2', 'price': 20, 'emoji': '🛡️'},
        {'name': 'Item 3', 'price': 30, 'emoji': '🔮'}
    ]

    embed = Embed(title='Marketplace', description='Welcome to the marketplace!')
    for item in items:
        embed.add_field(name=f"{item['emoji']} {item['name']}", value=f"Price: ${item['price']}", inline=False)

    await interaction.response.send_message(embed=embed)

    for item in items:
        await interaction.message.add_reaction(item['emoji'])

    await interaction.followup.send("React to the item you want to buy.")

# Fungsi untuk mengocok dadu
def roll_dice(num_dice: int, num_faces: int) -> str:
    if num_dice != 1 or num_faces != 6:
        return "Invalid dice configuration. Please roll one 6-faced die."
    roll_result = random.randint(1, 6)
    return f"The result of rolling a 6-sided die: {roll_result}"

@client.tree.command(name="roll-dice", description="Roll a six-sided die")
async def roll_dice_command(interaction: discord.Interaction, num_dice: int = 1, num_faces: int = 6):
    result = roll_dice(num_dice, num_faces)
    await interaction.response.send_message(result)

async def get_chatgpt_response(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            model="text-curie-001", 
            prompt=prompt,
            max_tokens=100,  
            temperature=0.7, 
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error while fetching response: {str(e)}"

@client.tree.command(name="chatgpt", description="Send a prompt to ChatGPT")
async def chatgpt_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer() 
    response = await get_chatgpt_response(prompt) 
    await interaction.followup.send(response)

@client.tree.command(name="start-merge-game", description="Start a merge game")
async def start_merge_game(interaction):
    member = interaction.user
    if member.id not in active_games:
        active_games[member.id] = Player(member)
        await interaction.response.send_message(f"{member.mention}, the merge game has started! Use /inventory to check your items.")
    else:
        await interaction.response.send_message("You are already in a game!")

@client.tree.command(name="inventory", description="Check your inventory")
async def inventory_command(interaction):
    member = interaction.user
    if member.id in active_games:
        player = active_games[member.id]
        inventory = player.get_inventory()
        await interaction.response.send_message(f"Your inventory:\n{inventory}")
    else:
        await interaction.response.send_message("You are not in a merge game. Start one with /start-merge-game.")

@client.tree.command(name="merge", description="Merge two items")
async def merge_command(interaction, item1: str, item2: str):
    member = interaction.user
    if member.id in active_games:
        player = active_games[member.id]
        new_item = player.merge_items(item1, item2)
        if new_item:
            await interaction.response.send_message(f"You merged {item1} and {item2} to create {new_item}!")
        else:
            await interaction.response.send_message("Merge failed! Check your items or the merge rules.")
    else:
        await interaction.response.send_message("You are not in a merge game. Start one with /start-merge-game.")

@client.tree.command(name="end-merge-game", description="End the merge game")
async def end_merge_game(interaction):
    member = interaction.user
    if member.id in active_games:
        del active_games[member.id]
        await interaction.response.send_message(f"{member.mention}, your merge game has ended.")
    else:
        await interaction.response.send_message("You are not in a merge game.")


@client.tree.command(name="random", description="Get random from your list")
async def random_command(interaction: discord.Interaction, names: str):
    # Memisahkan nama-nama yang dipisahkan dengan spasi
    name_list = names.split()
    
    if not name_list:
        await interaction.response.send_message("Please provide at least one name.")
        return

    # Memilih nama secara acak dari daftar
    random_name = random.choice(name_list)

    # Mengirimkan hasil ke channel
    await interaction.response.send_message(f"Randomly selected name: {random_name}")

@client.tree.command(name="launch-custom-activity", description="Launch your custom activity in the voice channel")
async def launch_custom_activity(interaction: discord.Interaction):
    # Periksa apakah user berada di voice channel
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You need to be in a voice channel to launch an activity.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    try:
        # Membuat invite untuk aktivitas di voice channel
        invite = await voice_channel.create_activity_invite(int(CUSTOM_ACTIVITY_ID))  # Pastikan ID diubah ke integer
        await interaction.response.send_message(f"Click here to join the custom activity: {invite.url}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to launch the custom activity: {e}", ephemeral=True)

@client.tree.command(name="echo", description="Chat anonim melalui bot")
async def echo_command(interaction: discord.Interaction, message: str):
    """
    Command untuk chat anonim, bot akan mengirim pesan yang dimasukkan pengguna tanpa menampilkan siapa yang memicu command.
    """
    try:
        # Menunda tanggapan ke pengguna agar tidak ada jejak command yang dijalankan
        await interaction.response.defer(ephemeral=True)

        # Bot mengirim pesan ke channel secara anonim
        channel = interaction.channel
        await channel.send(message)  # Bot mengirim pesan ke channel atas namanya sendiri
    except Exception as e:
        # Jika terjadi kesalahan, berikan pesan error hanya ke pengguna yang menjalankan command
        await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)

            
# Fungsi untuk mengirim pesan berdasarkan input pengguna
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Pesan kosong karena intents mungkin tidak diaktifkan)')
        return

    is_private = user_message[0] == '?'
    if is_private:
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)

# Menangani startup bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} sekarang aktif!')
    await client.tree.sync()

# Menangani pesan masuk
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    user_id = str(message.author.id)
    # Fetch user data from MongoDB
    user_data = user_collection.find_one({'id_user': user_id})
    
    if user_data:
        chat_count = user_data['chat_count'] + 1  # Increment chat count
        level = user_data['level']
    else:
        chat_count = 1
        level = 0

    # Calculate new level
    new_level = calculate_level(chat_count)

    # Update or insert user data in MongoDB
    if user_data:
        user_collection.update_one(
            {'id_user': user_id}, 
            {'$set': {'chat_count': chat_count, 'level': new_level}}
        )
    else:
        user_collection.insert_one({
            'id_user': user_id,
            'chat_count': chat_count,
            'level': new_level
        })

    # Send a message if the user's level increased
    if new_level > level:
        await message.channel.send(f"{message.author.mention}, congratulations! You've reached level {new_level}!")

    await send_message(message, user_message)


# GAME SECTION

# Ukuran papan permainan
BOARD_SIZE = 10

# Simbol untuk bagian ular dan makanan
SNAKE_CHAR = "🐍"
FOOD_CHAR = "🍎"
EMPTY_CHAR = "⬛"

# Perintah arah
DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1)
}

# Snake Game class
class SnakeGame:
    def __init__(self, ctx):
        self.ctx = ctx
        self.board = [[EMPTY_CHAR for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.snake = [(BOARD_SIZE // 2, BOARD_SIZE // 2)]  # Start di tengah
        self.direction = DIRECTIONS["up"]
        self.food = self.place_food()
        self.score = 0
        self.game_over = False

    def place_food(self):
        while True:
            x, y = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
            if (x, y) not in self.snake:
                self.board[x][y] = FOOD_CHAR
                return (x, y)

    def render_board(self):
        board_copy = [row[:] for row in self.board]
        for x, y in self.snake:
            board_copy[x][y] = SNAKE_CHAR
        return "\n".join("".join(row) for row in board_copy)

    def move_snake(self):
        # Hitung posisi baru kepala ular
        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        # Periksa jika ular menabrak dinding atau tubuhnya sendiri
        if (
            new_head[0] < 0 or new_head[0] >= BOARD_SIZE or
            new_head[1] < 0 or new_head[1] >= BOARD_SIZE or
            new_head in self.snake
        ):
            self.game_over = True
            return

        # Jika makan makanan
        if new_head == self.food:
            self.snake = [new_head] + self.snake  # Perpanjang ular
            self.food = self.place_food()  # Tempatkan makanan baru
            self.score += 1
        else:
            self.snake = [new_head] + self.snake[:-1]  # Gerakkan ular

# View untuk tombol kontrol
class SnakeControlView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="⬆️", style=ButtonStyle.primary)
    async def up_button(self, interaction: discord.Interaction, button: Button):
        self.game.direction = DIRECTIONS["up"]
        await self.update_game(interaction)

    @discord.ui.button(label="⬅️", style=ButtonStyle.primary)
    async def left_button(self, interaction: discord.Interaction, button: Button):
        self.game.direction = DIRECTIONS["left"]
        await self.update_game(interaction)

    @discord.ui.button(label="⬇️", style=ButtonStyle.primary)
    async def down_button(self, interaction: discord.Interaction, button: Button):
        self.game.direction = DIRECTIONS["down"]
        await self.update_game(interaction)

    @discord.ui.button(label="➡️", style=ButtonStyle.primary)
    async def right_button(self, interaction: discord.Interaction, button: Button):
        self.game.direction = DIRECTIONS["right"]
        await self.update_game(interaction)

    async def update_game(self, interaction):
        # Update pergerakan ular tanpa menunggu masukan dari pengguna
        self.game.move_snake()
        if self.game.game_over:
            await interaction.response.edit_message(content=f"Game Over! Skor akhir: {self.game.score}", view=None)
            await self.game.ctx.channel.send(f"{self.game.ctx.user.mention} mendapatkan skor {self.game.score}!")
        else:
            embed = discord.Embed(title="Snake Game", description=f"Skor: {self.game.score}\n{self.game.render_board()}")
            await interaction.response.edit_message(embed=embed)

# Loop permainan otomatis
async def game_loop(game, interaction):
    while not game.game_over:
        game.move_snake()
        if game.game_over:
            # Kirim hasil akhir yang dapat dilihat semua orang
            await interaction.edit_original_response(content=f"Game Over! Skor akhir: {game.score}", view=None)
            await game.ctx.channel.send(f"{game.ctx.user.mention} mendapatkan skor {game.score}!")
        else:
            # Update board untuk pemain, tapi tetap ephemeral selama permainan belum selesai
            embed = discord.Embed(title="Snake Game", description=f"Skor: {game.score}\n{game.render_board()}")
            await interaction.edit_original_response(embed=embed)
        await asyncio.sleep(0.5)

# Slash Command untuk memulai game
@client.tree.command(name="snake-game", description="play snake game")
async def start_game(interaction: discord.Interaction):
    game = SnakeGame(interaction)
    embed = discord.Embed(title="Snake Game", description=f"Skor: {game.score}\n{game.render_board()}")

    # Menambahkan kontrol dengan tombol di bawah kanvas
    view = SnakeControlView(game)
    
    # Kirim pesan pertama dengan ephemeral=True, hanya terlihat oleh pemain
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
    
    # Mulai loop permainan otomatis
    await game_loop(game, interaction)


# Command to provide the link to the FPS game
@client.tree.command(name="fps", description="Get the link to the FPS game")
async def game_link_command(interaction: discord.Interaction):
    try:
        game_url = "https://fpsaimlabfakecopyoioi.netlify.app/"
        await interaction.response.send_message(f"P main gim: {game_url}", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)


#YOUTUBE

# Queue untuk autoplay
music_queue = []
autoplay_enabled = False
stay_in_channel = False
# last_played_url = None
last_search_time = 0 
search_cooldown = 5
current_song_title = None
current_song_info = {"title": None, "url": None}
current_video_url = None


# YoutubeDL options
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': 'True'
}

# Fungsi untuk memutar lagu
async def play_music(interaction: discord.Interaction, url: str):
    global current_song_title, current_video_url
    try:
        voice_client = interaction.guild.voice_client
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2)
            
            current_song_title = info['title']  # Simpan judul lagu yang sedang diputar
            current_video_url = url  # Simpan URL video yang sedang diputar
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(interaction), client.loop))
            
            await interaction.followup.send(f"Memutar lagu: {current_song_title}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)


# Fungsi untuk menemukan lagu berikutnya dengan jeda antar pencarian
async def find_next_song(current_video_url: str):
    # Ambil ID video dari URL video saat ini
    video_id = current_video_url.split('v=')[-1]
    
    # Mencari video terkait di YouTube berdasarkan ID video saat ini
    related_url = f"http://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
    html_content = urllib.request.urlopen(related_url)
    search_results = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())

    # Memastikan tidak mengembalikan video yang sama sebagai rekomendasi
    for video in search_results:
        if video != video_id:
            return f"http://www.youtube.com/watch?v={video}"

    # Jika tidak ada rekomendasi yang ditemukan, naikkan pengecualian
    raise Exception("Gagal menemukan lagu otomatis berikutnya.")

# Fungsi untuk memainkan lagu berikutnya atau mencari lagu secara otomatis
async def next_song(interaction: discord.Interaction):
    global music_queue, autoplay_enabled, current_song_title, current_video_url

    if music_queue:
        # Jika ada lagu di antrian, putar lagu berikutnya dari antrian
        next_song_url = music_queue.pop(0)
        await play_music(interaction, next_song_url)
    elif autoplay_enabled and current_song_title:
        # Jika antrian kosong dan autoplay diaktifkan, cari lagu otomatis dari rekomendasi YouTube
        next_song_url = await find_next_song(current_video_url)
        await play_music(interaction, next_song_url)
    else:
        # Jika antrian kosong dan autoplay dinonaktifkan
        await interaction.followup.send("Tidak ada lagu di antrian dan autoplay dinonaktifkan.", ephemeral=True)


# Command untuk memutar lagu dari URL atau nama lagu
@client.tree.command(name="play", description="Play a song from YouTube using URL or song name")
async def play_command(interaction: discord.Interaction, search: str):
    global music_queue
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Connect bot to voice channel if not already connected
        if interaction.guild.voice_client is None:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
            else:
                await interaction.followup.send("Kamu harus berada di voice channel dulu!", ephemeral=True)
                return

        # Jika input adalah URL YouTube
        if "youtube.com/watch?v=" in search or "youtu.be/" in search:
            url = search
        else:
            # Pencarian di YouTube
            query_string = urllib.parse.urlencode({'search_query': search})
            html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
            search_results = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())
            url = 'http://www.youtube.com/watch?v=' + search_results[0]

        # Tambahkan lagu ke queue
        music_queue.append(url)

        # Jika bot tidak sedang memutar lagu, mulai memutar lagu dari queue
        if not interaction.guild.voice_client.is_playing():
            await next_song(interaction)  # Mulai memainkan lagu berikutnya dari antrian
        else:
            # Beri tahu pengguna posisi lagu di antrian jika sedang ada lagu yang diputar
            queue_position = len(music_queue)
            await interaction.followup.send(f"Lagu telah ditambahkan ke antrian di posisi ke-{queue_position}.", ephemeral=False)
    except Exception as e:
        await interaction.followup.send(f"Terjadi kesalahan: {e}", ephemeral=True)



# Command untuk toggle autoplay
@client.tree.command(name="autoplay", description="Enable or disable autoplay")
async def autoplay_command(interaction: discord.Interaction):
    global autoplay_enabled
    try:
        autoplay_enabled = not autoplay_enabled
        status = "enabled" if autoplay_enabled else "disabled"
        await interaction.response.send_message(f"Autoplay telah {status}.", ephemeral=False)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# Command untuk stop lagu
@client.tree.command(name="stop", description="Stop the currently playing song")
async def stop_command(interaction: discord.Interaction):
    """
    Command untuk menghentikan lagu yang sedang diputar.
    """
    try:
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Lagu telah dihentikan.", ephemeral=True)
        else:
            await interaction.response.send_message("Tidak ada lagu yang sedang diputar.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Terjadi kesalahan: {e}", ephemeral=True)

# Command to skip the current song and play the next one in queue
@client.tree.command(name="skip", description="Skip the currently playing song")
async def skip_command(interaction: discord.Interaction):
    try:
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()  # Stop current song to trigger `next_song`
            await interaction.response.send_message("Skipped the current song.", ephemeral=True)
        else:
            await interaction.response.send_message("No song is currently playing to skip.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# Command to toggle 24-7 mode
@client.tree.command(name="24-7", description="Keep the bot in the voice channel even when empty")
async def stay_command(interaction: discord.Interaction):
    global stay_in_channel
    try:
        stay_in_channel = not stay_in_channel
        status = "enabled" if stay_in_channel else "disabled"
        await interaction.response.send_message(f"24-7 mode has been {status}.", ephemeral=True)
        
        # Jika 24-7 mode dinonaktifkan dan tidak ada lagu yang diputar, bot akan keluar dari channel
        if not stay_in_channel and not interaction.guild.voice_client.is_playing():
            await leave_voice_channel(interaction.guild)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)


#LEVELING

# Function to calculate level based on chat count
def calculate_level(chat_count):
    level = math.floor(math.log(chat_count, 5))
    return level

# Command to check user level and chat count
@client.tree.command(name="check-level", description="Check your chat level and message count.")
async def check_level(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    # Fetch user data from MongoDB
    user_data = user_collection.find_one({'id_user': user_id})

    if user_data:
        chat_count = user_data['chat_count']
        level = user_data['level']
        await interaction.response.send_message(f"{interaction.user.mention}, you have sent {chat_count} messages and are currently at level {level}.")
    else:
        await interaction.response.send_message(f"{interaction.user.mention}, you have not sent any messages yet.")


# Helper function to check connection stability
@client.event
async def on_voice_state_update(member, before, after):
    voice_client = member.guild.voice_client
    # Disconnect if bot is alone in channel and 24-7 mode is not enabled
    if voice_client and len(voice_client.channel.members) == 1 and not stay_in_channel:
        await asyncio.sleep(60)  # Wait for a minute to see if anyone joins
        if len(voice_client.channel.members) == 1:
            await voice_client.disconnect()


#API
@client.tree.command(name="post", description="Create a new item in the API")
async def post_command(interaction: discord.Interaction, name: str, description: str):
    # Siapkan data untuk dikirim ke API
    data = {
        "name": name,
        "description": description
    }

    # Menambahkan header Content-Type: application/json
    headers = {
        "Content-Type": "application/json"
    }

    # Kirim permintaan POST ke API
    try:
        response = requests.post(API_URL_POST, json=data, headers=headers)
        response_data = response.json()

        # Cek jika request berhasil
        if response.status_code == 200:
            await interaction.response.send_message(
                f"Item created successfully!\n**Name:** {response_data['name']}\n**Description:** {response_data['description']}"
            )
        else:
            # Tampilkan error dari response API
            await interaction.response.send_message(
                f"Failed to create item. Error: {response_data.get('error', 'Unknown error')}"
            )
    except requests.exceptions.RequestException as e:
        # Tampilkan pesan error jika request gagal
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# Command untuk GET (Retrieve all items)
@client.tree.command(name="get", description="Retrieve all items from the API")
async def get_command(interaction: discord.Interaction):
    try:
        response = requests.get(API_URL_POST)
        items = response.json()
        if response.status_code == 200:
            item_list = "\n".join([f"ID: {item['id']} | Name: {item['name']} | Description: {item['description']}" for item in items])
            await interaction.response.send_message(f"**Items in Database:**\n{item_list}")
        else:
            await interaction.response.send_message("Failed to retrieve items.")
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# Command untuk UPDATE (Update item by ID)
@client.tree.command(name="update", description="Update an existing item in the API")
async def update_command(interaction: discord.Interaction, id: int, name: str, description: str):
    data = {
        "name": name,
        "description": description
    }
    headers = {"Content-Type": "application/json"}
    try:
        # Menggunakan URL dengan ID untuk update
        response = requests.put(f"{API_URL_UPDATE}/{id}", json=data, headers=headers)
        response_data = response.json()
        if response.status_code == 200:
            await interaction.response.send_message(
                f"Item updated successfully!\n**ID:** {response_data['id']}\n**Name:** {response_data['name']}\n**Description:** {response_data['description']}"
            )
        else:
            await interaction.response.send_message(
                f"Failed to update item. Error: {response_data.get('error', 'Unknown error')}"
            )
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")

# Command untuk DELETE (Delete item by ID)
@client.tree.command(name="delete", description="Delete an item from the API by ID")
async def delete_command(interaction: discord.Interaction, id: int):
    headers = {"Content-Type": "application/json"}
    try:
        # Menggunakan URL dengan ID untuk delete
        response = requests.delete(f"{API_URL_DELETE}/{id}", headers=headers)
        if response.status_code == 200:
            await interaction.response.send_message(f"Item with ID {id} deleted successfully.")
        else:
            response_data = response.json()
            await interaction.response.send_message(
                f"Failed to delete item. Error: {response_data.get('error', 'Unknown error')}"
            )
    except requests.exceptions.RequestException as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}")


# MAIN

@client.event
async def on_ready():
    print(f'{client.user} is now jamming')
    await client.tree.sync()
    
    # Mengatur aktivitas
    activity = discord.Activity(type=discord.ActivityType.playing, name="/help", url="https://dcsnekgim.netlify.app")
    await client.change_presence(activity=activity)
    print("Status bot telah diperbarui!")

@client.command()
async def set_activity(ctx, *, activity_name: str):
    activity = discord.Activity(type=discord.ActivityType.playing, name=activity_name, url="https://dcsnekgim.netlify.app")
    await client.change_presence(activity=activity)
    await ctx.send(f"Status bot diubah menjadi: {activity_name}")

def main() -> None:
    # client.add_cog(MusicCog(client))
    client.run(TOKEN)

if __name__ == '__main__':
    main()
