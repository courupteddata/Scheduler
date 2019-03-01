"""
Contains the base requirement for units to compute cost
"""


class Requirement:
    def __init__(self, label, requirement_value=0):
        self.label = label
        self.requirement_value = requirement_value
