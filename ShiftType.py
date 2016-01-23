# -*- coding: utf-8 -*-

class ShiftType(object):
    def __init__(self, name, time, not_followed_by):
        self.name = name
        self.time = time
        self.not_followed_by = not_followed_by
        self.cover_requirements = []

    def can_follow(self, shift):
        return self.name not in shift.not_followed_by

    def can_be_followed_by(self, shift):
        return shift.name not in self.not_followed_by
