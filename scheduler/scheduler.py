from datetime import timedelta
from ortools.sat.python import cp_model
from scheduler.models import AbsenceRequest, Commitment, Day, Duty, DutyQual, FlightOrg, FlightQual, Line, Person

def get_commitments_for_ausm_tier(tier: int):
    if (tier == 1):
        return 3
    if (tier == 2):
        return 5
    if (tier == 3):
        return 7
    if (tier == 4):
        return 9

class ShellSchedule:

    def __init__(self, lines, duties):
        self._days = []
        self._dates_used = {}

        commits = lines + duties

        for c in commits:
            date = c.start_dt().date()

            if (date not in self._dates_used):
                new_day = Day(date)
                self._dates_used[date] = new_day
                self.days().append(new_day)

            self._dates_used[date].insert(c)

    def days(self) -> list[Day]:
        return self._days

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

def get_absence_requests_for_person(absence_requests: list[AbsenceRequest], person: Person):
    return [ar for ar in absence_requests if ar.assigned_to(person)]

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
        for day in self._shell.days():
            for commitment in day.commitments():
                for person in self._personnel:
                    self._commit_vars[(day.date, commitment.id(), person.id())] = self._model.NewBoolVar('day_%s_commit_%s_pilot_%i' % (day.date, commitment.id(), person.id()))

    def _constraint_absence_requests(self):
        for day in self._shell.days():
            commits = day.commitments()

            for person in self._personnel:
                persons_absence_requests = get_absence_requests_for_person(self._absences, person)
        
                for ar in persons_absence_requests:
                    csp_conflicts = [self._commit_vars[(day.date, c.id(), person.id())] for c in commits if c.is_conflict(ar)]
                    self._model.Add(sum(csp_conflicts) == 0)

    def _constraint_max_num_events(self):
        MAX_NUM_EVENTS_PER_PERSON = 3
        for day in self._shell.days():
            for person in self._personnel:
                events_per_person = [self._commit_vars[(day.date, commitment.id(), person.id())] for commitment in day.commitments()]
                self._model.Add(sum(events_per_person) <= MAX_NUM_EVENTS_PER_PERSON)

    def _constraint_max_duty_day(self):
        #TODO: test this!
        for day in self._shell.days():
            commits = day.commitments()

            for person in self._personnel:
                for outer in commits:
                    csp_conflicts = [self._commit_vars[(day.date, inner.id(), person.id())] for inner in commits if duty_day_exceeded(outer, inner)]
                    self._model.Add(sum(csp_conflicts) == 0).OnlyEnforceIf(self._commit_vars[(day.date, outer.id(), person.id())])

    def _constraint_duty_filled_with_single_person(self):
        for day in self._shell.days():
            for duty in day.commitments(Duty):
                self._model.AddExactlyOne(self._commit_vars[(day.date, duty.id(), person.id())] for person in self._personnel)

    def _constraint_flight_filled_with_at_most_single_person(self):
        for day in self._shell.days():
            for curr_line in day.commitments(Line):
                pilots_in_line = [self._commit_vars[(day.date, curr_line.id(), person.id())] for person in self._personnel]
                self._model.Add(sum(pilots_in_line) <= 1)
            
    def _constraint_min_turn_time_between_commitments(self):
        #TODO: test this!!!
        for day in self._shell.days():
            commits = day.commitments()

            for person in self._personnel:
                for outer in commits:
                    conflicts = [self._commit_vars[(day.date, inner.id(), person.id())] for inner in commits if inner.is_conflict(outer)]
                    self._model.Add(sum(conflicts) <= 1).OnlyEnforceIf(self._commit_vars[(day.date, outer.id(), person.id())])

    def _constraint_max_turn_time_between_flight_and_flight(self):
        #TODO: write unit tests for this
        for day in self._shell.days():
            for person in self._personnel:
                for line in day.commitments(Line):
                    csp_forbidden_lines = [self._commit_vars[(day.date, l.id(), person.id())] for l in day.commitments(Line) if has_turn_time(line, l, timedelta(hours = 4, minutes = 15))]
                    self._model.Add(sum(csp_forbidden_lines) == 0).OnlyEnforceIf(self._commit_vars[(day.date, line.id(), person.id())])

    def _constraint_personnel_qualified_for_duty(self):
        for day in self._shell.days():
            for duty in day.commitments(Duty):
                duties_to_be_scheduled = [self._commit_vars[(day.date, duty.id(), person.id())] for person in self._personnel if person.is_qualified_for_duty(duty.type)]
                self._model.Add(sum(duties_to_be_scheduled) == 1)

    def _constraint_personnel_qualified_for_PIT(self):
        for day in self._shell.days():
            for person in self._personnel:
                forbidden_flights = [self._commit_vars[(day.date, l.id(), person.id())] for l in day.commitments(Line) if (l.flight_org == FlightOrg.X and not person.is_qualified_for_flight(FlightQual.PIT))]
                self._model.Add(sum(forbidden_flights) == 0)

    def _add_duty_objective(self, duty_quals: DutyQual | list[DutyQual]):
        epsilon = self._model.NewIntVar(0, 10, duty_quals.__str__() + "_eps")

        for person in self._personnel:
            duty_tours = []
            for day in self._shell.days():
                for d in day.commitments(Duty):
                    if (d.is_type(duty_quals)):
                        duty_tours.append(self._commit_vars[(day.date, d.id(), person.id())])

            self._model.Add(sum(duty_tours) <= 0 + epsilon)
        
        return epsilon

    def _add_objective(self):
        # minimize the unfilled lines
        lines_filled = []
        for day in self._shell.days():
            for line in day.commitments(Line):
                for person in self._personnel:
                    lines_filled.append(self._commit_vars[(day.date, line.id(), person.id())])

        ## minimize misassigned IPs by flight org
        lines_with_misassigned = []
        for day in self._shell.days():
            for line in day.commitments(Line):
                for person in self._personnel:
                    if (person._assigned_org != None and person._assigned_org != line.flight_org):
                        lines_with_misassigned.append(self._commit_vars[(day.date, line.id(), person.id())])

        # TODO: move this to a function
        num_total_lines = len([l for d in self._shell.days() for l in d.commitments(Line)])

        # optimize for AUSM tiers
        ausm_epsilon = self._model.NewIntVar(0, 10, "ausm_eps")
        for person in self._personnel:
            scheduled_commitments = []
            for day in self._shell.days():
                commitments = day.commitments()
                for c in commitments:
                    scheduled_commitments.append(self._commit_vars[(day.date, c.id(), person.id())])

            commitment_requirement = get_commitments_for_ausm_tier(person._ausm_tier)
            self._model.Add(sum(scheduled_commitments)  <= commitment_requirement + ausm_epsilon)
            self._model.Add(sum(scheduled_commitments)  >= commitment_requirement - ausm_epsilon)

        # optimize for duties
        quals = [DutyQual.OPS_SUP, DutyQual.SOF, [DutyQual.CONTROLLER, DutyQual.OBSERVER]]
        duty_epsilons = 0
        for qual in quals:
            duty_epsilons += self._add_duty_objective(qual)

        # TODO: absolutely need to normalize this!
        self._model.Minimize((num_total_lines - sum(lines_filled)) + sum(lines_with_misassigned) + ausm_epsilon + 100*duty_epsilons)

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
        self._solver = cp_model.CpSolver()

    def solve(self):

        status = self._solver.Solve(self._model._handle())

        if status != cp_model.OPTIMAL:
            return (status, {})

        return (status, self._get_solution())


    def _get_solution(self):
        solution = {}

        for day in self._shell.days():
            for d in day.commitments(Duty):
                solution[d.id()] = None

                for person in self._personnel:
                    if self._solver.Value(self._model._variable((day.date, d.id(), person.id()))):
                        solution[d.id()] = person

            for l in day.commitments(Line):
                solution[l.id()] = None

                for person in self._personnel:
                    if self._solver.Value(self._model._variable((day.date, l.id(), person.id()))):
                        solution[l.id()] = person

        return solution
