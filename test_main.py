import datetime
import random
import unittest
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from fastapi import status
from fastapi.encoders import jsonable_encoder
from main import app
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
        n = 3
        events = [
            EventCreate(
                deadline=datetime.datetime.now(),
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

    def test_update(self):
        event: dict = jsonable_encoder(self.events[0])
        event_update = event.copy()
        event_update.pop('uid')
        event_update.pop('deadline')
        event_update['status'] = 2
        event_update['coefficient'] = 1.5

        response = self.client.put(
            f"/events/{event['uid']}",
            json=event_update
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.json(), event | event_update)

        response_get = self.client.get(f"/events/{event['uid']}")
        self.assertEqual(status.HTTP_200_OK, response_get.status_code)
        self.assertEqual(response_get.json(), event | event_update)