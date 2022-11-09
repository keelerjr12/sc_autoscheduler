from ortools.sat.python import cp_model

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

        solver = cp_model.CpSolver()

        return solver.Solve(model)

    def _add_variables(self, model: cp_model.CpModel):

        # create all duty variables
        for duty in self._sched_model.duties:
            for person in self._sched_model.personnel:
                _duty_schedule_vars[(duty.name, person.prsn_id)] = model.NewBoolVar('duty_s%s%i' % (duty.name, person.prsn_id))    
