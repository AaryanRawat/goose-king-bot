from peewee import PostgresqlDatabase, Model, CharField, DateTimeField, BigIntegerField, BooleanField
import os
from dotenv import load_dotenv
import logging

# Logging set up
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Database connection settings
db_name = os.getenv('PG_DB')
db_user = os.getenv('PG_USER')
db_password = os.getenv('PG_PASSWORD')
db_host = os.getenv('PG_HOST')
db_port = os.getenv('PG_PORT')

# DB Connection
try:
    db = PostgresqlDatabase(
        db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    logger.info(f"Connected to the PostgreSQL database: {db_name}")
except Exception as e:
    logger.error(f"Failed to connect to the PostgreSQL database: {e}")
    raise SystemExit(f"Database connection failed: {e}")

class BaseModel(Model):
    class Meta:
        database = db
class ScheduledEvent(BaseModel):
    event_name = CharField()
    event_datetime = DateTimeField()
    channel_id = BigIntegerField()
    completed = BooleanField(default=False)

def create_tables():
    try:
        db.connect(reuse_if_open=True)
        db.create_tables([ScheduledEvent])
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    finally:
        if not db.is_closed():
            db.close()

def close_connection():
    try:
        if not db.is_closed():
            db.close()
            logger.info("Database connection closed successfully.")
    except Exception as e:
        logger.error(f"Failed to close the database connection: {e}")

if __name__ == "__main__":
    create_tables()
