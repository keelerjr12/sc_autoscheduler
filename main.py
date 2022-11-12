import csv
from datetime import datetime, timedelta
from enum import IntEnum, Flag, auto
from typing import NamedTuple
from abc import ABC, abstractmethod
from ortools.sat.python import cp_model

from scheduler import ScheduleModel, ScheduleSolver, Duty, DutyType, Line, Person, AbsenceRequest

def parse_csv(file: str, parse_fn):
    all_objs = []

    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)

        all_objs = [parse_fn(row) for row in reader]

    return all_objs

def str_to_duty_type(str_type: str) -> DutyType:
    lc_str_type = str_type.lower()

    if lc_str_type.find('controller') != -1:
        return DutyType.CONTROLLER
    elif lc_str_type.find('observer') != -1:
        return DutyType.OBSERVER
    elif lc_str_type.find('recorder') != -1:
        return DutyType.RECORDER
    elif lc_str_type.find('spotter') != -1:
        return DutyType.SPOTTER
    elif lc_str_type.find('loner') != -1:
        return DutyType.LONER
    elif lc_str_type.find('sof') != -1:
        return DutyType.SOF
    else:
        return DutyType.OPS_SUP

def parse_duties(str: str):
    return Duty(str[3], str_to_duty_type(str[3]), datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(str[10], '%m/%d/%Y %I:%M:%S %p'))

def parse_shell_lines(str: str):
    return Line(int(str[0]), datetime.strptime(str[1], '%m/%d/%Y %I:%M:%S %p'))

class LOX_COL(IntEnum):
    LAST_NAME = 0
    FIRST_NAME = 1
    PRSN_ID = 2
    OBSERVER = 11
    CONTROLLER = 12
    SOF = 13
    OPS_SUP = 14

def is_qualified(qual_row, qual: LOX_COL) -> bool:
    LOX_val = qual_row[qual]
    return (LOX_val.find('X') != -1) or (LOX_val.find('D') != -1)

def parse_personnel(str: str):
    last_name = str[LOX_COL.LAST_NAME]
    first_name = str[LOX_COL.FIRST_NAME]
    prsn_id = int(str[LOX_COL.PRSN_ID])

    p = Person(prsn_id, last_name, first_name)
    
    if is_qualified(str, LOX_COL.CONTROLLER) == True:
        p.qual(DutyType.CONTROLLER)

    if is_qualified(str, LOX_COL.OBSERVER) == True:
        p.qual(DutyType.OBSERVER)

    if is_qualified(str, LOX_COL.OPS_SUP) == True:
        p.qual(DutyType.OPS_SUP)

    if is_qualified(str, LOX_COL.SOF) == True:
        p.qual(DutyType.SOF)

    return p

def parse_absence_requests(str: str):
    prsn_id = int(str[2])
    start_dt = datetime.strptime(str[8], '%m/%d/%Y %I:%M:%S %p')
    end_dt = datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p')

    return AbsenceRequest(prsn_id, start_dt, end_dt)

class ScheduleSolverPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, duty_schedule, flying_schedule, duties: list[Duty], lines: list[Line], personnel: list[Person], limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._solution_count = 0
            self._solution_limit = limit

            self._duty_schedule = duty_schedule
            self._duties = duties

            self._flying_schedule = flying_schedule
            self._lines = lines
            self._personnel = personnel

        def on_solution_callback(self):
            self._solution_count += 1
            print('Solution %i' % self._solution_count)

            for d in self._duties:
                for p in self._personnel:
                    if self.Value(self._duty_schedule[(d.name, p.prsn_id)]):
                        print('  [%s]: sign-in: %s, sign-out: %s -- %s, %s' % (d.name, d.start_dt().strftime('%H%M'), d.end_dt().strftime('%H%M'), p._last_name, p._first_name))

            for l in self._lines:
                print('  [%i]: brief: %s, takeoff: %s, debrief_end: %s -- ' % (l.number, l.time_brief.strftime('%H%M'), l.time_takeoff.strftime('%H%M'), l.time_debrief_end.strftime('%H%M')), end='')

                for p in self._personnel:
                    if self.Value(self._flying_schedule[(l.number, p.prsn_id)]):
                        print(' %s, %s' % (p._last_name, p._first_name), end='')

                print()

            if self._solution_count >= self._solution_limit:
                print('Stop search after %i solutions' % self._solution_limit)
                self.StopSearch()

        def solution_count(self):
            return self._solution_count

def run():
    print("Entering Run")

    RES_DIR = 'res/'

    duty_schedule_file = RES_DIR + 'duty_schedule.csv'
    flying_schedule_file = RES_DIR + 'flying_schedule.csv'
    lox_file = RES_DIR + 'lox.csv'
    absence_request_file = RES_DIR + 'absence_requests.csv'

    all_duties: list[Duty] = parse_csv(duty_schedule_file, parse_duties)
    all_lines: list[Line] = parse_csv(flying_schedule_file, parse_shell_lines)
    all_personnel: list[Person] = parse_csv(lox_file, parse_personnel)
    all_absences: list[AbsenceRequest] = parse_csv(absence_request_file, parse_absence_requests)

    model = ScheduleModel(all_lines, all_duties, all_personnel, all_absences)
    solver = ScheduleSolver(model)
    (status, solution) = solver.solve()

    for d in all_duties:
        person = solution[d.name]
        print(d.name + ': ' + person._last_name, person._first_name)

    for l in all_lines:
        person = solution[l.number]
        print('[%i] brief: %s, takeoff: %s, debrief end: %s -- %s, %s' % (l.number, l.time_brief.strftime('%H%M'), l.time_takeoff.strftime('%H%M'), l.time_debrief_end.strftime('%H%M'), person._last_name, person._first_name))

#    # must have turn time between duty and flight
#    for p in all_personnel:
#        for d in all_duties:
#            fl = [flying_schedule[(l.number, p.prsn_id)] for l in all_lines if l.is_conflict(d)]
#            model.Add(sum(fl) == 0).OnlyEnforceIf(duty_schedule[(d.name, p.prsn_id)])
#
#

#    solver.parameters.enumerate_all_solutions = True
#    printer = ScheduleSolverPrinter(duty_schedule, flying_schedule, all_duties, all_lines, all_personnel, 5)
#    solver.Solve(model, printer)

    print("Exiting Run")

if __name__ == "__main__":
    run()
