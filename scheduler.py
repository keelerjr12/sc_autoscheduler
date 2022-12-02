from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum, Flag, auto
from ortools.sat.python import cp_model

def get_commitments_for_ausm_tier(tier: int):
    if (tier == 1):
        return 3
    if (tier == 2):
        return 5
    if (tier == 3):
        return 7
    if (tier == 4):
        return 9

class FlightOrg(Enum):
    M = auto()
    N = auto()
    O = auto()
    P = auto()
    X = auto()
    CHECK = auto()

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

    def __init__(self, prsn_id: int, last_name: str, first_name: str, ausm_tier: int):
        self.prsn_id = prsn_id
        self._first_name = first_name
        self._last_name = last_name
        self._duty_quals: DutyQual = DutyQual.CONTROLLER & DutyQual.OBSERVER
        self._flight_quals: FlightQual = FlightQual.PIT & ~FlightQual.PIT
        self._assigned_org = None
        self._ausm_tier = ausm_tier

    def assign_to(self, org: FlightOrg | None):
        self._assigned_org = org

    def qual_for_duty(self, type: DutyQual):
        self._duty_quals = self._duty_quals | type

    def qual_for_flight(self, type: FlightQual):
        self._flight_quals = self._flight_quals | type

    def is_qualified_for_duty(self, type: DutyQual) -> bool:
        return (self._duty_quals & type) != (DutyQual.CONTROLLER & ~DutyQual.CONTROLLER) ## TODO: This is a very hacky way for bitwise 0

    def is_qualified_for_flight(self, type: FlightQual) -> bool:
        return (self._flight_quals & type) != (FlightQual.PIT & ~FlightQual.PIT) ## TODO: This is a very hacky way for bitwise 0

class Commitment(ABC):
    #    TODO: issue with absence request; need to migrate to entity class
    #    @abstractmethod
    #    def id(self):
    #        pass

    @abstractmethod
    def start_dt(self) -> datetime:
        pass

    @abstractmethod
    def end_dt(self) -> datetime:
        pass

    def is_conflict(self, other) -> bool:
        return other.end_dt() > self.start_dt() and other.start_dt() < self.end_dt()

class Line(Commitment):

    def __init__(self,number: int, org: FlightOrg, time_takeoff: datetime):
        self.number = number
        self.flight_org = org

        self.time_takeoff = time_takeoff
        self.time_brief = time_takeoff - timedelta(hours=1, minutes=15)
        self.time_debrief_end = self.time_brief + timedelta(hours=3, minutes=30)

    def id(self):
        return str(self.number) + self.start_dt().strftime("%m/%d/%Y")

    def start_dt(self) -> datetime:
        return self.time_brief

    def end_dt(self) -> datetime:
        return self.time_debrief_end

class Duty(Commitment):

    def __init__(self, name: str, type: DutyQual, sign_in_dt: datetime, sign_out_dt: datetime):
        assert(sign_in_dt <= sign_out_dt)

        self.name = name
        self.type = type
        self._sign_in_dt = sign_in_dt
        self._sign_out_dt = sign_out_dt

    def id(self):
        return self.name + self._sign_in_dt.strftime("%m/%d/%Y")

    def start_dt(self) -> datetime:
        return self._sign_in_dt

    def end_dt(self) -> datetime:
        return self._sign_out_dt

class AbsenceRequest(Commitment):

    def __init__(self, prsn_id: int, start_dt: datetime, end_dt: datetime):
        assert(start_dt <= end_dt)

        self._prsn_id = prsn_id
        self._start_dt = start_dt
        self._end_dt = end_dt

    def __eq__(self, other):
        if (not isinstance(other, AbsenceRequest)):
            return NotImplemented

        return other._prsn_id == self._prsn_id and other._start_dt == self._start_dt and other._end_dt == self._end_dt

    def __str__(self) -> str:
        return self._start_dt.strftime('%m/%d/%Y %I:%M:%S %p') + " " + self._end_dt.strftime('%m/%d/%Y %I:%M:%S %p')

    def start_dt(self) -> datetime:
        return self._start_dt

    def end_dt(self) -> datetime:
        return self._end_dt

    def assigned_to(self, prsn: Person) -> bool:
        return self._prsn_id == prsn.prsn_id

