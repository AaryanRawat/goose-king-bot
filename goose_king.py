# PRAISE THE GOOSE KING
import nextcord
from nextcord.ext import commands
from config import DISCORD_TOKEN
from scheduler_api import load_events, scheduler, stop_scheduler
from event_queue import enqueue_event
import logging
import dateparser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents = intents)

EST = pytz.timezone('America/New_York')

# Example: Parsing a date and time provided by the user
def parse_datetime(date_time_str):
    # Parse the date and time with dateparser
    dt = dateparser.parse(date_time_str, settings={'RETURN_AS_TIMEZONE_AWARE': True, 'PREFER_DATES_FROM': 'future'})
    
    if dt is None:
        return None
    
    # Convert to EST
    dt_est = parsed_dt.astimezone(EST)
    return dt_est

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
        event_datetime = parse_datetime(date_time)
        if event_datetime is None:
            await ctx.send("Could not understand the date and time. Please try again.")
            return

        # Storage in UTC, collection and display in EST
        event_datetime_utc = event_datetime.astimezone(pytz.UTC) 
        
        enqueue_event(event_name, event_datetime_utc, ctx.channel.id)
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
