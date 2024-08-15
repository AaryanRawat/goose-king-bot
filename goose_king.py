# PRAISE THE GOOSE KING

import nextcord
from nextcord.ext import commands
from config import DISCORD_TOKEN
from api import load_events, scheduler, stop_scheduler
from event_queue import enqueue_event
import logging
import dateparser
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents = intents)

@bot.event
async def on_ready():
    try:
        logger.info(f'Logged in as {bot.user}')
        load_events() 
        scheduler.start()  

    except Exception as e:
        logger.error(f"Failed during Goose King startup: {e}")
        await bot.close()

@bot.event
async def on_disconnect():
    try:
        stop_scheduler()
        logger.info("Bot disconnected and scheduler stopped.")
        
    except Exception as e:
        logger.error(f"Error during Goose King disconnection: {e}")

@bot.command(name='schedule')
async def schedule_event(ctx, date_time: str, *, event_name: str):
    try:
        event_datetime = dateparser.parse(date_time, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': True})
        if event_datetime is None:
            await ctx.send("Could not understand the date and time. Please try again.")
            return
        
        enqueue_event(event_name, event_datetime, ctx.channel.id)
        await ctx.send(f"Event '{event_name}' scheduled for {event_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    except Exception as e:
        logger.error(f"Failed to schedule event '{event_name}': {e}")
        await ctx.send(f"Failed to schedule event '{event_name}': {e}")

@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Command error: {error}")
    await ctx.send(f"An error occurred: {error}")

try:
    bot.run(DISCORD_TOKEN)
    
except Exception as e:
    logger.error(f"Failed to run the bot: {e}")
