from typing import Final
import os
from dotenv import load_dotenv
import asyncio
from discord import Intents, Client, Message, Embed
from responses import get_response

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)


# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        # Check if the message is a buy command
        if user_message.startswith('!buy'):
            await handle_marketplace_command(message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


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


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)

async def handle_marketplace_command(message: Message) -> None:
    # Daftar barang yang tersedia beserta emoji yang sesuai
    items = [
        {'name': 'Item 1', 'price': 10, 'emoji': '⚔️'},  # Emoji untuk Item 1
        {'name': 'Item 2', 'price': 20, 'emoji': '🛡️'},  # Emoji untuk Item 2
        {'name': 'Item 3', 'price': 30, 'emoji': '🔮'}   # Emoji untuk Item 3
    ]

    # Membuat pesan embed untuk menu barang
    embed = Embed(title='Marketplace', description='Welcome to the marketplace!')
    for item in items:
        embed.add_field(name=f"{item['emoji']} {item['name']}", value=f"Price: ${item['price']}", inline=False)

    # Mengirim pesan embed ke saluran pesan pengguna
    sent_message = await message.channel.send(embed=embed)

    # Menambahkan reaksi ke setiap item di menu
    for item in items:
        await sent_message.add_reaction(item['emoji'])

    # Pesan penjelasan untuk pengguna
    await message.channel.send("React to the item you want to buy.")

    # Menunggu tanggapan dari pengguna dalam bentuk reaksi
    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in [item['emoji'] for item in items]

    try:
        reaction, _ = await client.wait_for('reaction_add', timeout=60.0, check=check)
        selected_item = next((item for item in items if item['emoji'] == str(reaction.emoji)), None)
        if selected_item:
            response = f"You've selected {selected_item['name']} for ${selected_item['price']}."
            await message.channel.send(response)
        else:
            await message.channel.send("Invalid selection.")
    except asyncio.TimeoutError:
        await message.channel.send("You didn't select any item within the time limit.")

if __name__ == '__main__':
    main()

