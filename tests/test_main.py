import datetime
import os
import unittest
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv


load_dotenv('../.env')

from connections.services import RedisHandler
from main import app
from connections.database import get_session, engine


async def override_get_session() -> AsyncSession:
    """
    Dependency for injection into handlers that provides SQLAlchemy session
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession,
        autocommit=False, autoflush=False
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session


class TestSimpleEndpoints(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    async def asyncSetUp(self) -> None:
        RedisHandler().connect(os.getenv('REDIS_URL'))

    async def asyncTearDown(self) -> None:
        await RedisHandler().disconnect()

    def test_get_events(self):
        now = datetime.datetime.now().isoformat()
        response = self.client.get('/events')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        data = response.json()
        self.assertIsInstance(data, list)
        for event in data:
            self.assertGreater(event['deadline'], now)

    def test_create_bet_wrong_event(self):
        response = self.client.post('/bets', json={'amount': 15, 'event_uid': str(uuid4())})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_bet(self):
        response = self.client.get('/events')
        data = response.json()
        if len(data) == 0:
            self.assertTrue(False, 'Populate test environment with events')

        event = data[0]
        response = self.client.post('/bets', json={'amount': 15, 'event_uid': event['uid']})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        bet = response.json()
        self.assertIsInstance(bet, dict)
        self.assertEqual(event['uid'], bet['event_uid'])
        self.assertEqual(15, bet['amount'])

    def test_create_bet_bad_amount(self):
        response = self.client.get('/events')
        data = response.json()
        if len(data) == 0:
            self.assertTrue(False, 'Populate test environment with events')

        event = data[0]
        response = self.client.post('/bets', json={'amount': 0, 'event_uid': event['uid']})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)