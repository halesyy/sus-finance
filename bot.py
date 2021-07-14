
import discord
from discord.ext.tasks import loop
import os
import json
from datetime import date

# shorthands, work well for quickly writing new func
today = lambda: date.today().strftime("%d/%m/%Y")
get_data = lambda: json.loads(open("data.json", "r").read())
save_data = lambda d: open("data.json", "w").write(json.dumps(d, indent=4))
get_days = lambda: get_data()["days_checked"]
has_worked_today = lambda: today() in get_days()

token = open("token", "r").read().strip()

if len(token) < 10:
    print("Client token could not be extracted from SUS_D_KEY...")
    input("Idle... needs fix")
    exit()

def latest_data(): # simple getter function for latest data
    data = get_data()
    return (data["latest_date"], data["latest_score"])

def set_latest_date(latest_date, latest_score): # simple setter function for latest data
    data = get_data()
    data["latest_date"] = latest_date
    data["latest_score"] = latest_score
    save_data(data)

def save_date_score(date, score):
    data = get_data()
    data["days_data"][date] = score
    save_data(data)

def finished_work_today():
    data = get_data()
    days = data["days_checked"]
    if today() not in days:
        days.append(today())
        open("data.json", "w").write(json.dumps(data, indent=4))

client = discord.Client()

@loop(seconds=3600)
async def check_latest():
    if has_worked_today():
        print("> still waiting...")
    else:
        print("> starting work...")
        from scraper import work
        # current (scrape) vs old (cache)
        latest_date, latest_score, dates= work()
        old_date, old_score = latest_data()
        # await message_channel("864753953182842880", f"<@135605387373051905> error: {message}")
        if latest_date != old_date:
            latest_score_pn = f"+{latest_score}" if latest_score >= 0 else f"-{latest_score}"
            channel = await client.fetch_channel("864717912291672095")
            response = await channel.send(f"(new) <@135605387373051905> the score for **{latest_date}** is **{latest_score_pn}** (bullish - bearish)")
            set_latest_date(latest_date, latest_score)
        else:
            print("> nothing new in daily work, ignoring")
        finished_work_today()

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    print("Starting: scrape checker")
    check_latest.start() # initialize

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$latest"):
        latest_date, latest_score = latest_data()
        await message.channel.send(f"The latest score for **{latest_date}** is **{latest_score}**")

client.run(token)
