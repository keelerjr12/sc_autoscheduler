from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, Flag, auto
from ortools.sat.python import cp_model

class DutyQual(Flag):
    CONTROLLER = auto()
    OBSERVER = auto()
    RECORDER = auto()
    SPOTTER = auto()
    LONER = auto()
    OPS_SUP = auto()
    SOF = auto()

class FlightQual(Flag):
    PIT = auto()
    CHECK = auto()

class Person:
    prsn_id: int
    _first_name: str
    _last_name: str
    _duty_quals: DutyQual
    _flight_quals: FlightQual 

    def __init__(self, prsn_id: int, last_name: str, first_name: str):
        self.prsn_id = prsn_id
        self._first_name = first_name
        self._last_name = last_name
        self._duty_quals: DutyQual = DutyQual.CONTROLLER & DutyQual.OBSERVER
        self._flight_quals: FlightQual = FlightQual.PIT & ~FlightQual.PIT

    def qual_for_duty(self, type: DutyQual):
        self._duty_quals = self._duty_quals | type

    def qual_for_flight(self, type: FlightQual):
        self._flight_quals = self._flight_quals | type

    def is_qualified_for_duty(self, type: DutyQual) -> bool:
        return (self._duty_quals & type) != (DutyQual.CONTROLLER & ~DutyQual.CONTROLLER) ## TODO: This is a very hacky way for bitwise 0

    def is_qualified_for_flight(self, type: FlightQual) -> bool:
        return (self._flight_quals & type) != (FlightQual.PIT & ~FlightQual.PIT) ## TODO: This is a very hacky way for bitwise 0

class Commitment(ABC):
    def is_conflict(self, other) -> bool:
        return other.end_dt() > self.start_dt() and other.start_dt() < self.end_dt()

    @abstractmethod
    def start_dt(self) -> datetime:
        pass

    @abstractmethod
    def end_dt(self) -> datetime:
        pass

class FlightOrg(Enum):
    M = auto()
    N = auto()
    O = auto()
    P = auto()
    X = auto()

class Line(Commitment):
    number: int
    flight_org: FlightOrg

    time_brief: datetime
    time_takeoff: datetime
    time_debrief_end: datetime

    def __init__(self, number: int, org: FlightOrg, time_takeoff: datetime):
        self.number = number
        self.flight_org = org

        self.time_takeoff = time_takeoff
        self.time_brief = time_takeoff - timedelta(hours=1, minutes=15)
        self.time_debrief_end = self.time_brief + timedelta(hours=3, minutes=30)

    def start_dt(self) -> datetime:
        return self.time_brief

    def end_dt(self) -> datetime:
        return self.time_debrief_end

class Duty(Commitment):
    name: str
    type: DutyQual
    _sign_in_dt: datetime
    _sign_out_dt: datetime

    def __init__(self, name: str, type: DutyQual, sign_in_dt: datetime, sign_out_dt: datetime):
        self.name = name
        self.type = type
        self._sign_in_dt = sign_in_dt
        self._sign_out_dt = sign_out_dt

    def start_dt(self) -> datetime:
        return self._sign_in_dt

    def end_dt(self) -> datetime:
        return self._sign_out_dt

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

class ScheduleModel:
    lines: list[Line] = []
    duties: list[Duty] = []
    personnel: list[Person] = []
    absences: list[AbsenceRequest] = []
    
    def __init__(self, lines: list[Line], duties: list[Duty], personnel: list[Person], absences: list[AbsenceRequest]):
        self.lines = lines
        self.duties = duties
        self.personnel = personnel
        self.absences = absences

def duty_day_exceeded(c1: Commitment, c2: Commitment) -> bool:
    td1:timedelta = c1.end_dt() - c2.start_dt()
    td1_hrs = td1.total_seconds() / 3600.0

    td2:timedelta = c2.end_dt() - c1.start_dt()
    td2_hrs = td2.total_seconds() / 3600.0

    return td1_hrs > 12.0 or td2_hrs > 12.0

def has_turn_time(l1: Line, l2: Line, td: timedelta) -> bool:
    td1 :timedelta = l1.time_takeoff - l2.time_takeoff
    td2 :timedelta = l2.time_takeoff - l1.time_takeoff

    return td1 > td or td2 > td

