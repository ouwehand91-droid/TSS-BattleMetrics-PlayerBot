import os
import discord
import asyncio
import aiohttp

from discord.ext import commands, tasks


# ==========================
# CONFIGURATION
# ==========================

BATTLEMETRICS_SERVER_ID = "33517301"

UPDATE_INTERVAL = 300  # seconds (5 minutes)

PLAYER_CHANNEL_ID = int(os.getenv("PLAYER_CHANNEL_ID", "0"))

BOT_TOKEN = os.getenv("DISCORD_TOKEN")


# ==========================
# DISCORD SETUP
# ==========================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================
# BATTLEMETRICS FUNCTION
# ==========================

async def get_server_status():

    url = (
        f"https://api.battlemetrics.com/servers/"
        f"{BATTLEMETRICS_SERVER_ID}"
    )

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            if response.status != 200:
                return None

            data = await response.json()

            server = data["data"]["attributes"]

            players = server.get("players", 0)
            max_players = server.get("maxPlayers", 0)

            status = server.get("status")

            return {
                "players": players,
                "max": max_players,
                "online": status == "online"
            }


# ==========================
# UPDATE CHANNEL
# ==========================

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_player_channel():

    if PLAYER_CHANNEL_ID == 0:
        return

    channel = bot.get_channel(PLAYER_CHANNEL_ID)

    if channel is None:
        return


    server = await get_server_status()


    if server is None or not server["online"]:

        await channel.edit(
            name="🔴 Public Players: Offline"
        )

        return


    await channel.edit(
        name=f"🟢 Public Players: {server['players']}/{server['max']}"
    )


# ==========================
# BOT EVENTS
# ==========================

@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

    if not update_player_channel.is_running():
        update_player_channel.start()


# ==========================
# START
# ==========================

bot.run(BOT_TOKEN)
