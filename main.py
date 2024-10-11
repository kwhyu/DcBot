from typing import Final
import os
from dotenv import load_dotenv
import discord
from discord import Intents, Client, Message, Embed, VoiceChannel, Guild, Member, File, Activity, ActivityType
from discord.ext import commands
from discord import FFmpegPCMAudio
import random
from easy_pil import Editor, load_image_async, Font
from responses import get_response
import openai
import random

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

TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CUSTOM_ACTIVITY_ID = os.getenv('CUSTOM_ACTIVITY_ID')

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
WELCOME_CHANNEL_ID2: Final[int] = 1236526200306929786

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

@client.tree.command(name="help", description="List of available commands and their descriptions")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", description="Here is a list of commands you can use:", color=discord.Color.blue())
    
    embed.add_field(name="/ping", value="Check bot's latency.", inline=False)
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

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="settings", description="Open the bot's settings dashboard")
async def settings_command(interaction: discord.Interaction):
    dashboard_url = "http://your-flask-app-url.com"  # Ganti dengan URL yang sesuai
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

    await send_message(message, user_message)

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
