import pytest
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from scheduler import ScheduleModel, ScheduleSolver, Person, Duty, DutyType

def test_given_single_duty_and_single_person_when_solved_then_duty_is_filled():
    duties = [Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    personnel = [Person(1, "LastName", "FirstName")]

    model = ScheduleModel(duties, personnel)
    solver = ScheduleSolver(model)

    solution = solver.solve()

    assert solution == {duties[0].name: personnel[0].prsn_id}
