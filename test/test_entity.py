from unittest import TestCase
from scheduler.entity import Entity
from scheduler.entityrequirement import EntityRequirement
from datetime import datetime, timedelta


class TestEntity(TestCase):
    def test_clear_state_and_schedule(self):
        entity = Entity("name")
        now = datetime.now()
        now_end = datetime.now() + timedelta(hours=8)

        self.assertEqual(entity.name, "name", "Name should equal")
        entity.schedule(now, now_end)

        self.assertEqual(entity.state.hours_worked_in(now, now_end), 8, "Schedule should set hours correctly")

        entity.clear_state()

        self.assertEqual(entity.state.hours_worked_in(now, now_end), 0, "Schedule should clear hours correctly")

    def test_cost_to_schedule_and_add_remove_req(self):
        entity = Entity("OtherName")
        now = datetime.now()
        now_end = datetime.now() + timedelta(hours=8)

        self.assertEqual(entity.name, "OtherName", "Name should equal")

        req = EntityRequirement("label", 17)
        entity.add_requirement(req)

        self.assertEqual(entity.cost_to_schedule(now, now_end), 17, "Cost should be from one always requirement")

        entity.remove_requirement(req)

        self.assertEqual(entity.cost_to_schedule(now, now_end), 0, "Cost should be zero, no requirements")
