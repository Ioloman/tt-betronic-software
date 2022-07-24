import logging
import os
import datetime
import random
from decimal import Decimal
from uuid import UUID

from aio_pika.abc import AbstractRobustConnection, DeliveryMode

from init import init
from fastapi import FastAPI, status, HTTPException, Query, BackgroundTasks

from models import Event, EventPut, EventCreate, EventStatus, EventStatusUpdate
from utils import DummyDB
import aio_pika


LOGGER_NAME = init(__file__)
logger = logging.getLogger(LOGGER_NAME)

app = FastAPI(
    title='Line Provider'
)

event_db = DummyDB()
if os.getenv('APP_ENV') == 'prod':
    for _ in range(10):
        event_db.add(Event(
            coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2)),
            deadline=datetime.datetime.now() + datetime.timedelta(minutes=random.randint(5, 30))
        ))


mq_connection = aio_pika.connect_robust(
    host=os.getenv('RABBIT_HOST'),
    port=int(os.getenv('RABBIT_PORT')),
    login=os.getenv('RABBIT_USER'),
    password=os.getenv('RABBIT_PASS'),
    timeout=int(os.getenv('RABBIT_TIMEOUT'))
)


@app.on_event('startup')
async def startup():
    global mq_connection
    mq_connection = await mq_connection


@app.on_event('shutdown')
async def shutdown():
    await mq_connection.close()


@app.get('/events', response_model=list[Event])
async def get_events(current: bool = Query(None)):
    """
    Get list of all events
    """
    logger.info(f'request to get events current_mode={current}')
    events = event_db.get_all()
    if current:
        now = datetime.datetime.now()
        return [event for event in events if event.deadline < now]
    else:
        return events


@app.post('/events', response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    event_created = Event(**event.dict())
    event_db.add(event_created)
    logger.info(f'added event={event_created}')
    return event_created


@app.get('/events/{uid}', response_model=Event)
async def get_event(uid: UUID):
    """
    Get event by uuid
    """
    event = event_db.get(str(uid))
    logger.info(f'got {event=} from {uid=}')
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event Not Found')
    return event


@app.put('/events/{uid}', response_model=Event)
async def update_event(uid: UUID, event: EventPut, tasks: BackgroundTasks):
    """
    Update event
    """
    # get event from db
    event_stored = event_db.get(str(uid))
    logger.info(f'got {event_stored=} from {uid=}, update {event}')
    if event_stored is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event Not Found')

    # update it
    event_updated = event_stored.copy(update=event.dict())
    result = event_db.update(str(uid), event_updated)

    # return result and update bet
    if result:
        logger.info('updated')
        # create notification task about status update
        if event_stored.get_status() != event_updated.get_status():
            logger.info('create task to notify status update')
            tasks.add_task(notify_status_update, mq_connection, uid, event_updated.get_status())

        return event_updated
    else:
        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE, detail='Update failed')


async def notify_status_update(connection: AbstractRobustConnection, uid: UUID, status: EventStatus):
    channel = await connection.channel()
    queue = await channel.declare_queue(os.getenv('RABBIT_QUEUE'), durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=EventStatusUpdate(uid=uid, status=status).json().encode(),
            delivery_mode=DeliveryMode.PERSISTENT
        ),
        queue.name
    )
