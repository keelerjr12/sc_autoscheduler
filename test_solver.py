import pytest
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from scheduler import ScheduleModel, ScheduleSolver, Person, Line, Duty, DutyType

def test_given_max_num_duties_single_qualified_person_when_solved_then_optimal_solution():
    lines = []
    duty1 = Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 9, 0), datetime(2022, 7, 29, 10, 0))   
    duty2 = Duty("Tinder 2 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 10, 0), datetime(2022, 7, 29, 11, 0))   
    duty3 = Duty("Tinder 3 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 11, 0), datetime(2022, 7, 29, 12, 0))   
    duties = [duty1, duty2, duty3]

    controller = Person(1, "LastName", "FirstName")
    controller.qual(DutyType.CONTROLLER)
    personnel = [controller]

    model = ScheduleModel(lines, duties, personnel)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0].prsn_id, duties[1].name: personnel[0].prsn_id, duties[2].name: personnel[0].prsn_id}

def test_given_greater_than_max_num_duties_single_qualified_person_when_solved_then_infeasible_solution():
    lines = []
    duty1 = Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 9, 0), datetime(2022, 7, 29, 10, 0))   
    duty2 = Duty("Tinder 2 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 10, 0), datetime(2022, 7, 29, 11, 0))   
    duty3 = Duty("Tinder 3 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 11, 0), datetime(2022, 7, 29, 12, 0))   
    duty4 = Duty("Tinder 4 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 12, 0), datetime(2022, 7, 29, 13, 0))   
    duties = [duty1, duty2, duty3, duty4]

    controller = Person(1, "LastName", "FirstName")
    controller.qual(DutyType.CONTROLLER)
    personnel = [controller]

    model = ScheduleModel(lines, duties, personnel)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.INFEASIBLE
    assert solution == {} 


def test_given_single_duty_and_single_qualified_person_when_solved_then_duty_is_filled():
    lines = []
    duties = [Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]

    controller = Person(1, "LastName", "FirstName")
    controller.qual(DutyType.CONTROLLER)
    personnel = [controller]

    model = ScheduleModel(lines, duties, personnel)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0].prsn_id}

def test_given_single_duty_and_single_unqualified_person_when_solved_then_duty_is_unfilled():
    lines = []
    duties = [Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    personnel = [Person(1, "LastName", "FirstName")]

    model = ScheduleModel(lines, duties, personnel)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.INFEASIBLE
    assert solution == {}

def test_given_single_line_and_single_person_when_solved_then_line_is_filled():
    lines = [Line(1, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    person = Person(1, "LastName", "FirstName")
    personnel = [person]

    model = ScheduleModel(lines, duties, personnel)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {lines[0].number: personnel[0].prsn_id}
