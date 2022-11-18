import pytest
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from main import parse_absence_requests
from scheduler import ScheduleSolver, Person, FlightOrg, Line, Duty, DutyQual, has_turn_time

def test_single_recurring_absence_request_when_parsed_returns_all_times_unavailable():
    ar_str = ["1160170043","1160044308","1160005566","Hatfield","Bennett","Absent","Meeting","OG Meeting","2/2/2021 10:30:00 AM","2/2/2021 12:00:00 PM","2/2/2021 10:30:00 AM","4/5/2023 12:00:00 PM","8"]
    
    ars = parse_absence_requests(ar_str);
    print([(ar.start_dt(), ar.end_dt()) for ar in ars])

    assert False

def test_given_max_num_duties_single_qualified_person_when_solved_then_optimal_solution():
    lines = []
    duty1 = Duty("Tinder 1 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 9, 0), datetime(2022, 7, 29, 10, 0))   
    duty2 = Duty("Tinder 2 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 10, 0), datetime(2022, 7, 29, 11, 0))   
    duty3 = Duty("Tinder 3 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 11, 0), datetime(2022, 7, 29, 12, 0))   
    duties = [duty1, duty2, duty3]
    absences = []

    controller = Person(1, "LastName", "FirstName", 4)
    controller.qual_for_duty(DutyQual.CONTROLLER)
    personnel = [controller]

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0], duties[1].name: personnel[0], duties[2].name: personnel[0]}

def test_given_greater_than_max_num_duties_single_qualified_person_when_solved_then_infeasible_solution():
    lines = []
    duty1 = Duty("Tinder 1 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 9, 0), datetime(2022, 7, 29, 10, 0))   
    duty2 = Duty("Tinder 2 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 10, 0), datetime(2022, 7, 29, 11, 0))   
    duty3 = Duty("Tinder 3 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 11, 0), datetime(2022, 7, 29, 12, 0))   
    duty4 = Duty("Tinder 4 Controller", DutyQual.CONTROLLER, datetime(2022, 7, 29, 12, 0), datetime(2022, 7, 29, 13, 0))   
    duties = [duty1, duty2, duty3, duty4]
    absences = []

    controller = Person(1, "LastName", "FirstName", 4)
    controller.qual_for_duty(DutyQual.CONTROLLER)
    personnel = [controller]

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.INFEASIBLE
    assert solution == {} 


def test_given_single_duty_and_single_qualified_person_when_solved_then_duty_is_filled():
    lines = []
    duties = [Duty("Tinder 1 Controller", DutyQual.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]

    controller = Person(1, "LastName", "FirstName", 4)
    controller.qual_for_duty(DutyQual.CONTROLLER)
    personnel = [controller]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {duties[0].name: personnel[0]}

def test_given_single_duty_and_single_unqualified_person_when_solved_then_duty_is_unfilled():
    lines = []
    duties = [Duty("Tinder 1 Controller", DutyQual.CONTROLLER, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'), datetime.strptime('7/29/2022 10:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    personnel = [Person(1, "LastName", "FirstName", 4)]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.INFEASIBLE
    assert solution == {}

def test_given_single_line_and_single_person_when_solved_then_line_is_filled():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    person = Person(1, "LastName", "FirstName", 4)
    personnel = [person]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {lines[0].number: personnel[0]}

def test_given_single_pilot_with_turn_time_when_solved_then_optimal_solution():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2,FlightOrg.M, datetime.strptime('7/29/2022 11:30:00 AM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    person = Person(1, "LastName", "FirstName", 4)
    personnel = [person]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert solution == {lines[0].number: personnel[0], lines[1].number: personnel[0]}

def test_given_multiple_pilots_with_turn_time_when_solved_then_optimal_solution():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, FlightOrg.O, datetime.strptime('7/29/2022 8:30:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(3, FlightOrg.P, datetime.strptime('7/29/2022 11:30:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(4, FlightOrg.P, datetime.strptime('7/29/2022 12:00:00 PM', '%m/%d/%Y %I:%M:%S %p'))]
    duties = []
    personnel = [Person(1, "LastName", "FirstName", 3), Person(2, "LastName", "FirstName", 4)]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert ((solution == {lines[0].number: personnel[0], lines[1].number: personnel[1], lines[2].number: personnel[0], lines[3].number: personnel[1]}) or (solution == {lines[0].number: personnel[1], lines[1].number: personnel[0], lines[2].number: personnel[1], lines[3].number: personnel[0]}))

def test_given_single_pilot_without_turn_time_when_solved_then_optimal_solution_with_empty_line():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, FlightOrg.O, datetime.strptime('7/29/2022 11:29:59 AM', '%m/%d/%Y %I:%M:%S %p'))] 
    duties = []
    personnel = [Person(1, "LastName", "FirstName", 4)]
    absences = []

    solver = ScheduleSolver(personnel, lines, duties, absences)
    (status, solution) = solver.solve()

    assert status == cp_model.OPTIMAL
    assert ((solution == {lines[0].number: None, lines[1].number: personnel[0]}) or (solution == {lines[0].number: personnel[0], lines[1].number: None}))

def test_given_commitments_with_time_delta_exceeded_when_run_returns_true():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, FlightOrg.O, datetime.strptime('7/29/2022 12:14:00 AM', '%m/%d/%Y %I:%M:%S %p'))]

    is_exceeded = has_turn_time(lines[0], lines[1], timedelta(hours = 4, minutes = 15))

    assert is_exceeded == True

def test_given_commitments_with_time_delta_not_exceeded_when_run_returns_false():
    lines = [Line(1, FlightOrg.M, datetime.strptime('7/29/2022 8:00:00 AM', '%m/%d/%Y %I:%M:%S %p')), Line(2, FlightOrg.N, datetime.strptime('7/29/2022 12:15:00 PM', '%m/%d/%Y %I:%M:%S %p'))]

    is_exceeded = has_turn_time(lines[0], lines[1], timedelta(hours = 4, minutes = 15))

    assert is_exceeded == False

