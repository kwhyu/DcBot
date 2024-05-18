from responses import get_response
import os
from typing import Final, List
from dotenv import load_dotenv
import discord
from discord import Intents, Embed, File, Member
from discord.ext import commands
from discord import FFmpegPCMAudio
import random
from easy_pil import Editor, load_image_async, Font
import asyncio

# Load the token from .env file
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot settings
intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)

# FFmpeg options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"',
    'executable': 'C:\FFmpeg\zbin\zffmpeg.exe'
}

# Welcome channel IDs
WELCOME_CHANNEL_ID: Final[int] = 1227942494684057705
WELCOME_CHANNEL_ID2: Final[int] = 1236526200306929786

WELCOME_IMAGE: Final[str] = "pic1.jpg"

# Global variables to manage playlist and looping
playlist: List[str] = []
is_looping: bool = True

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

@client.tree.command(name="kwhy", description="Kwhy is good")
async def kwhy_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hello Minna sama")

async def play_next_song(guild: discord.Guild):
    global playlist, is_looping
    voice_client = guild.voice_client

    if not voice_client or not playlist:
        return

    audio_source = FFmpegPCMAudio(playlist[0], **ffmpeg_options)
    voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(on_song_end(guild), client.loop))

async def on_song_end(guild: discord.Guild):
    global playlist, is_looping
    if not playlist:
        return

    # Remove the first song from the playlist
    playlist.pop(0)

    if is_looping and not playlist:
        # Reset the playlist if looping is enabled and playlist is empty
        playlist.extend(['mantap.mp3', 'mantap2.mp3', 'mantap3.mp3'])  # Replace with your list of songs

    await play_next_song(guild)

@client.tree.command(name="play-music", description="Play music in the voice channel")
async def play_music_command(interaction: discord.Interaction):
    global playlist, is_looping
    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("I'm not connected to a voice channel. Use /join-voice to invite me.")
        return

    # Add songs to the playlist
    new_songs = ['mantap.mp3', 'mantap2.mp3', 'mantap3.mp3']  # Replace with your list of songs
    playlist.extend(new_songs)

    if not voice_client.is_playing():
        await play_next_song(interaction.guild)
        await interaction.response.send_message("Now playing music!")
    else:
        await interaction.response.send_message("Added songs to the playlist.")

@client.tree.command(name="leave-voice", description="Leave the voice channel")
async def leave_voice_command(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.response.send_message("Bot has left the voice channel.")
    else:
        await interaction.response.send_message("Bot is not connected to a voice channel.")

@client.tree.command(name="join-voice", description="Invite the bot to a voice channel")
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

def roll_dice(num_dice: int, num_faces: int) -> str:
    if num_dice != 1 or num_faces != 6:
        return "Invalid dice configuration. Please roll one 6-faced die."
    roll_result = random.randint(1, 6)
    return f"The result of rolling a 6-sided die: {roll_result}"

@client.tree.command(name="roll-dice", description="Roll a six-sided die")
async def roll_dice_command(interaction: discord.Interaction, num_dice: int = 1, num_faces: int = 6):
    result = roll_dice(num_dice, num_faces)
    await interaction.response.send_message(result)

async def send_message(message: discord.Message, user_message: str) -> None:
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

@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    await send_message(message, user_message)

@client.event
async def on_ready():
    print(f'{client.user} sekarang aktif!')
    await client.tree.sync()

def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
