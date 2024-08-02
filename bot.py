import os
import nextcord
from nextcord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta, timezone
import pytz
import dateparser
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()



@bot.command(name='schedule')
async def schedule_event(ctx, date_time: str, *, event_name: str):
    # Parse the date and time
    event_datetime = dateparser.parse(date_time, settings={'TIMEZONE': 'EST', 'RETURN_AS_TIMEZONE_AWARE': True})
    
    if event_datetime is None:
        await ctx.send("Could not understand the date and time. Please try again.")
        return
    
    # Calculate the time remaining until the event
    now = datetime.now(pytz.UTC)
    time_until_event = event_datetime - now
    
    if time_until_event.total_seconds() <= 0:
        await ctx.send("The specified time is in the past. Please provide a future date and time.")
        return
    
    # Schedule reminders (every hour, then every minute for the last 5 minutes)
    reminder_times = [
        event_datetime - timedelta(hours=1),
        event_datetime - timedelta(minutes=30),
        event_datetime - timedelta(minutes=15),
        event_datetime - timedelta(minutes=5),
        event_datetime - timedelta(minutes=1)
    ]
    
    for reminder_time in reminder_times:
        if reminder_time > now:
            scheduler.add_job(send_reminder, trigger=DateTrigger(reminder_time), args=[ctx.channel.id, event_name, reminder_time])
    
    # Schedule the final event notification
    scheduler.add_job(send_reminder, trigger=DateTrigger(event_datetime), args=[ctx.channel.id, event_name, event_datetime, True])
    
    await ctx.send(f"Event '{event_name}' scheduled for {event_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")

async def send_reminder(channel_id, event_name, event_time, final=False):
    channel = bot.get_channel(channel_id)
    if final:
        await channel.send(f"⏰ It's time for the event: **{event_name}**!")
    else:
        await channel.send(f"Reminder: The event **{event_name}** is coming up at {event_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()
    
bot.run(TOKEN)
