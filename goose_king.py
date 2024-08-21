# PRAISE THE GOOSE KING
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from config import DISCORD_TOKEN
from scheduler_api import load_events, scheduler, stop_scheduler
from event_queue import enqueue_event
import logging
import dateparser
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents = intents)

EST = ZoneInfo('America/New_York')
UTC = ZoneInfo('UTC')

@bot.event
async def on_ready():
    try:
        logger.info(f'Logged in as {bot.user}')
        load_events() 
        scheduler.start()  

    except Exception as e:
        logger.error(f"Failed during Goose King startup: {e}")
        await bot.close()

@bot.slash_command(name='schedule', description="Schedule an event with a date and time")
async def schedule_event(interaction: Interaction,
 date_time: str = SlashOption(description="Date/Time in 'YYYY-MM-DD HH:MM' format (EST), 24 Hour System"),
 event_name: str = SlashOption(description="Name of the Event")):
    try:
        event_datetime = parse_datetime(date_time)
        if event_datetime is None:
            await interaction.response.send_message("Could not understand the date and time. Please try again.")
            return

        event_dt_display = event_datetime.replace(tzinfo=EST)
        # Storage in UTC, collection and display in EST/EDT
        event_datetime = event_dt_display.astimezone(UTC) 
        
        enqueue_event(bot, event_name, event_datetime, interaction.channel_id)
        await interaction.response.send_message(f"Event '{event_name}' scheduled for {event_dt_display.strftime('%Y-%m-%d %H:%M')} hours")

    except Exception as e:
        logger.error(f"Failed to schedule event '{event_name}': {e}")
        await interaction.response.send_message(f"Failed to schedule event '{event_name}': {e}")

def parse_datetime(date_time_str):
    # Parse the date and time with dateparser, should already be in EST
    dt = dateparser.parse(date_time_str, settings={'RETURN_AS_TIMEZONE_AWARE': False, 'PREFER_DATES_FROM': 'future'})
    
    if dt is None:
        return None
    
    return dt.replace(second = 0, microsecond = 0)

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Command error: {error}")
    await ctx.send(f"An error occurred: {error}")

@bot.event
async def on_disconnect():
    stop_scheduler()
    logger.info("Bot disconnected.")

@bot.event
async def on_shutdown():
    stop_scheduler()
    logger.info("Bot is shutting down.")

try:
    bot.run(DISCORD_TOKEN)

except Exception as e:
    logger.error(f"Failed to run the bot: {e}")
