from unittest import TestCase
from scheduler.entitystate import EntityState
from datetime import datetime, timedelta


class TestEntityState(TestCase):
    def test_scheduled(self):
        entity_state = EntityState()
        start = datetime(year=2019, month=4, day=1, hour=12)

        self.assertEqual(entity_state.hours_worked_in(start - timedelta(days=1), start + timedelta(days=1)),
                         0, "No entries")

        entity_state.scheduled(start, 10)

        self.assertEqual(entity_state.hours_worked_in(start - timedelta(days=1), start + timedelta(days=1)),
                         10, "The hours worked should be only from one entry")

        entity_state.scheduled(start + timedelta(days=10), timedelta(hours=5))

        self.assertEqual(entity_state.hours_worked_in(start + timedelta(days=1), start + timedelta(days=11)),
                         5, "The hours worked should be only from one entry")

        self.assertEqual(entity_state.hours_worked_in(start - timedelta(days=1), start + timedelta(days=11)),
                         15, "The time should be from both entries")


class TestEntityStateWorkedEntry(TestCase):

    def test_creation(self):
        a_date = datetime(year=2019, month=4, day=1, hour=12)

        entry = EntityState.WorkedEntry(a_date, 4)
        self.assertEqual(entry.shift_start, a_date, "Date should be the same")
        self.assertEqual(entry.hours_worked, 4, "Hours worked should be the same")

    def test_order(self):
        first_date = datetime(year=2019, month=4, day=1, hour=12)
        second_date = datetime(year=2019, month=4, day=1, hour=14)

        entry_one = EntityState.WorkedEntry(first_date, 3)
        entry_two = EntityState.WorkedEntry(second_date, 1)

        self.assertTrue(entry_one < entry_two, "Entry one should come before entry two")