def get_duties_conflicting_with_duty(duty: Duty, duties: list[Duty]) -> list[Duty]:
    conflicting_duties = [d for d in duties if duty.is_conflict(d)]
    return conflicting_duties

class ScheduleSolver:
    _flying_schedule_vars = {}
    _duty_schedule_vars = {}
    
    def __init__(self, personnel, lines, duties, absences):
        self._personnel = personnel
        self._lines = lines
        self._duties = duties
        self._absences = absences

    def solve(self) -> bool:
        model = cp_model.CpModel()

        self._add_variables(model)
        self._add_constraints(model)
        self._add_objective(model)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status != cp_model.OPTIMAL:
            return (status, {})

        return (status, self._get_solution(solver))

    def _add_variables(self, model: cp_model.CpModel):
        # create all duty variables
        for duty in self._duties:
            for person in self._personnel:
                self._duty_schedule_vars[(duty.name, person.prsn_id)] =  model.NewBoolVar('duty_s%s%i' % (duty.name, person.prsn_id))
        
        # create all flying line variables
        for curr_line in self._lines:
            for p in self._personnel:
                self._flying_schedule_vars[(curr_line.number, p.prsn_id)] = model.NewBoolVar('line_n%ipilot_n%i' % (curr_line.number, p.prsn_id))

    def _constraint_absence_requests(self, model: cp_model.CpModel):
        for p in self._personnel:
            persons_absence_requests = [ar for ar in self._absences if ar.assigned_to(p)]
    
            for ar in persons_absence_requests:
                csp_conflicting_lines = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if l.is_conflict(ar)]
                model.Add(sum(csp_conflicting_lines) == 0)

    def _constraint_max_num_events(self, model: cp_model.CpModel):
        MAX_NUM_EVENTS_PER_PERSON = 3
        for p in self._personnel:
            events_per_person = []

            for curr_line in self._lines:
                events_per_person.append(self._flying_schedule_vars[(curr_line.number, p.prsn_id)])

            for duty in self._duties:
                events_per_person.append(self._duty_schedule_vars[(duty.name, p.prsn_id)])

            model.Add(sum(events_per_person) <= MAX_NUM_EVENTS_PER_PERSON)

    def _constraint_max_duty_day(self, model: cp_model.CpModel):
        #TODO: test this!
        for p in self._personnel:
            for duty in self._duties:
                csp_forbidden_duties = [self._duty_schedule_vars[(d.name, p.prsn_id)] for d in self._duties if duty_day_exceeded(duty, d)]
                csp_forbidden_lines = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if duty_day_exceeded(duty, l)]
                model.Add(sum(csp_forbidden_duties) + sum(csp_forbidden_lines) == 0).OnlyEnforceIf(self._duty_schedule_vars[(duty.name, p.prsn_id)])
            
            for line in self._lines:
                csp_forbidden_duties = [self._duty_schedule_vars[(d.name, p.prsn_id)] for d in self._duties if duty_day_exceeded(line, d)]
                csp_forbidden_lines = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if duty_day_exceeded(line, l)]
                model.Add(sum(csp_forbidden_duties) + sum(csp_forbidden_lines) == 0).OnlyEnforceIf(self._flying_schedule_vars[(line.number, p.prsn_id)])

    def _constraint_duty_filled_with_single_person(self, model: cp_model.CpModel):
        for duty in self._duties:
            model.AddExactlyOne(self._duty_schedule_vars[(duty.name, p.prsn_id)] for p in self._personnel)

    def _constraint_flight_filled_with_at_most_single_person(self, model: cp_model.CpModel):
        for curr_line in self._lines:
            pilots_in_line = [self._flying_schedule_vars[(curr_line.number, p.prsn_id)] for p in self._personnel]
            model.Add(sum(pilots_in_line) <= 1)
            
    def _constraint_min_turn_time_between_duty_and_duty(self, model: cp_model.CpModel):
        # TODO: refactor/test this!
        for duty in self._duties:
            conflicting_duties = get_duties_conflicting_with_duty(duty, self._duties)
    
            for p in self._personnel:
                conflicting_duties_for_person = [self._duty_schedule_vars[(cd.name, p.prsn_id)] for cd in conflicting_duties]
    
                model.Add(sum(conflicting_duties_for_person) <= 1)

    def _constraint_min_turn_time_between_flight_and_flight(self, model: cp_model.CpModel):
        #TODO: write unit tests for this!
        for p in self._personnel:
            for curr_line in self._lines:
                csp_allowed_lines = [self._flying_schedule_vars[(stepped_line.number, p.prsn_id)] for stepped_line in self._lines if curr_line.is_conflict(stepped_line)]
                model.Add(sum(csp_allowed_lines) <= 1).OnlyEnforceIf(self._flying_schedule_vars[(curr_line.number, p.prsn_id)])
    
    def _constraint_min_turn_time_between_duty_and_flight(self, model: cp_model.CpModel):
        #TODO: test this!!!
        for p in self._personnel:
            for d in self._duties:
                fl = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if l.is_conflict(d)]
                model.Add(sum(fl) == 0).OnlyEnforceIf(self._duty_schedule_vars[(d.name, p.prsn_id)])

    def _constraint_min_turn_time_between_flight_and_duty(self, model: cp_model.CpModel):
        #TODO: test this!!!
        for p in self._personnel:
            for l in self._lines:
                fd = [self._duty_schedule_vars[(d.name, p.prsn_id)] for d in self._duties if d.is_conflict(l)]
                model.Add(sum(fd) == 0).OnlyEnforceIf(self._flying_schedule_vars[(l.number, p.prsn_id)])

    def _constraint_max_turn_time_between_flight_and_flight(self, model: cp_model.CpModel):
        #TODO: write unit tests for this
        for p in self._personnel:
            for line in self._lines:
                csp_forbidden_duties = []
                #csp_forbidden_duties = [self._duty_schedule_vars[(d.name, p.prsn_id)] for d in self._duties if has_turn_time(line, d, timedelta(hours = 4, minutes = 15))]
                csp_forbidden_lines = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if has_turn_time(line, l, timedelta(hours = 4, minutes = 15))]
                model.Add(sum(csp_forbidden_duties) + sum(csp_forbidden_lines) == 0).OnlyEnforceIf(self._flying_schedule_vars[(line.number, p.prsn_id)])

    def _constraint_personnel_qualified_for_duty(self, model: cp_model.CpModel):
        for duty in self._duties:
            duties_to_be_scheduled = [self._duty_schedule_vars[(duty.name, p.prsn_id)] for p in self._personnel if p.is_qualified_for_duty(duty.type)]
            model.Add(sum(duties_to_be_scheduled) == 1)

    def _constraint_personnel_qualified_for_PIT(self, model: cp_model.CpModel):
        for p in self._personnel:
            forbidden_flights = [self._flying_schedule_vars[(l.number, p.prsn_id)] for l in self._lines if (l.flight_org == FlightOrg.X and not p.is_qualified_for_flight(FlightQual.PIT))]
            model.Add(sum(forbidden_flights) == 0)

    def _add_constraints(self, model: cp_model.CpModel):
        self._constraint_absence_requests(model)
        self._constraint_max_num_events(model)
        self._constraint_max_duty_day(model)
        self._constraint_duty_filled_with_single_person(model)
        self._constraint_flight_filled_with_at_most_single_person(model)
        self._constraint_min_turn_time_between_duty_and_duty(model)
        self._constraint_min_turn_time_between_flight_and_flight(model)
        self._constraint_min_turn_time_between_duty_and_flight(model)
        self._constraint_min_turn_time_between_flight_and_duty(model)
        self._constraint_max_turn_time_between_flight_and_flight(model)
        self._constraint_personnel_qualified_for_duty(model)
        self._constraint_personnel_qualified_for_PIT(model)

    def _add_objective(self, model: cp_model.CpModel):
        # maximize the lines filled by IPs
        lines_filled = []
        for l in self._lines:
            for p in self._personnel:
                lines_filled.append(self._flying_schedule_vars[(l.number, p.prsn_id)])

        model.Maximize(sum(lines_filled))

    def _get_solution(self, solver: cp_model.CpSolver):
        solution = {}

        for d in self._duties:
            for p in self._personnel:
                if solver.Value(self._duty_schedule_vars[(d.name, p.prsn_id)]):
                    solution[d.name] = p

        for l in self._lines:
            solution[l.number] = None

            for p in self._personnel:
                if solver.Value(self._flying_schedule_vars[(l.number, p.prsn_id)]):
                    solution[l.number] = p

        return solution
