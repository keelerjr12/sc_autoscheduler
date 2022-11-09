import pytest
from ortools.sat.python import cp_model
from scheduler import ScheduleModel, ScheduleSolver

def test_lines_filled():
    duties = []
    personnel = []

    model = ScheduleModel(duties, personnel)
    solver = ScheduleSolver(model)

    status = solver.solve()

    assert status == cp_model.OPTIMAL
