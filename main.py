import csv
from datetime import datetime, timedelta
from enum import IntEnum, Flag, auto
from typing import NamedTuple
from abc import ABC, abstractmethod
from ortools.sat.python import cp_model

from scheduler import ScheduleModel, ScheduleSolver

class DutyType(Flag):
    CONTROLLER = auto()
    OBSERVER = auto()
    RECORDER = auto()
    SPOTTER = auto()
    LONER = auto()
    OPS_SUP = auto()
    SOF = auto()

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

class Person:
    prsn_id: int
    _first_name: str
    _last_name: str
    _quals: DutyType

    def __init__(self, prsn_id: int, last_name: str, first_name: str):
        self.prsn_id = prsn_id
        self._first_name = first_name
        self._last_name = last_name
        self._quals: DutyType = DutyType.CONTROLLER & DutyType.OBSERVER

    def qual(self, type: DutyType):
        self._quals = self._quals | type

    def is_qualified(self, type: DutyType) -> bool:
        return (self._quals & type) != (DutyType.CONTROLLER & ~DutyType.CONTROLLER) ## TODO: This is a very hacky way for bitwise 0

class Commitment(ABC):
    def is_conflict(self, other) -> bool:
        return other.end_dt() > self.start_dt() and other.start_dt() < self.end_dt()

    @abstractmethod
    def start_dt(self) -> datetime:
        pass

    @abstractmethod
    def end_dt(self) -> datetime:
        pass

class Duty(Commitment):
    name: str
    type: DutyType
    _sign_in_dt: datetime
    _sign_out_dt: datetime

    def __init__(self, name: str, type: DutyType, sign_in_dt: datetime, sign_out_dt: datetime):
        self.name = name
        self.type = type
        self._sign_in_dt = sign_in_dt
        self._sign_out_dt = sign_out_dt

    def start_dt(self) -> datetime:
        return self._sign_in_dt

    def end_dt(self) -> datetime:
        return self._sign_out_dt

class Line(Commitment):
    number: int
    time_brief: datetime
    time_takeoff: datetime
    time_debrief_end: datetime

    def __init__(self, number: int, time_takeoff: datetime):
        self.number = number
        self.time_takeoff = time_takeoff
        self.time_brief = time_takeoff - timedelta(hours=1, minutes=15)
        self.time_debrief_end = self.time_brief + timedelta(hours=3, minutes=30)

    def start_dt(self) -> datetime:
        return self.time_brief

    def end_dt(self) -> datetime:
        return self.time_debrief_end

class AbsenceRequest(Commitment):
    _prsn_id: int
    _start_dt: datetime
    _end_dt: datetime

    def __init__(self, prsn_id: int, start_dt: datetime, end_dt: datetime):
        self._prsn_id = prsn_id
        self._start_dt = start_dt
        self._end_dt = end_dt

    def __str__(self) -> str:
        return self._start_dt.strftime('%m/%d/%Y %I:%M:%S %p') + " " + self._end_dt.strftime('%m/%d/%Y %I:%M:%S %p')

    def start_dt(self) -> datetime:
        return self._start_dt

    def end_dt(self) -> datetime:
        return self._end_dt

    def assigned_to(self, prsn: Person) -> bool:
        return self._prsn_id == prsn.prsn_id

def parse_csv(file: str, parse_fn):
    all_objs = []

    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)

        all_objs = [parse_fn(row) for row in reader]

    return all_objs

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

def get_duties_conflicting_with_duty(duty: Duty, duties: list[Duty]) -> list[Duty]:
    conflicting_duties = [d for d in duties if duty.is_conflict(d)]
    return conflicting_duties

def duty_day_exceeded(c1: Commitment, c2: Commitment) -> bool:
    td1:timedelta = c1.end_dt() - c2.start_dt()
    td1_hrs = td1.total_seconds() / 3600.0

    td2:timedelta = c2.end_dt() - c1.start_dt()
    td2_hrs = td2.total_seconds() / 3600.0

    return td1_hrs > 12.0 or td2_hrs > 12.0

def run():
    print("Entering Run")

    RES_DIR = 'res/'

    duty_schedule_file = RES_DIR + 'duty_schedule.csv'
    flying_schedule_file = RES_DIR + 'flying_schedule.csv'
    lox_file = RES_DIR + 'lox.csv'
    absence_request_file = RES_DIR + 'absence_requests.csv'

    all_duties: list[Duty] = parse_csv(duty_schedule_file, parse_duties)
    #all_duties= [Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Duty("Tinder 2 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 11:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Duty("Tinder 3 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 11:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 12:00:00 PM', '%m/%d/%Y %I:%M:%S %p'))]
    all_lines: list[Line] = parse_csv(flying_schedule_file, parse_shell_lines)
    #all_lines = [Line(1, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, datetime.strptime('7/29/2022 12:30:00 PM', '%m/%d/%Y %I:%M:%S %p')), Line(3, datetime.strptime('7/29/2022 2:00:00 PM', '%m/%d/%Y %I:%M:%S %p'))] 
    all_personnel: list[Person] = parse_csv(lox_file, parse_personnel)
    #keeler = Person(1, "Keeler", "Joshua")
    #keeler.qual(DutyType.CONTROLLER)
    #hannon = Person(2, "Phil", "Hannon")
    #hannon.qual(DutyType.CONTROLLER)
    #all_personnel = [keeler, hannon]
    all_absences: list[AbsenceRequest] = parse_csv(absence_request_file, parse_absence_requests)
    #all_absences: list[AbsenceRequest] = [AbsenceRequest(1, datetime.strptime('7/29/2022 5:44:00 PM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 6:35:00 PM', '%m/%d/%Y %I:%M:%S %p'))]
    #all_absences = []

    model = ScheduleModel()
    solver = ScheduleSolver(model)
    solution = solver.solve()

