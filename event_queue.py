from queue import Queue, Empty
import threading
from scheduler_api import create_event
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

event_queue = Queue()

def process_event_queue():
    while True:
        try:
            event_data = event_queue.get(timeout=1)
            create_event(event_data['event_name'], event_data['event_datetime'], event_data['channel_id'])
            event_queue.task_done()

        except Empty:
            continue

        except Exception as e:
            logger.error(f"Failed to process event queue: {e}")

# Start the queue processing thread
try:
    threading.Thread(target=process_event_queue, daemon=True).start()
    logger.info("Event queue processing started successfully.")

except Exception as e:
    logger.error(f"Failed to start event queue processing: {e}")

def enqueue_event(event_name, event_datetime, channel_id):
    try:
        event_queue.put({
            'event_name': event_name,
            'event_datetime': event_datetime,
            'channel_id': channel_id
        })
        logger.info(f"Event '{event_name}' enqueued successfully.")

    except Exception as e:
        logger.error(f"Failed to enqueue event '{event_name}': {e}")

# Dequeue/deletion taken care of by bot.py