class Day:

    def __init__(self, date: datetime.date):
        self.date = date
        self.lines = []
        self.duties = []

    def insert(self, commitment: Commitment):
        # TODO: refactor this for a dict of lists to get rid of if statement
        if (type(commitment) is Line):
            self.lines.append(commitment)
        elif (type(commitment) is Duty):
            self.duties.append(commitment)

class ShellSchedule:

    def __init__(self, lines, duties):
        self.days = []
        self._dates_used = {}

        commits = lines + duties

        for c in commits:
            date = c.start_dt().date()

            if (date not in self._dates_used):
                new_day = Day(date)
                self._dates_used[date] = new_day
                self.days.append(new_day)

            self._dates_used[date].insert(c)

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

# TODO: DESIGN: possibly a builder??????????
class ScheduleModel:

    def __init__(self, shell: ShellSchedule, personnel: list[Person], absences: list[AbsenceRequest]):
        self._commit_vars = {}
        self._model = cp_model.CpModel()

        self._shell = shell
        self._personnel = personnel
        self._absences = absences

        self._add_variables()
        self._add_objective()

    def _handle(self) -> cp_model.CpModel:
        return self._model

    def _variable(self, var: tuple) -> str:
        return self._commit_vars[var]
        
    def _add_variables(self):
        for day in self._shell.days:
            commits = day.duties + day.lines
        
            for c in commits:
                for p in self._personnel:
                    self._commit_vars[(day.date, c.id(), p.prsn_id)] = self._model.NewBoolVar('day_%s_commit_%s_pilot_%i' % (day.date, c.id(), p.prsn_id))

    def _constraint_absence_requests(self):
        for day in self._shell.days:
            commits = day.duties + day.lines

            for p in self._personnel:
                persons_absence_requests = [ar for ar in self._absences if ar.assigned_to(p)]
        
                for ar in persons_absence_requests:
                    csp_conflicts = [self._commit_vars[(day.date, c.id(), p.prsn_id)] for c in commits if c.is_conflict(ar)]
                    self._model.Add(sum(csp_conflicts) == 0)

    def _constraint_max_num_events(self):
        MAX_NUM_EVENTS_PER_PERSON = 3
        for day in self._shell.days:
            commits = day.duties + day.lines

            for p in self._personnel:
                events_per_person = [self._commit_vars[(day.date, c.id(), p.prsn_id)] for c in commits]
                self._model.Add(sum(events_per_person) <= MAX_NUM_EVENTS_PER_PERSON)

    def _constraint_max_duty_day(self):
        #TODO: test this!
        for day in self._shell.days:
            commits = day.duties + day.lines

            for p in self._personnel:
                for outer in commits:
                    csp_conflicts = [self._commit_vars[(day.date, inner.id(), p.prsn_id)] for inner in commits if duty_day_exceeded(outer, inner)]
                    self._model.Add(sum(csp_conflicts) == 0).OnlyEnforceIf(self._commit_vars[(day.date, outer.id(), p.prsn_id)])

    def _constraint_duty_filled_with_single_person(self):
        for day in self._shell.days:
            for duty in day.duties:
                self._model.AddExactlyOne(self._commit_vars[(day.date, duty.id(), p.prsn_id)] for p in self._personnel)

    def _constraint_flight_filled_with_at_most_single_person(self):
        for day in self._shell.days:
            for curr_line in day.lines:
                pilots_in_line = [self._commit_vars[(day.date, curr_line.id(), p.prsn_id)] for p in self._personnel]
                self._model.Add(sum(pilots_in_line) <= 1)
            
    def _constraint_min_turn_time_between_commitments(self):
        #TODO: test this!!!
        for day in self._shell.days:
            commits = day.duties + day.lines

            for p in self._personnel:
                for outer in commits:
                    conflicts = [self._commit_vars[(day.date, inner.id(), p.prsn_id)] for inner in commits if inner.is_conflict(outer)]
                    self._model.Add(sum(conflicts) <= 1).OnlyEnforceIf(self._commit_vars[(day.date, outer.id(), p.prsn_id)])

    def _constraint_max_turn_time_between_flight_and_flight(self):
        #TODO: write unit tests for this
        for day in self._shell.days:
            for p in self._personnel:
                for line in day.lines:
                    csp_forbidden_lines = [self._commit_vars[(day.date, l.id(), p.prsn_id)] for l in day.lines if has_turn_time(line, l, timedelta(hours = 4, minutes = 15))]
                    self._model.Add(sum(csp_forbidden_lines) == 0).OnlyEnforceIf(self._commit_vars[(day.date, line.id(), p.prsn_id)])

    def _constraint_personnel_qualified_for_duty(self):
        for day in self._shell.days:
            for duty in day.duties:
                duties_to_be_scheduled = [self._commit_vars[(day.date, duty.id(), p.prsn_id)] for p in self._personnel if p.is_qualified_for_duty(duty.type)]
                self._model.Add(sum(duties_to_be_scheduled) == 1)

    def _constraint_personnel_qualified_for_PIT(self):
        for day in self._shell.days:
            for p in self._personnel:
                forbidden_flights = [self._commit_vars[(day.date, l.id(), p.prsn_id)] for l in day.lines if (l.flight_org == FlightOrg.X and not p.is_qualified_for_flight(FlightQual.PIT))]
                self._model.Add(sum(forbidden_flights) == 0)

    def _add_objective(self):
        # minimize the unfilled lines
        lines_filled = []
        for day in self._shell.days:
            for l in day.lines:
                for p in self._personnel:
                    lines_filled.append(self._commit_vars[(day.date, l.id(), p.prsn_id)])

        ## minimize misassigned IPs by flight org
        lines_with_misassigned = []
        for day in self._shell.days:
            for l in day.lines:
                for p in self._personnel:
                    if (p._assigned_org != None and p._assigned_org != l.flight_org):
                        lines_with_misassigned.append(self._commit_vars[(day.date, l.id(), p.prsn_id)])

        # TODO: move this to a function
        num_total_lines = len([l for d in self._shell.days for l in d.lines])

        # calculuate MSE for AUSM tiers
        epsilon = 10
        for p in self._personnel:
            scheduled_commitments = []
            for day in self._shell.days:
                commitments = day.lines + day.duties
                for c in commitments:
                    scheduled_commitments.append(self._commit_vars[(day.date, c.id(), p.prsn_id)])

            commitment_requirement = get_commitments_for_ausm_tier(p._ausm_tier)
            self._model.Add(sum(scheduled_commitments)  <= commitment_requirement + epsilon)
            self._model.Add(sum(scheduled_commitments)  >= commitment_requirement - epsilon)

        self._model.Minimize((num_total_lines - sum(lines_filled)) + sum(lines_with_misassigned) + epsilon)

    constraints = {
        "Absence Request": _constraint_absence_requests,
        "Max Events": _constraint_max_num_events,
        "Max Duty Day": _constraint_max_duty_day,
        "Fill Duties": _constraint_duty_filled_with_single_person,
        "Fill Flights": _constraint_flight_filled_with_at_most_single_person,
        "Min Turn Time": _constraint_min_turn_time_between_commitments,
        "Max Turn Time": _constraint_max_turn_time_between_flight_and_flight,
        "Duty Qualified Personnel": _constraint_personnel_qualified_for_duty,
        "PIT Qualified Personnel": _constraint_personnel_qualified_for_PIT
    }

    def add_all_contraints(self):
        for con in self.constraints.keys():
            self.add_constraint(con)

    def add_constraint(self, constraint_nm: str):
        fn = self.constraints[constraint_nm]
        fn(self)

class ScheduleSolver:
    
    def __init__(self, model:ScheduleModel, personnel: list[Person], shell: ShellSchedule):
        self._model = model
        self._personnel = personnel
        self._shell = shell

    def solve(self) -> bool:

        solver = cp_model.CpSolver()
        status = solver.Solve(self._model._handle())

        if status != cp_model.OPTIMAL:
            return (status, {})

        return (status, self._get_solution(solver))


    def _get_solution(self, solver: cp_model.CpSolver):
        solution = {}

        for day in self._shell.days:
            for d in day.duties:
                solution[d.id()] = None

                for p in self._personnel:
                    if solver.Value(self._model._variable((day.date, d.id(), p.prsn_id))):
                        solution[d.id()] = p

            for l in day.lines:
                solution[l.id()] = None

                for p in self._personnel:
                    if solver.Value(self._model._variable((day.date, l.id(), p.prsn_id))):
                        solution[l.id()] = p

        return solution
