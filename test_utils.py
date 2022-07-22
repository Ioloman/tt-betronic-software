import datetime
import random
import unittest
from decimal import Decimal
from uuid import uuid4
from models import Line
from utils import DummyDB


class TestAddDummyDB(unittest.TestCase):
    def test_add(self):
        db = DummyDB()
        uuid = uuid4()
        line = Line(uid=uuid, deadline=datetime.datetime.now(), coefficient=Decimal(1.5))
        db.add(line)
        self.assertEqual(line, db.get_all()[0])


class TestDummyDB(unittest.TestCase):
    def setUp(self) -> None:
        n = 50
        self.lines = {
            str(uid): Line(
                uid=uid,
                deadline=datetime.datetime.now(),
                coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2))
            )
            for uid in [uuid4() for _ in range(n)]
        }
        self.db = DummyDB()
        for line in self.lines.values():
            self.db.add(line)

    def test_get(self):
        for uid, line in self.lines.items():
            self.assertEqual(self.db.get(uid), line)

    def test_get_all(self):
        all_ = self.db.get_all()

        for line in all_:
            if line not in self.lines.values():
                self.assertTrue(False, 'Extra line in db')

        for line in self.lines.values():
            if line not in all_:
                self.assertTrue(False, 'Line was not added')