import csv
from datetime import datetime, timedelta
from enum import IntEnum, Flag, auto
from typing import NamedTuple
from abc import ABC, abstractmethod
from ortools.sat.python import cp_model

from scheduler import ShellSchedule, ScheduleSolver, Duty, DutyQual, FlightOrg, FlightQual, Line, Person, AbsenceRequest

def parse_csv(file: str, parse_fn):
    all_objs = []

    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)

        for row in reader:
            obj = parse_fn(row)

            # need to flatten a list if it's returned from the parsing function
            if type(obj) is list:
                all_objs = all_objs + obj
            else:
                all_objs.append(obj)

    return all_objs

def str_to_duty_type(str_type: str) -> DutyQual:
    lc_str_type = str_type.lower()

    if lc_str_type.find('controller') != -1:
        return DutyQual.CONTROLLER
    elif lc_str_type.find('observer') != -1:
        return DutyQual.OBSERVER
    elif lc_str_type.find('recorder') != -1:
        return DutyQual.RECORDER
    elif lc_str_type.find('spotter') != -1:
        return DutyQual.SPOTTER
    elif lc_str_type.find('loner') != -1:
        return DutyQual.LONER
    elif lc_str_type.find('sof') != -1:
        return DutyQual.SOF
    else:
        return DutyQual.OPS_SUP

def parse_duties(str: str):
    return Duty(str[3], str_to_duty_type(str[3]), datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(str[10], '%m/%d/%Y %I:%M:%S %p'))

def parse_shell_lines(str: str):
    flight_designator_str = str[2].split(sep=' - ')[1][0]
    org = FlightOrg[flight_designator_str]
    return Line(int(str[0]), org, datetime.strptime(str[1], '%m/%d/%Y %I:%M:%S %p'))

class LOX_COL(IntEnum):
    LAST_NAME = 0
    FIRST_NAME = 1
    PRSN_ID = 2
    OBSERVER = 11
    CONTROLLER = 12
    SOF = 13
    OPS_SUP = 14
    PIT_IP = 19
    AUSM_TIER = 29
    ASSIGNED_FLIGHT = 30

def is_qualified(qual_row, qual: LOX_COL) -> bool:
    LOX_val = qual_row[qual]
    return (LOX_val.find('X') != -1) or (LOX_val.find('D') != -1)

def parse_personnel(str: str):
    last_name = str[LOX_COL.LAST_NAME]
    first_name = str[LOX_COL.FIRST_NAME]
    prsn_id = int(str[LOX_COL.PRSN_ID])
    assigned_flight = str[LOX_COL.ASSIGNED_FLIGHT]
    ausm_tier = int(str[LOX_COL.AUSM_TIER])

    p = Person(prsn_id, last_name, first_name, ausm_tier)

    if (assigned_flight != ""):
        p.assign_to(FlightOrg[assigned_flight.upper()])
    
    if is_qualified(str, LOX_COL.CONTROLLER) == True:
        p.qual_for_duty(DutyQual.CONTROLLER)

    if is_qualified(str, LOX_COL.OBSERVER) == True:
        p.qual_for_duty(DutyQual.OBSERVER)

    if is_qualified(str, LOX_COL.OPS_SUP) == True:
        p.qual_for_duty(DutyQual.OPS_SUP)

    if is_qualified(str, LOX_COL.SOF) == True:
        p.qual_for_duty(DutyQual.SOF)

    if is_qualified(str, LOX_COL.PIT_IP) == True:
        p.qual_for_flight(FlightQual.PIT)

    return p

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)
    
def parse_absence_requests(str: str):
    prsn_id = int(str[2])
    start_dt = datetime.strptime(str[8], '%m/%d/%Y %I:%M:%S %p')
    end_dt = datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p')
    recur_end_dt = datetime.strptime(str[11], '%m/%d/%Y %I:%M:%S %p')
    weekday_ptn = str[12]

    if (weekday_ptn == ""):
        return AbsenceRequest(prsn_id, start_dt, end_dt)

    weekday_bit_ptn = int(weekday_ptn)

    ars = []
    for single_date in daterange(start_dt, recur_end_dt):
            if ((1 << single_date.isoweekday()) & weekday_bit_ptn):
                ars.append(AbsenceRequest(prsn_id, single_date, end_dt));
    return ars

def print_solution(solution, duties, lines):
    for duty in duties:
        person = solution[duty.name]
        print(duty.name + ': ', end='')

        if solution[duty.name] != None:
            print ("%s, %s" % (person._last_name, person._first_name), end='')
            
        print()

    for line in lines:
        person = solution[line.number]

        print('[%i][%s] brief: %s, takeoff: %s, debrief end: %s -- ' % (line.number, line.flight_org, line.time_brief.strftime('%H%M'), line.time_takeoff.strftime('%H%M'), line.time_debrief_end.strftime('%H%M')), end='')

        if solution[line.number] != None:
            print ("%s, %s" % (person._last_name, person._first_name), end='')
            
        print()
def run():
    print("Entering Run")

    RES_DIR = 'res/'

    duty_schedule_file = RES_DIR + 'duty_schedule.csv'
    flying_schedule_file = RES_DIR + 'flying_schedule.csv'
    lox_file = RES_DIR + 'lox.csv'
    absence_request_file = RES_DIR + 'absence_requests.csv'

    duties: list[Duty] = parse_csv(duty_schedule_file, parse_duties)
    lines: list[Line] = parse_csv(flying_schedule_file, parse_shell_lines)
    personnel: list[Person] = parse_csv(lox_file, parse_personnel)
    absences: list[AbsenceRequest] = parse_csv(absence_request_file, parse_absence_requests)

    shell = ShellSchedule(lines, duties)

    solver = ScheduleSolver(personnel, shell, absences)
    (status, solution) = solver.solve()

    if (status == cp_model.OPTIMAL):
        print_solution(solution, duties, lines)
    else:
        print("Solution is infeasible")

    print("Exiting Run")

if __name__ == "__main__":
    run()
