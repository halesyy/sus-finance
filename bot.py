
import discord
import os
from lib.timer import interval

token = os.getenv("SUS_D_KEY", False)

if token == False:
    print("Client token could not be extracted from SUS_D_KEY...")
    input("Idle... needs fix")
    exit()

client = discord.Client()

def check_latest():
    print("hi...")

# interval(check_latest, 5)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    print("Starting: scrape checker")
    channel = await client.fetch_channel("864717912291672095")
    response = await channel.send("hi?")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hi!")

client.run(token)
