from unittest import TestCase
from scheduler.entityrequirement import EntityRequirement
from scheduler.entitystate import EntityState
from datetime import datetime


class TestEntityRequirement(TestCase):
    def test_applies(self):
        cost = 10
        label = "always"
        always_requirement = EntityRequirement(label, cost)

        self.assertTrue(always_requirement.applies(EntityState(), datetime.now(), datetime.now()),
                        "The base class should always return true for applies.")

        self.assertEqual(always_requirement.cost, cost, "Cost should be set correctly")

        cost = 20
        always_requirement.cost = cost

        self.assertEqual(always_requirement.cost, cost, "Cost should be updated correctly")

        self.assertEqual(always_requirement.label, label, "Label should be set correctly")
        self.assertFalse(always_requirement.is_relative, "A base requirement should not be relative")
