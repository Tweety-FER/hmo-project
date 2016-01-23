# -*- coding: utf-8 -*-

import re
from Employee import Employee
from ShiftType import ShiftType
from Problem import Problem

def intify(x):
    if isinstance(x, list):
        return [intify(a) for a in x]

    return int(x)

def day_count_parser(text):
    return int(text)

def shifts_parser(text):
    parts = text.split(',')
    return ShiftType(parts[0], int(parts[1]), parts[2].split('|'))

def staff_parser(text):
    parts = text.split(',')
    employee = Employee(parts[0])

    shift_max_pairs = map(lambda x: x.split('='), parts[1].split('|'))
    shifts_max = {}

    for shift, limit in shift_max_pairs:
        shifts_max[shift] = int(limit)

    employee.set_max_shifts(shifts_max)
    employee.max_total_minutes = int(parts[2])
    employee.min_total_minutes = int(parts[3])
    employee.max_consecutive_shifts = int(parts[4])
    employee.min_consecutive_shifts = int(parts[5])
    employee.min_consecutive_days_off = int(parts[6])
    employee.max_weekends = int(parts[7])

    return employee

def days_off_parser(text):
    parts = text.split(',')
    return (parts[0], intify(parts[1:]))

def shift_request_parser(text):
    parts = text.split(',')

    return (parts[0], int(parts[1]), parts[2], int(parts[3]))

def section_cover_parser(text):
    parts = text.split(',')
    return (int(parts[0]), parts[1], int(parts[2]), int(parts[3]), int(parts[4]))

def merge_data(data):
    indices = {}
    employees = data['staff']
    shifts = data['shifts']
    days = data['days'][0]
    section_covers = {}
    daily_on_requests = {}
    daily_off_requests = {}

    for cover in data['section_cover']:
        if cover[0] in section_covers:
            section_covers[cover[0]].append(cover[1:])
        else:
            section_covers[cover[0]] = [cover[1:]]



    # Enumerate employees by name
    for i, employee in enumerate(employees):
        indices[employee.name] = i

    # Add employee days off
    for (name, d_off) in data['days_off']:
        employees[indices[name]].days_off = d_off

    # Add employee shift on/off requests
    for shift in data['shift_on_reqs']:
        employees[indices[shift[0]]].add_shift_on_request(shifts[1:])

    for shift in data['shift_off_reqs']:
        employees[indices[shift[0]]].add_shift_off_request(shifts[1:])

    return Problem(days, section_covers, employees, shifts)

class Parser(object):
    def __init__(self):
        self._block_parsers = []
        self._post_process = lambda x : x
        self._comment_pattern = re.compile('^\s*\#.*$')

        self.add_block_parser('days', day_count_parser)
        self.add_block_parser('shifts', shifts_parser)
        self.add_block_parser('staff', staff_parser)
        self.add_block_parser('days_off', days_off_parser)
        self.add_block_parser('shift_on_reqs', shift_request_parser)
        self.add_block_parser('shift_off_reqs', shift_request_parser)
        self.add_block_parser('section_cover', section_cover_parser)

        self.set_postprocessor(merge_data)

    def _is_comment(self, line):
        return self._comment_pattern.search(line) is not None

    def _parse_block(self, line_generator, parse):
        values = []
        is_title_read = False

        for line in line_generator:
            if(self._is_comment(line)):
                continue

            if not is_title_read:
                is_title_read = True
                continue

            if not line.strip():
                break

            values.append(parse(line.strip()))

        return line_generator, values

    def add_block_parser(self, name, parser):
        self._block_parsers.append((name, parser))

    def set_postprocessor(self, pp):
        self._post_process = pp

    def parse(self, file_name):
        f = open(file_name, 'r')
        results = {}

        for name, parser in self._block_parsers:
            _, vals = self._parse_block(f, parser)
            results[name] = vals

        return self._post_process(results)
