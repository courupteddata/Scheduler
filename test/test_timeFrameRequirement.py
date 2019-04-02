from unittest import TestCase
from scheduler.entityrequirement import TimeFrameRequirement
from scheduler.entitystate import EntityState
from datetime import datetime, timedelta, time


class TestTimeFrameRequirement(TestCase):

    def test_default_init(self):
        default_init = TimeFrameRequirement("Should Never Apply", 0)

        self.assertEqual(default_init.cost, 0, "Cost setting should still work")
        self.assertFalse(default_init.applies(EntityState(), datetime.now(), datetime.now()),
                         "Default creation should not apply.")
        self.assertFalse(default_init.is_relative, "Should not be relative")

    def test_create_day_week_requirement(self):
        label = "Day week"
        cost = 10

        monday = datetime(year=2019, month=4, day=1, hour=12)  # This is a monday

        day_week_req = TimeFrameRequirement.create_day_week_requirement(label, monday, cost)

        self.assertFalse(day_week_req.is_relative, "Should not be relative")

        self.assertTrue(day_week_req.applies(EntityState(), monday - timedelta(hours=3), monday + timedelta(hours=3)),
                        "Should apply because the shift is on Monday")
        self.assertEqual(cost, day_week_req.cost, "Cost should be the same")
        self.assertEqual(label, day_week_req.label, "Label should be the same")

        self.assertFalse(day_week_req.applies(EntityState(), monday - timedelta(days=1), monday - timedelta(days=1)),
                         "Should not apply since it is not longer monday")

        self.assertRaises(ValueError, day_week_req.applies, EntityState(), monday + timedelta(hours=3),
                          monday - timedelta(hours=3))  # The end of a shift can not come before the start

    def test_create_date_range_requirement(self):
        label = "Date range"
        cost = 11

        center = datetime(year=2019, month=4, day=1, hour=12)

        date_range_req = TimeFrameRequirement.create_date_range_requirement(label, center - timedelta(days=1),
                                                                            center + timedelta(days=1), cost)

        self.assertTrue(date_range_req.applies(EntityState(), center, center + timedelta(days=1)),
                        "Contains the range, should apply.")

        self.assertFalse(date_range_req.applies(EntityState(), center + timedelta(days=5), center + timedelta(days=6)),
                         "Outside of date range")

        self.assertFalse(date_range_req.is_relative, "A date range requirement should not be relative")
        self.assertEqual(label, date_range_req.label, "Labels should equal")
        self.assertEqual(cost, date_range_req.cost, "Costs should equal")
        self.assertFalse(date_range_req.is_relative, "Should not be relative")

    def test_create_time_range_requirement(self):
        label = "Time range"
        cost = 12

        center = datetime(year=2019, month=4, day=1, hour=12)
        start = center.time()
        end = (center + timedelta(hours=1)).time()

        time_range_req = TimeFrameRequirement.create_time_range_requirement(label, start, end, cost)

        self.assertTrue(
            time_range_req.applies(EntityState(), center - timedelta(hours=5), center + timedelta(minutes=30)),
            "Contains the time range requirement")

        self.assertFalse(
            time_range_req.applies(EntityState(), center + timedelta(hours=5), center + timedelta(hours=6)),
            "Should not contain the time range requirement")

        self.assertEqual(label, time_range_req.label, "Label should be the same")
        self.assertEqual(cost, time_range_req.cost, "Cost should be the same")
        self.assertFalse(time_range_req.is_relative, "Should not be relative")
