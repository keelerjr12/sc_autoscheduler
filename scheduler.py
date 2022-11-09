from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Flag, auto
from ortools.sat.python import cp_model

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

class ScheduleModel:
    duties = []
    personnel = []
    
    def __init__(self, duties, personnel):
        self.duties = duties
        self.personnel = personnel

class ScheduleSolver:
    _duty_schedule_vars = {}
    _sched_model: ScheduleModel
    
    def __init__(self, sched_model: ScheduleModel):
        self._sched_model = sched_model

    def solve(self) -> bool:
        model = cp_model.CpModel()

        self._add_variables(model)
        self._add_constraints(model)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status != cp_model.OPTIMAL:
            raise Exception("Suboptimal solution")
            
        return self._get_solution(solver)


    def _add_variables(self, model: cp_model.CpModel):
        # create all duty variables
        for duty in self._sched_model.duties:
            for person in self._sched_model.personnel:
                self._duty_schedule_vars[(duty.name, person.prsn_id)] = model.NewBoolVar('duty_s%s%i' % (duty.name, person.prsn_id))    

    def _add_constraints(self, model: cp_model.CpModel):
        # all duties filled with respective qual'd personnel
        for duty in self._sched_model.duties:
            model.AddExactlyOne(self._duty_schedule_vars[(duty.name, p.prsn_id)] for p in self._sched_model.personnel)

    def _get_solution(self, solver: cp_model.CpSolver):
        solution = {}

        for d in self._sched_model.duties:
            for p in self._sched_model.personnel:
                if solver.Value(self._duty_schedule_vars[(d.name, p.prsn_id)]):
                    solution[d.name] = p.prsn_id

        return solution