#    model = cp_model.CpModel()
#
#    # create all duty variables
#    duty_schedule = {}
#    for duty in all_duties:
#        for p in all_personnel:
#            duty_schedule[(duty.name, p.prsn_id)] = model.NewBoolVar('duty_s%s%i' % (duty.name, p.prsn_id))    
#
#    # create all flying line variables
#    flying_schedule = {}
#    for curr_line in all_lines:
#        for p in all_personnel:
#            flying_schedule[(curr_line.number, p.prsn_id)] = model.NewBoolVar('line_n%ipilot_n%i' % (curr_line.number, p.prsn_id))
#    
#    # all duties filled with respective qual'd personnel
#    for duty in all_duties:
#        model.AddExactlyOne(duty_schedule[(duty.name, p.prsn_id)] for p in all_personnel)
#
##   TODO: refactor/test this!
##    # must have turn time between duties
#    for duty in all_duties:
#        conflicting_duties = get_duties_conflicting_with_duty(duty, all_duties)
#
#        for p in all_personnel:
#            conflicting_duties_for_person = []
#
#            for cd in conflicting_duties:
#                conflicting_duties_for_person.append(duty_schedule[(cd.name, p.prsn_id)])
#
#            model.Add(sum(conflicting_duties_for_person) <= 1)
#    
#    # must be qualified for duty
#    for duty in all_duties:
#        duties_to_be_scheduled = [duty_schedule[(duty.name, p.prsn_id)] for p in all_personnel if p.is_qualified(duty.type)]
#        model.Add(sum(duties_to_be_scheduled) == 1)
#
#    # limit lines to at most one pilot
#    for curr_line in all_lines:
#        pilots_in_line = [flying_schedule[(curr_line.number, p.prsn_id)] for p in all_personnel]
#        model.Add(sum(pilots_in_line) <= 1)
#
#    # max number of events
#    MAX_NUM_EVENTS_PER_PERSON = 3
#    for p in all_personnel:
#        events_per_person = []
#
#        for curr_line in all_lines:
#            events_per_person.append(flying_schedule[(curr_line.number, p.prsn_id)])
#
#        for duty in all_duties:
#            events_per_person.append(duty_schedule[(duty.name, p.prsn_id)])
#
#        model.Add(sum(events_per_person) <= MAX_NUM_EVENTS_PER_PERSON)
#
#    # all pilots must have turn time between sorties 
#    for p in all_personnel: 
#        for curr_line in all_lines:
#            csp_allowed_lines = [flying_schedule[(stepped_line.number, p.prsn_id)] for stepped_line in all_lines if curr_line.is_conflict(stepped_line)]
#            model.Add(sum(csp_allowed_lines) <= 1)
#
#    # must have turn time between duty and flight
#    for p in all_personnel:
#        for d in all_duties:
#            fl = [flying_schedule[(l.number, p.prsn_id)] for l in all_lines if l.is_conflict(d)]
#            model.Add(sum(fl) == 0).OnlyEnforceIf(duty_schedule[(d.name, p.prsn_id)])
#
#    #TODO: test this!
#    # must have 12 hour duty day
#    for p in all_personnel:
#        for duty in all_duties:
#            csp_forbidden_duties = [duty_schedule[(d.name, p.prsn_id)] for d in all_duties if duty_day_exceeded(duty, d)]
#            csp_forbidden_lines = [flying_schedule[(l.number, p.prsn_id)] for l in all_lines if duty_day_exceeded(duty, d)]
#            model.Add(sum(csp_forbidden_duties) + sum(csp_forbidden_lines) == 0).OnlyEnforceIf(duty_schedule[(duty.name, p.prsn_id)])
#        
#        for line in all_lines:
#            csp_forbidden_duties = [duty_schedule[(d.name, p.prsn_id)] for d in all_duties if duty_day_exceeded(line, d)]
#            csp_forbidden_lines = [flying_schedule[(l.number, p.prsn_id)] for l in all_lines if duty_day_exceeded(line, l)]
#            model.Add(sum(csp_forbidden_duties) + sum(csp_forbidden_lines) == 0).OnlyEnforceIf(flying_schedule[(line.number, p.prsn_id)])
#
#    # honor absence requests  for every person
#    for p in all_personnel:
#        persons_absence_requests = [ar for ar in all_absences if ar.assigned_to(p)]
#
#        for ar in persons_absence_requests:
#            csp_conflicting_lines = [flying_schedule[(curr_line.number, p.prsn_id)] for l in all_lines if l.is_conflict(ar)]
#            model.Add(sum(csp_conflicting_lines) == 0)
#
#    # maximize the lines filled by IPs
#    lines_filled = []
#    for l in all_lines:
#        for p in all_personnel:
#            lines_filled.append(flying_schedule[(l.number, p.prsn_id)])
#
#    model.Maximize(sum(lines_filled))
#
#    solver = cp_model.CpSolver()
#    solver.parameters.enumerate_all_solutions = True
#
#    printer = ScheduleSolverPrinter(duty_schedule, flying_schedule, all_duties, all_lines, all_personnel, 5)
#    solver.Solve(model, printer)

    print("Exiting Run")

if __name__ == "__main__":
    run()
