from peewee import PostgresqlDatabase, Model, CharField, DateTimeField, BigIntegerField, BooleanField
import os
from dotenv import load_dotenv

load_dotenv()

db = PostgresqlDatabase(
    os.getenv('PG_DB'),
    user = os.getenv('PG_USER'),
    password = os.getenv('PG_PASSWORD'),
    host = os.getenv('PG_HOST'),
    port = os.getenv('PG_PORT')
)

class BaseModel(Model):
    class Meta:
        database = db

class ScheduledEvent(BaseModel):
    event_name = CharField()
    event_datetime = DateTimeField()
    channel_id = BigIntegerField()
    completed = BooleanField(default = False)

def create_tables():
    db.connect()
    db.create_tables([ScheduledEvent])