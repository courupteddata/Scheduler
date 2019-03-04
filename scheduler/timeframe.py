import datetime


class TimeFrame:
    def __init__(self, begin: datetime.datetime = None, end: datetime.datetime = None, inclusive: bool = True):
        """
        Create a time frame that can be checked against. Setting to None means always.
        :param begin: A start date time, or None for always
        :param end: A end date time, will be ignored if begin is None
        :param inclusive: Whether the begin and end are inclusive
        """

        self.begin = begin
        self.end = end
        self.inclusive = inclusive

    def __contains__(self, item) -> bool:
        if self.begin is None:  # First check to see if it is an always time frame
            return True
        if item is None:  # Ignore None values items
            return False
        if isinstance(item, datetime.datetime):  # Now to check to see if the item will be contained in the specified
            # date range
            if self.inclusive:
                return self.begin <= item <= self.end
            else:
                return self.begin < item < self.end
        return False
