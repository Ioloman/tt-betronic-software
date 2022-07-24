import asyncio
import datetime
import os
import urllib.parse

import httpx
from aio_pika.connection import make_url
from aioredis import Redis
from fastapi import FastAPI, Depends, BackgroundTasks, status, HTTPException
from sqlalchemy.sql import Select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from connections.database import init_db
from connections.services import RedisHandler, RabbitHandler
from models import Bet, BetCreate, Event
from connections.database import get_session
from helpers import get_events_cached, update_bet

app = FastAPI(
    title='Bet Maker'
)


@app.on_event('startup')
async def startup():
    await init_db()
    RedisHandler().connect(os.getenv('REDIS_URL'))
    rabbit = RabbitHandler()
    await rabbit.connect(make_url(
        host=os.getenv('RABBIT_HOST'),
        port=int(os.getenv('RABBIT_PORT')),
        login=os.getenv('RABBIT_USER'),
        password=os.getenv('RABBIT_PASS'),
        timeout=int(os.getenv('RABBIT_TIMEOUT'))
    ))

    channel = await rabbit.get_conn()
    queue = await channel.declare_queue(os.getenv('RABBIT_QUEUE'), durable=True)
    await queue.consume(update_bet)


@app.on_event('shutdown')
async def shutdown():
    await RedisHandler().disconnect()
    await RabbitHandler().disconnect()


@app.get('/bets', response_model=list[Bet])
async def get_bets(session: AsyncSession = Depends(get_session)):
    expr: Select = select(Bet)
    result = (await session.exec(expr)).all()
    return result


@app.post('/bets', response_model=Bet)
async def create_bet(bet: BetCreate, session: AsyncSession = Depends(get_session)):
    async with httpx.AsyncClient() as client:  # type: httpx.AsyncClient
        response = await client.get(urllib.parse.urljoin(os.getenv('EVENTS_API_URL'), f'/events/{bet.event_uid}'))
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='event not found')
    event = Event(**response.json())
    if event.deadline < datetime.datetime.now():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='event deadline passed')

    bet_created = Bet(**bet.dict(), coefficient=event.coefficient, status=event.status)
    session.add(bet_created)
    await session.commit()
    await session.refresh(bet_created)
    return bet_created


@app.get('/events', response_model=list[Event])
async def get_events(*, redis: Redis = Depends(RedisHandler().get_conn), tasks: BackgroundTasks):
    return await get_events_cached(redis, tasks)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8001)