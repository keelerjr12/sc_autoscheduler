import csv
import configparser
from datetime import datetime, timedelta
from enum import IntEnum
from repository import DatabaseRepository
from printers import get_printer

from scheduler.models import AbsenceRequest, Duty, Line, Person 
from scheduler.solver import ScheduleModel, ScheduleSolver, ShellSchedule

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

def str_to_duty_type(str_type: str) -> str:
    lc_str_type = str_type.lower()

    if lc_str_type.find('controller') != -1:
        return 'RSU Controller'
    elif lc_str_type.find('observer') != -1:
        return 'RSU Observer'
    elif lc_str_type.find('recorder') != -1:
        return 'RSU Recorder'
    elif lc_str_type.find('spotter') != -1:
        return 'RSU Spotter'
    elif lc_str_type.find('loner') != -1:
        return 'RSU Loner'
    elif lc_str_type.find('sof') != -1:
        return 'SOF'
    else:
        return 'Operations Supervisor'

def parse_duties(str: str):
    return Duty(str[3], str_to_duty_type(str[3]), datetime.strptime(str[6], '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(str[7], '%m/%d/%Y %I:%M:%S %p'))

def parse_shell_lines(str: str):
    flight_designator = str[2].split(sep=' - ')[1][0]
    org = flight_designator
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
        p.assign_to(assigned_flight.upper())
    
    if is_qualified(str, LOX_COL.CONTROLLER) == True:
        p.qual('Duty', 'RSU Controller')

    if is_qualified(str, LOX_COL.OBSERVER) == True:
        p.qual('Duty', 'RSU Observer')

    if is_qualified(str, LOX_COL.OPS_SUP) == True:
        p.qual('Duty', 'Operations Supervisor')

    if is_qualified(str, LOX_COL.SOF) == True:
        p.qual('Duty', 'SOF')

    if is_qualified(str, LOX_COL.PIT_IP) == True:
        p.qual_for_flight('PIT IP')

    return p

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


#TODO: needs refactoring!    
def parse_absence_requests(str: str):
    prsn_id = int(str[2])
    start_dt = datetime.strptime(str[8], '%m/%d/%Y %I:%M:%S %p')
    end_dt = datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p')
    recur_end_dt = datetime.strptime(str[11], '%m/%d/%Y %I:%M:%S %p')
    weekday_ptn = str[12]

    # TODO: moving this to database as well -- encapsulate
    if (weekday_ptn == ""):
        return AbsenceRequest(prsn_id, start_dt, end_dt)

    weekday_bit_ptn = int(weekday_ptn)

    init_dt = True
    ars = []
    for single_dt in daterange(start_dt, recur_end_dt):

        if (init_dt == True):
            ars.append(AbsenceRequest(prsn_id, single_dt, end_dt))
            init_dt = False
        elif ((1 << single_dt.isoweekday()) & weekday_bit_ptn):
            new_end_dt = end_dt + timedelta(days = (single_dt - start_dt).days)
            ars.append(AbsenceRequest(prsn_id, single_dt, new_end_dt))

    return ars

def run():
    print("Entering Run")
    PRINTER_TYPE = 'Console'

    config = configparser.ConfigParser()
    config.read("autoscheduler/config.ini")

    #duties: list[Duty] = parse_csv(config["FILES"]["duty-schedule"], parse_duties)
    #lines: list[Line] = parse_csv(config["FILES"]["flying-schedule"], parse_shell_lines)
    #personnel: list[Person] = parse_csv(config["FILES"]["lox"], parse_personnel)
    #absences: list[AbsenceRequest] = parse_csv(config["FILES"]["absence-requests"], parse_absence_requests)
    
    repo = DatabaseRepository()
    personnel = repo.get_personnel()
    lines = repo.get_lines()
    duties = repo.get_duties()
    absences = repo.get_absences()
   
    shell = ShellSchedule(lines, duties)
    model = ScheduleModel(shell, personnel, absences)
    model.add_all_contraints()

    solver = ScheduleSolver(model, personnel, shell)
    solution = solver.solve()

    printer = get_printer(PRINTER_TYPE, config, solution)
    printer.print()

    print("Exiting Run")

if __name__ == "__main__":
    run()
