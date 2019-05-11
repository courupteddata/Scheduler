from unittest import TestCase
from scheduler.timeframe import TimeFrame
import datetime


class TestTimeFrame(TestCase):
    def test___contains__always(self):
        """
        Default time frame is always
        :return:
        """
        timeframe_always = TimeFrame()
        self.assertTrue(None in timeframe_always, "None should always return true if it is always.")
        self.assertTrue(datetime.time() in timeframe_always, "Any arbitrary date should work.")

    def test__contains__window(self):
        """
        Test to make sure that the window functionality works
        :return:
        """
        start_date = datetime.datetime(year=2019, month=1, day=1)
        end_date = datetime.datetime(year=2019, month=2, day=1)

        timeframe_window = TimeFrame(start_date, end_date, True)

        self.assertTrue(start_date in timeframe_window, "Should include edge case for inclusive")
        self.assertTrue(end_date in timeframe_window, "Should include edge case for inclusive")
        self.assertTrue(datetime.datetime(year=2019, month=1, day=22) in timeframe_window, "Should include valid ranges")
        self.assertFalse(None in timeframe_window, "Should not include None")
        self.assertFalse(datetime.datetime(year=2018, month=1, day=22) in timeframe_window, "Ignore invalid ranges")

        timeframe_window = TimeFrame(start_date, end_date, False)
        self.assertFalse(start_date in timeframe_window, "Should not include edge case for not inclusive")
        self.assertFalse(end_date in timeframe_window, "Should not include edge case for not inclusive")
        self.assertTrue(datetime.datetime(year=2019, month=1, day=22) in timeframe_window, "Should include valid ranges")
        self.assertFalse(None in timeframe_window, "Should not include None")
        self.assertFalse(datetime.datetime(year=2018, month=1, day=22) in timeframe_window, "Ignore invalid ranges")