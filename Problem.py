# -*- coding: utf-8 -*-

class Problem(object):
    """
    A simple problem container
    """
    def __init__(self, days, section_covers, employees, shifts):
        self.days = days
        self.section_covers = section_covers
        self.employees = employees
        self.shifts = shifts
