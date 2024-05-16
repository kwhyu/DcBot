from typing import Final
import os
from dotenv import load_dotenv
import asyncio
import discord
from discord import Intents, Client, Message, Embed, VoiceChannel, Guild, Member
# from discord_slash import SlashCommand, SlashContext
# from discord_slash.utils.manage_commands import create_choice, create_option
from responses import get_response

from discord.ext import commands
from discord import FFmpegPCMAudio
import random




# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True
# client: Client = Client(intents=intents)
client = commands.Bot(command_prefix='/', intents=intents)

@client.tree.command(name="kwhy",description="Kwhy is gud")
async def kwhy_command(interaction:discord.Interaction):
    await interaction.response.send_message("Hello Minna sama")

#pip install pynacl

@client.tree.command(name="play-music", description="Play music in the voice channel")
async def play_music_command(ctx: commands.Context):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        return await ctx.send("I'm not connected to a voice channel. Use /join-voice to invite me.")
    if voice_client.is_playing():
        return await ctx.send("I'm already playing music.")
    audio_source = FFmpegPCMAudio('mantap.mp3')
    voice_client.play(audio_source, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send("Now playing music!")

@client.tree.command(name="leave-voice", description="Leave the voice channel")
async def leave_voice_command(ctx: commands.Context):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Bot has left the voice channel.")
    else:
        await ctx.send("Bot is not connected to a voice channel.")

@client.tree.command(name="join-voice", description="Invite Kwhy to Voice Channel")
async def join_voice_command(interaction: discord.Interaction):
    member = interaction.user
    if isinstance(member, discord.Member) and member.guild:
        if member.voice and member.voice.channel:
            voice_channel = member.voice.channel
            await voice_channel.connect()
            try:
                await interaction.response.send_message("Bot has been invited to the voice channel.")
            except discord.errors.NotFound:
                print("Interaction not found.")
            return
    await interaction.response.send_message("You must be connected to a voice channel to invite the bot.")

@client.tree.command(name="marketplace", description="Access the marketplace")
async def marketplace_command(interaction: discord.Interaction):
    items = [
        {'name': 'Item 1', 'price': 10, 'emoji': '⚔️'},
        {'name': 'Item 2', 'price': 20, 'emoji': '🛡️'},
        {'name': 'Item 3', 'price': 30, 'emoji': '🔮'}
    ]

    if interaction.message:
        embed = Embed(title='Marketplace', description='Welcome to the marketplace!')
        for item in items:
            embed.add_field(name=f"{item['emoji']} {item['name']}", value=f"Price: ${item['price']}", inline=False)

        await interaction.response.send_message(embed=embed)

        for item in items:
            await interaction.message.add_reaction(item['emoji'])

        await interaction.followup.send("React to the item you want to buy.")
    else:
        print("Message for interaction not found.")

# Fungsi untuk roll dice
def roll_dice(num_dice: int, num_faces: int) -> str:
    if num_dice != 1 or num_faces != 6:
        return "Invalid dice configuration. Please roll one 6-faced die."
    roll_result = random.randint(1, 6)
    return f"The result of rolling a 6-sided die: {roll_result}"

@client.tree.command(name="roll-dice", description="Roll a six-sided die")
async def roll_dice_command(interaction: discord.Interaction, num_dice: int = 1, num_faces: int = 6):
    result = roll_dice(num_dice, num_faces)
    await interaction.response.send_message(result)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')
    await client.tree.sync()

# @client.event
# async def on_ready():
#     await client.tree.sync()


# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    await send_message(message, user_message)

# STEP 6: MAIN ENTRY POINT
def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()
