# -*- coding: utf-8 -*-

class Employee(object):
    def __init__(self, name):
        self.name = name
        self._max_shifts = {}
        self.max_total_minutes = 0
        self.min_total_minutes = 0
        self.max_consecutive_shifts = 0
        self.min_consecutive_shifts = 0
        self.min_consecutive_days_off = 0
        self.max_weekends = 0
        self.days_off = []
        self._shift_on_requests = []
        self._shift_off_requests = []

    def set_max_shifts(self, shifts):
        self._max_shifts = shifts

    def get_max_shift(self, name):
        return self._max_shifts.get(name, 0)

    def add_shift_on_request(self, req):
        day = req[0]

        if day in self._shift_on_requests:
            self._shift_on_requests[day].append(tuple(req[1:]))
        else:
            self._shift_on_requests = [ tuple(req[:1]) ]

    def add_shift_off_request(self, req):
        day = req[0]

        if day in self._shift_off_requests:
            self._shift_off_requests[day].append(tuple(req[1:]))
        else:
            self._shift_off_requests = [ tuple(req[:1]) ]

    def get_shift_penalty(self, day, shift):
        """
        Gets penalty (if any) for shift that is on and should be off, or vice
        versa.
        """
        if shift: # Possibly penalize shift on when should be off
            if day in self._shift_off_requests:
                for s, w in self._shift_off_requests[day]:
                    if s == shift:
                        return w
        else: # Possibly penalize shift off when should be on
            if day in self._shift_on_requests:
                for s, w in self._shift_on_requests[day]:
                    if s == shift:
                        return w

        return 0 # All good!
