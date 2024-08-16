from schema import ScheduledEvent, db, close_connection
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

EST = pytz.timezone('America/New_York')

def create_event(event_name: str, event_datetime: datetime, channel_id: int):
    try:
        db.connect(reuse_if_open=True)
        event = ScheduledEvent.create(
            event_name = event_name,
            event_datetime = event_datetime,
            channel_id = channel_id,
            completed = False
        )

        schedule_reminders(event)
        return event
        
    except Exception as e:
        logger.error(f"Failed to create '{event_name}': {e} ")
        return None

    finally:
        if not db.is_closed():
            db.close()

def schedule_reminders(event):
    now_utc = datetime.now(pytz.utc)
    # Convert to EST for display
    event_datetime_est = event.event_datetime.astimezone(EST)

    reminder_intervals = [
        timedelta(weeks=1),
        timedelta(days=1),
        timedelta(hours=1),
        timedelta(minutes=5)
    ]

    for interval in reminder_intervals:
        reminder_time = event.event_datetime - interval

        if reminder_time > now_utc:
            reminder_time_est = reminder_time_utc.astimezone(EST)
            try:
                scheduler.add_job(
                    send_reminder, 
                    trigger = DateTrigger(reminder_time), 
                    args = [event.channel_id, event.event_name, reminder_time_est])
            
            except Exception as e:
                logger.error(f"Failed to schedule reminder for event '{event.event_name}' at {reminder_time_est}: {e}")
    
    try:
        scheduler.add_job(
            complete_event, 
            trigger=DateTrigger(event_datetime_est), 
            args=[event.id])

    except Exception as e:
        logger.error(f"Failed to schedule completion for event '{event.event_name}': {e}")
    
async def send_reminder(channel_id, event_name, event_time):
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Reminder: The event **{event_name}** is coming up at {event_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
        else:
           logger.error(f"Channel ID {channel_id} not found for event '{event_name}'.")

    except Exception as e:
        logger.error(f"Failed to send reminder for event '{event_name}': {e}")

def complete_event(event_id):
    try:
        db.connect(reuse_if_open=True)
        event = ScheduledEvent.get(ScheduledEvent.id == event_id)
        event.completed = True
        event.save()         
        #delete_event(event.id)

    except Exception as e:
        logger.error(f"Failed to complete event with ID {event_id}: {e}")

    finally:
        if not db.is_closed():
            db.close()

def delete_event(event_id):
    try:
        db.connect(reuse_if_open=True)
        event = ScheduledEvent.get(ScheduledEvent.id == event_id)
        event.delete_instance()
        logger.info(f"Event with ID {event_id} deleted successfully.")

    except Exception as e:
        logger.error(f"Failed to delete event with ID {event_id}: {e}")

    finally:
        if not db.is_closed():
            db.close()

def load_events():
    try:
        db.connect(reuse_if_open=True)
        events = ScheduledEvent.select().where(ScheduledEvent.completed == False)
        now_utc = datetime.now(pytz.UTC)  # Get the current time in UTC

        for event in events:
            if event.event_datetime.tzinfo is None:
                event_datetime_aware = pytz.UTC.localize(event.event_datetime)
            else:
                event_datetime_aware = event.event_datetime

            if event_datetime_aware > now_utc:
                schedule_reminders(event)

    except Exception as e:
        logger.error(f"Failed to load events: {e}")

    finally:
        if not db.is_closed():
            db.close()

# Ensures the scheduler stops cleanly
def stop_scheduler():
    try:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped successfully")

    except Exception as e:
        logger.error(f"Failed to stop the scheduler: {e}")

