from datetime import time, datetime, timedelta
from typing import List


#  Model everything as a list of shifts that can be on or off.


class Shift:

    def __init__(self, start_time: time = None, end_time: time = None, label: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.label = label

    def __repr__(self):
        return f"Start: {self.start_time}, End: {self.end_time}, Label: {self.label}"


class Schedule:

    #  def __init__(self):
    #        self.placeholder = " "

    def __repr__(self):
        representation = ""
        for shift in self.shifts:
            representation += str(shift) + "\n"
        return representation

    @classmethod
    def create_template_from_sample(cls, week: List[List[Shift]], start: datetime, end: datetime):
        """
        @Todo Finish this function implementation
        Creates a blank schedule from a list that is Seven elements long to represent a week. Also a start and end
        datetime
        :param week: A week starting on Monday, if a shift starts on the previous day then don't redefine it
        for the next day. Also have each day sorted from 0000-2400.
        :param start: A datetime to start the scheduling
        :param end: A datetime to end the scheduling
        :return: an empty schedule to be filled with shifts to be scheduled
        """

        template = cls()
        template.shifts = []
        template.week = week
        template.start = start
        template.end = end

        #  current_date_time = start

        #  determine the start of the week that corresponds to the start
        #  day_of_week_index = current_date_time.weekday()
        return template

    @classmethod
    def create_template_from_shift_length(cls, shift_length: timedelta, start: datetime, end: datetime):
        """
        Creates a blank calendar that can be scheduled into.
        :param shift_length: The number of hours that a shift should be
        :param start: The datetime to start
        :param end: The datetime to stop
        :return: a template that is ready to be filled
        """
        template = cls()

        template.shift_length = shift_length
        template.start = start
        template.end = end
        template.shifts = []

        current_datetime = start

        while current_datetime <= end:
            end_shift = current_datetime + shift_length

            template.shifts.append(Shift(start_time=current_datetime.time(), end_time=end_shift.time(), label="Test"))
            current_datetime = end_shift

        return template


if __name__ == '__main__':
    test = Schedule.create_template_from_shift_length(shift_length=timedelta(hours=8), start=datetime(year=2019, month=1, day=1), end=datetime(year=2019, month=2, day=1))
    print(test)
