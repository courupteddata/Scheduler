from datetime import datetime, timedelta
from typing import List
import math
import json
from dateutil import parser
import uuid
import random

#  Model everything as a list of shifts that can be on or off.


class Shift:

    def __init__(self, start: datetime = None, end: datetime = None, label: str = None,
                 filled: str = ""):
        self.start = start
        self.end = end
        self.label = label
        self.filled = filled

    def __lt__(self, other) -> bool:
        return self.start < other.start

    def __repr__(self):
        return f"Start: {self.start}, End: {self.end}, Label: {self.label}, Filled: {self.filled}"

    def to_json(self) -> str:
        return json.dumps({"start": self.start.isoformat(),
                           "end": self.end.isoformat(),
                           "label": self.label,
                           "filled": self.filled})


class Schedule:

    def __init__(self):
        self.shifts: List[Shift] = []
        self.schedule_id = str(uuid.uuid1(random.getrandbits(48) | 0x010000000000))

    def __repr__(self):
        representation = ""
        for shift in self.shifts:
            representation += str(shift) + "\n"
        return representation

    def to_json(self) -> str:
        to_return = "["
        for shift in self.shifts:
            to_return += shift.to_json() + ","
        return to_return[:-1] + "]"

    @classmethod
    def from_json(cls, data: str):
        loaded = json.loads(data)

        created = cls()
        for shift in loaded:
            created.shifts.append(Shift(start=parser.parse(shift["start"]),
                                        end=parser.parse(shift["end"]),
                                        label=shift["label"],
                                        filled=shift["filled"]))
        return created

    @classmethod
    def create_template_from_sample(cls, week: List[List[Shift]], end: datetime):
        """
        @Todo Check this implementation
        Creates a blank schedule from a list that is Seven elements long to represent a week. Also a end datetime.
        The list doesn't have to be seven elements long, it can be longer or shorter if a day isn't important
        :param week: A template that will be replicated till the end datetime is reached. This needs to be sorted
        :param end: A datetime to end the scheduling
        :return: an empty schedule to be filled with shifts to be scheduled
        """

        for day in week:
            day.sort()

        template = cls()
        template.shifts = []
        template.week = week
        template.start = week[0][0].start
        template.end = end

        # Put the template in the shift list
        for day in week:
            for shift in day:
                template.shifts.append(Shift(start=shift.start, end=shift.end, label=shift.label))

        """
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        |M|T|W|T|F|S|S|
        """
        length_of_week_list = len(week) - 1
        length_of_last_item = len(week[length_of_week_list]) - 1
        length = (week[length_of_week_list][length_of_last_item].end - template.start).total_seconds()
        seconds_in_a_week = 604800
        week_offset = length/seconds_in_a_week
        days_offset = math.ceil(week_offset) * 7

        shift_offset_increment = timedelta(days=days_offset)
        shift_offset = shift_offset_increment

        while True:
            for day in week:
                for shift in day:
                    if shift.end+shift_offset > end:
                        return template
                    template.shifts.append(Shift(start=shift.start+shift_offset,
                                                 end=shift.end+shift_offset,
                                                 label=shift.label))
            shift_offset = shift_offset + shift_offset_increment

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

            template.shifts.append(Shift(start=current_datetime, end=end_shift, label="Test"))
            current_datetime = end_shift

        return template


if __name__ == '__main__':
    test = Schedule.create_template_from_shift_length(shift_length=timedelta(hours=8),
                                                      start=datetime(year=2019, month=1, day=1),
                                                      end=datetime(year=2019, month=2, day=1))
    print(test)

    just_tuesday = [
        [
            Shift(start=datetime(year=2019, month=1, day=1),
                  end=datetime(year=2019, month=1, day=1)+timedelta(hours=8),
                  label="Tuesday")
        ]
    ]

    test2 = Schedule.create_template_from_sample(just_tuesday, datetime(year=2019, month=2, day=1))

    print("-"*20)
    print(test2)

    two_tuesday = [[Shift(start=datetime(year=2019, month=1, day=1) + timedelta(hours=8),
                    end=datetime(year=2019, month=1, day=1)+timedelta(hours=16),
                    label="TuesdayFirst-Later in day"), Shift(start=datetime(year=2019, month=1, day=1),
                    end=datetime(year=2019, month=1, day=1)+timedelta(hours=8),
                    label="TuesdayFirst"), ],
                   [Shift(start=datetime(year=2019, month=1, day=8),
                    end=datetime(year=2019, month=1, day=8)+timedelta(hours=9),
                    label="TuesdaySecond-9Hours")]]

    test3 = Schedule.create_template_from_sample(two_tuesday, datetime(year=2019, month=2, day=1))

    print("-"*20)
    print(test3)

    temp = test3.to_json()

    print(temp)

    print(Schedule.from_json(temp))
