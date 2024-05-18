from typing import Final
import os
from dotenv import load_dotenv
import discord
from discord import Intents, Client, Message, Embed, VoiceChannel, Guild, Member, File
from discord.ext import commands
from discord import FFmpegPCMAudio
import random
from easy_pil import Editor, load_image_async, Font
from responses import get_response


import asyncio
import yt_dlp
#pip install --user yt-dlp
import urllib.parse, urllib.request, re

# Memuat token dari file .env
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Pengaturan bot
intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)


#YT Stuff
queues = {}
voice_clients = {}
youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

# ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"',
    'executable': 'C:\FFmpeg\bin'  # Specify the full path to the FFmpeg executable
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
    audio_source = FFmpegPCMAudio('mantap.mp3')
    voice_client.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
    await interaction.response.send_message("Now playing music!")

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


# class MusicCog(commands.Cog, name="Music"):
#     def __init__(self, bot):
#         self.bot = bot

#     async def play_next(self, ctx):
#         if queues[ctx.guild.id] != []:
#             link = queues[ctx.guild.id].pop(0)
#             await self.play(ctx, link=link)
    
#     @commands.tree.command(name="play", description="Play a song from YouTube")
#     async def play(self, ctx, *, link):
#         try:
#             voice_client = ctx.guild.voice_client
#             if not voice_client:
#                 voice_channel = ctx.author.voice.channel
#                 voice_client = await voice_channel.connect()
#                 voice_clients[voice_client.guild.id] = voice_client

#             if not voice_client.is_playing():
#                 if youtube_base_url not in link:
#                     query_string = urllib.parse.urlencode({
#                         'search_query': link
#                     })

#                     content = urllib.request.urlopen(
#                         youtube_results_url + query_string
#                     )

#                     search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

#                     link = youtube_watch_url + search_results[0]

#                 loop = asyncio.get_event_loop()
#                 data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

#                 song = data['url']
#                 player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

#                 voice_client.play(player, after=lambda e: asyncio.ensure_future(self.play_next(ctx)))
#         except Exception as e:
#             print(e)

#     @commands.tree.command(name="clear_queue", description="Clear the music queue")
#     async def clear_queue(self, ctx):
#         if ctx.guild.id in queues:
#             queues[ctx.guild.id].clear()
#             await ctx.send("Queue cleared!")
#         else:
#             await ctx.send("There is no queue to clear")

#     @commands.tree.command(name="pause", description="Pause the currently playing song")
#     async def pause(self, ctx):
#         try:
#             voice_client = ctx.guild.voice_client
#             if voice_client and voice_client.is_playing():
#                 voice_client.pause()
#         except Exception as e:
#             print(e)

#     @commands.tree.command(name="resume", description="Resume the paused song")
#     async def resume(self, ctx):
#         try:
#             voice_client = ctx.guild.voice_client
#             if voice_client and voice_client.is_paused():
#                 voice_client.resume()
#         except Exception as e:
#             print(e)

#     @commands.tree.command(name="stop", description="Stop playing and disconnect from the voice channel")
#     async def stop(self, ctx):
#         try:
#             voice_client = ctx.guild.voice_client
#             if voice_client:
#                 voice_client.stop()
#                 await voice_client.disconnect()
#                 del voice_clients[ctx.guild.id]
#         except Exception as e:
#             print(e)

#     @commands.tree.command(name="queue", description="Add a song to the music queue")
#     async def queue(self, ctx, *, url):
#         if ctx.guild.id not in queues:
#             queues[ctx.guild.id] = []
#         queues[ctx.guild.id].append(url)
#         await ctx.send("Added to queue!")

def main() -> None:
    # client.add_cog(MusicCog(client))
    client.run(TOKEN)

if __name__ == '__main__':
    main()
