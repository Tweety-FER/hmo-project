# -*- coding: utf-8 -*-

from GABase import Evaluator, Instance, PopulationGenerator
from random import random, randint, choice
from math import floor
from sys import exit

N_MUTATIONS = 2 # Maximum number of possible mutations in generation
P_MUTATION = 0.1

HARD_CONSTR_PENALTY = 2500 # Penalty for each break of hard constraints

def is_saturday(day):
    return day % 7 == 5

def is_sunday(day):
    return day % 7 == 6

def unshared_copy(inList):
    if isinstance(inList, list):
        return list( map(unshared_copy, inList) )
    return inList

class ScheduleInstance(Instance):
    def __init__(self, days = 0, employees = [], shift_names = []):
        self._matrix = []
        self._shift_names = shift_names

        for employee in employees:
            row = []

            for i in xrange(days):
                row.append(None)

            self._matrix.append(row)

        if self._matrix:
            self._rows = len(self._matrix)
            self._cols = len(self._matrix[0])

    def __str__(self):
        lines = []

        for assignments in self._matrix:
            lines.append('\t'.join(assignments))

        return '\n'.join(lines)

    def _swap_rows(self, i, j):
        self._matrix[i], self._matrix[j] = self._matrix[j][:], self._matrix[i][:]

    def _swap_cols(self, i, j):
        for k in xrange(self._rows):
            self._matrix[k][i], self._matrix[k][j] = self._matrix[k][j], self._matrix[k][i]

    def _set_random(self, value):
        i = randint(0, self._rows - 1)
        j = randint(0, self._cols - 1)

        self._matrix[i][j] = value

    def mutate(self):
        mutant = ScheduleInstance()
        mutant._matrix = unshared_copy(self._matrix)
        mutant._shift_names = self._shift_names

        mutant._rows = self._rows
        mutant._cols = self._cols

        for i in xrange(N_MUTATIONS):
            if random() <= P_MUTATION:
                mut_choice = randint(1, 4)

                if mut_choice == 1: #Unset assignment
                    self._set_random('')
                elif mut_choice == 2: #Set assignment
                    self._set_random(choice(self._shift_names))
                elif mut_choice == 3: #Swap two assignments in row
                    row = randint(0, self._rows - 1)
                    j = randint(0, self._cols - 1)
                    k = randint(0, self._cols - 1)

                    mutant._matrix[row][j], mutant._matrix[row][k] = \
                        mutant._matrix[row][k], mutant._matrix[row][j]
                else: #Swap two assignments in col
                    col = randint(0, self._cols - 1)

                    j = randint(0, self._rows - 1)
                    k = randint(0, self._rows - 1)

                    mutant._matrix[j][col], mutant._matrix[k][col] = \
                        mutant._matrix[k][col], mutant._matrix[j][col]


                #elif mut_choice == 3:
                #    mutant._swap_rows(randint(0, self._rows - 1), randint(0, self._rows - 1))
                #else:
                #    mutant._swap_cols(randint(0, self._cols - 1), randint(0, self._cols - 1))

        return mutant


    def cross(self, other):
        #Uniform cross on rows (inherit one of the mployee assignments)
        baby = ScheduleInstance()
        baby._shift_names = self._shift_names
        baby._matrix = []
        baby._rows = self._rows
        baby._cols = self._cols

        cross_week = floor(randint(0, self._rows - 1) // 7)
        cross_day = cross_week * 7

        for i in xrange(self._rows):
            if i < cross_day:
                baby._matrix.append(unshared_copy(self._matrix[i]))
            else:
                baby._matrix.append(unshared_copy(other._matrix[i]))

        return baby


class ScheduleEvaluator(Evaluator):
    def __init__(self, problem):
        self._problem = problem
        self._employee_map = {}
        self._shift_map = {}

        for i, e in enumerate(self._problem.employees):
            self._employee_map[e.name] = i

        for i, s in enumerate(self._problem.shifts):
            self._shift_map[s.name] = i

    def evaluate(self, inst):
        broke_hard, score = self._evaluate(inst)

        if broke_hard:
            score += HARD_CONSTR_PENALTY * broke_hard

        return score

    def is_feasible(self, inst):
        broke_hard, score = self._evaluate(inst)
        return broke_hard == 0

    def _evaluate(self, inst):
        """
        Computes the score of a potential solutions (the penalty), and whether
        any hard constraints were broken.
        """
        score = 0
        broke_hard = 0

        # Let us first iterate through the employee row related stuff
        for i in xrange(inst._rows):
            broke_hard_empl, score_empl = self._evaluate_for_employee(inst._matrix[i], i)

            broke_hard += broke_hard_empl

            score += score_empl

        # Now we need to check if the shift covers were satisfied
        score += self._evaluate_section_covers(inst)

        return broke_hard, score


    def _evaluate_section_covers(self, inst):
        score = 0

        for col in xrange(inst._cols): #For each day
            shift_covers = {}

            if not self._problem.section_covers[col]:
                continue #Nothing to check

            for shift in self._problem.shifts:
                shift_covers[shift.name] = 0

            for row in xrange(inst._rows):
                val = inst._matrix[row][col]

                if val:
                    shift_covers[val] += 1

            for shift in shift_covers:
                for name, req, w_under, w_over in self._problem.section_covers[col]:
                    if name == shift:
                        if shift_covers[shift] < req:
                            score += w_under
                        if shift_covers[shift] > req:
                            score += w_over

        return score

    def _evaluate_for_employee(self, row, i):
        prev_shift = None
        max_shifts = {}
        time_worked = 0
        work_streak = None
        vacation_streak = None
        work_weekends = 0
        employee = self._problem.employees[i]
        score = 0
        already_worked_this_weekend = False
        prev_shift = None
        broke_hard = 0

        for name in self._shift_map:
            max_shifts[name] = 0

        for day in xrange(self._problem.days):
            shift_name = row[day]

            if is_saturday(day):
                already_worked_this_weekend = False

            if shift_name:
                shift = self._problem.shifts[self._shift_map[shift_name]]

                if work_streak is None:
                    work_streak = 0

                work_streak += 1

                if is_saturday(day):
                    work_weekends += 1
                    already_worked_this_weekend = True # Do not count one weekend twice

                if is_sunday and not already_worked_this_weekend:
                    work_weekends += 1

                # Vacation streak possibly just ended. Check if too short
                if vacation_streak is not None and vacation_streak < employee.min_consecutive_days_off:
                    print 'Under minimum vacations'
                    broke_hard += 1

                vacation_streak = 1 if vacation_streak is None else vacation_streak + 1

                # Check invalid shifts lined up
                if prev_shift:
                    actual_prev_shift = self._problem.shifts[self._shift_map[prev_shift]]
                    if not shift.can_follow(actual_prev_shift):
                        print 'Invalid shift follows this shift'
                        broke_hard += 1

                # Update shift counter
                max_shifts[shift_name] += 1

                #Check if day off
                if day in employee.days_off:
                    print 'Working on a day off'
                    broke_hard += 1



                # Update work hours
                time_worked += shift.time
            else:
                if vacation_streak is None:
                    vacation_streak = 0

                # Work streak possibly just ended. Check if in min, max bounds
                if work_streak is not None:
                    if work_streak < employee.min_consecutive_shifts or work_streak > employee.max_consecutive_shifts:
                        print 'Worked {} shifts when expecting [{}, {}]'.format(work_streak, employee.min_consecutive_shifts, employee.max_consecutive_shifts)
                        broke_hard += 1

                work_streak = None

                vacation_streak += 1

            # Soft constraint: requests for days on/off
            score += employee.get_shift_penalty(day, shift_name)

            prev_shift = shift_name

        # Check max shifts
        for shift in self._shift_map:
            if max_shifts.get(shift, 0) > employee.get_max_shift(shift):
                print 'Worked too many shifts of type {}: {} when max is {}'.format(shift, max_shifts.get(shift, 0), employee.get_max_shift(shift))
                broke_hard += 1

        # Check min and max work hours
        if time_worked < employee.min_total_minutes or time_worked > employee.max_total_minutes:
            print 'Worked total minutes {} when expecting [{}, {}]'.format(time_worked, employee.min_total_minutes, employee.max_total_minutes)
            broke_hard += 1

        # Check max work weekends
        if work_weekends > employee.max_weekends:
            print 'Worked too many weekends {}/{}'.format(work_weekends, employee.max_weekends)
            broke_hard += 1


        return broke_hard, score

class GreedySchedulePopulationGenerator(PopulationGenerator):
    """
    Tries a bit harder to satisfy the constraints
    """
    def __init__(self, problem):
        self._problem = problem
        self._shift_types = []
        self._no_follows = {}
        self._n_employees = len(problem.employees)
        self._shift_durations = {s.name : s.time for s in self._problem.shifts}

        for shift in self._problem.shifts:
            self._shift_types.append(shift.name)
            self._no_follows[shift.name] = shift.not_followed_by

    def _generate_employee_assignments(self, i, inst):
        work_weekends = 0
        work_streak = 0
        vacation_streak = 0
        time_worked = 0
        already_worked_this_weekend = False
        assigned_shifts = {shift : 0 for shift in self._shift_types}
        employee = self._problem.employees[i]
        prev_shift = ''
        possible_shifts = []

        for shift in self._shift_types:
            duration = self._shift_durations[shift]
            possible_shifts.append((shift, duration))

        possible_shifts = sorted(possible_shifts, key=lambda x: x[1])#, reverse=True)

        for day in xrange(self._problem.days):
            would_be_new_work_weekend = is_saturday(day) or (is_sunday(day) and not already_worked_this_weekend)

            # Check for situations when we CANNOT assign a user a task
            needs_vacation = work_streak == employee.max_consecutive_shifts
            is_day_off = day in employee.days_off
            done_working = time_worked == employee.max_total_minutes
            not_done_vacationing = 0 < vacation_streak < employee.min_consecutive_days_off
            too_many_work_weekends = work_weekends >= employee.max_weekends and would_be_new_work_weekend

            if needs_vacation or is_day_off or done_working or not_done_vacationing or too_many_work_weekends:
                work_streak = 0
                vacation_streak += 1
                prev_shift = ''

                inst._matrix[i][day] = ''

            else: # You're working, man
                # We need to find the shifts the person CAN work
                # They cannot work shifts that cannot follow this one,
                # shifts that would put them over the max hours or shifts
                # that they've already done enough of
                valid_shifts = []

                for shift, duration in possible_shifts:
                    if prev_shift and shift in self._no_follows[prev_shift]:
                        continue
                    if time_worked + duration > employee.max_total_minutes:
                        continue
                    if assigned_shifts[shift] + 1 > employee.get_max_shift(shift):
                        continue

                    valid_shifts.append((shift, duration))

                # TODO random choice?
                if valid_shifts: # Any actual choices left?
                    job, duration = valid_shifts[0]
                    time_worked += duration
                    prev_shift = job
                    assigned_shifts[job] += 1

                    work_streak += 1
                    vacation_streak = 0
                    inst._matrix[i][day] = job

                    if would_be_new_work_weekend:
                        work_weekends += 1

                else:
                    prev_shift = ''
                    vacation_streak += 1
                    work_streak = 0
                    inst._matrix[i][day] = ''

    def generate_population(self, size):
        # Completely randomply generate a population
        pops = []

        for i in xrange(size):
            inst = ScheduleInstance(self._problem.days, self._problem.employees, self._shift_types)
            for j in xrange(self._n_employees):
                self._generate_employee_assignments(j, inst)

            pops.append(inst)

        return pops
