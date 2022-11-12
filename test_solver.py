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
    absences = []

    controller = Person(1, "LastName", "FirstName")
    controller.qual(DutyType.CONTROLLER)
    personnel = [controller]

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0], duties[1].name: personnel[0], duties[2].name: personnel[0]}

def test_given_greater_than_max_num_duties_single_qualified_person_when_solved_then_infeasible_solution():
    lines = []
    duty1 = Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 9, 0), datetime(2022, 7, 29, 10, 0))   
    duty2 = Duty("Tinder 2 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 10, 0), datetime(2022, 7, 29, 11, 0))   
    duty3 = Duty("Tinder 3 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 11, 0), datetime(2022, 7, 29, 12, 0))   
    duty4 = Duty("Tinder 4 Controller", DutyType.CONTROLLER, datetime(2022, 7, 29, 12, 0), datetime(2022, 7, 29, 13, 0))   
    duties = [duty1, duty2, duty3, duty4]
    absences = []

    controller = Person(1, "LastName", "FirstName")
    controller.qual(DutyType.CONTROLLER)
    personnel = [controller]

    model = ScheduleModel(lines, duties, personnel, absences)
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
    absences = []

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0]}

def test_given_single_duty_and_single_unqualified_person_when_solved_then_duty_is_unfilled():
    lines = []
    duties = [Duty("Tinder 1 Controller", DutyType.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    personnel = [Person(1, "LastName", "FirstName")]
    absences = []

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.INFEASIBLE
    assert solution == {}

def test_given_single_line_and_single_person_when_solved_then_line_is_filled():
    lines = [Line(1, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    person = Person(1, "LastName", "FirstName")
    personnel = [person]
    absences = []

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {lines[0].number: personnel[0]}

def test_given_single_pilot_with_turn_time_when_solved_then_optimal_solution():
    lines = [Line(1, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, datetime.strptime('7/29/2022 11:30:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    person = Person(1, "LastName", "FirstName")
    personnel = [person]
    absences = []

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {lines[0].number: personnel[0], lines[1].number: personnel[0]}

def test_given_multiple_pilots_with_turn_time_when_solved_then_optimal_solution():
    lines = [Line(1, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, datetime.strptime('7/29/2022 8:30:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(3, datetime.strptime('7/29/2022 11:30:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(4, datetime.strptime('7/29/2022 12:00:00 PM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    personnel = [Person(1, "LastName", "FirstName"), Person(2, "LastName", "FirstName")]
    absences = []

    model = ScheduleModel(lines, duties, personnel, absences)
    solver = ScheduleSolver(model)

    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    for key, val in solution.items():
        print(key)
        print(val.prsn_id)
    assert ((solution == {lines[0].number: personnel[0], lines[1].number: personnel[1], lines[2].number: personnel[0], lines[3].number: personnel[1]}) or (solution == {lines[0].number: personnel[1], lines[1].number: personnel[0], lines[2].number: personnel[1], lines[3].number: personnel[0]}))
