import datetime
import random
import unittest
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from fastapi import status
from fastapi.encoders import jsonable_encoder
from main import app, event_db
from models import EventCreate, Event


class TestCreate(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        n = 5
        self.events = [
            EventCreate(
                deadline=datetime.datetime.now(),
                coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2))
            )
            for _ in range(n)
        ]

    def test_create_event(self):
        event = jsonable_encoder(self.events[0])
        response = self.client.post(
            '/events',
            json=event
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        event_response = response.json()
        self.assertIn('uid', event_response)
        uid = event_response.pop('uid')
        self.assertEqual(event_response, event)
        try:
            UUID(uid, version=4)
        except ValueError:
            self.assertTrue(False, 'uuid not valid')


class TestGetUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        n = 10
        events = [
            EventCreate(
                deadline=datetime.datetime.now() + datetime.timedelta(seconds=random.randint(-10, 10)),
                coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2))
            )
            for _ in range(n)
        ]
        self.events = []
        for event in events:
            response = self.client.post(
                '/events',
                json=jsonable_encoder(event)
            )
            self.events.append(Event(**response.json()))

    def tearDown(self) -> None:
        event_db.clear()

    def test_get(self):
        event = jsonable_encoder(self.events[0])
        response = self.client.get(f"/events/{event['uid']}")
        self.assertEqual(event, response.json())
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_not_found(self):
        response = self.client.get(f"/events/{uuid4()}")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual({'detail': 'Event Not Found'}, response.json())

    def test_get_all(self):
        response = self.client.get('/events')
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), len(self.events))
        for event in response_data:
            self.assertIn(Event(**event), self.events)

    def test_get_current(self):
        now = datetime.datetime.now()
        response = self.client.get('/events?current=true')
        response_data = response.json()
        self.assertIsInstance(response_data, list)
        events = [event for event in self.events if event.deadline > now]
        self.assertEqual(len(response_data), len(events))
        for event in response_data:
            self.assertIn(Event(**event), events)