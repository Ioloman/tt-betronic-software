import datetime
import random
import unittest
from decimal import Decimal
from uuid import uuid4
from models import Event
from utils import DummyDB


class TestAddDummyDB(unittest.TestCase):
    def test_add(self):
        db = DummyDB()
        uuid = uuid4()
        event = Event(uid=uuid, deadline=datetime.datetime.now(), coefficient=Decimal(1.5))
        db.add(event)
        self.assertEqual(event, db.get_all()[0])


class TestDummyDB(unittest.TestCase):
    def setUp(self) -> None:
        n = 50
        self.events = {
            str(uid): Event(
                uid=uid,
                deadline=datetime.datetime.now(),
                coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2))
            )
            for uid in [uuid4() for _ in range(n)]
        }
        self.db = DummyDB()
        for event in self.events.values():
            self.db.add(event)

    def test_get(self):
        for uid, event in self.events.items():
            self.assertEqual(self.db.get(uid), event)

    def test_get_all(self):
        all_ = self.db.get_all()

        for event in all_:
            if event not in self.events.values():
                self.assertTrue(False, 'Extra event in db')

        for event in self.events.values():
            if event not in all_:
                self.assertTrue(False, 'Event was not added')

    def test_update(self):
        for uid, event in self.events.items():
            coef = Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2))
            self.db.update(uid, event.copy(update={'coefficient': coef}))
            self.assertEqual(self.db.get(uid).coefficient, coef, 'Update test failed')