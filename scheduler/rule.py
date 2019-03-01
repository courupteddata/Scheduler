class Rule:
    """
    In a time frame this action, yes or no
    """

    def __init__(self, time_frame, action, yes_or_no):
        """
        Creates a rule
        :param time_frame: A time frame
        :param action: an action that can be done
        :param yes_or_no: whether the action is allowed to be done
        """
        self.time_frame = time_frame
        self.action = action
        self.yes_or_no = yes_or_no
