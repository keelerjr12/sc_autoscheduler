import csv
import configparser
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import IntEnum
from ortools.sat.python import cp_model
import xlsxwriter
import os

from scheduler.models import AbsenceRequest, Duty, DutyQual, FlightOrg, FlightQual, Line, Person
from scheduler.solver import ScheduleModel, ScheduleSolution, ScheduleSolver, ShellSchedule, time_between

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
    return Duty(str[3], str_to_duty_type(str[3]), datetime.strptime(str[6], '%m/%d/%Y %I:%M:%S %p'), datetime.strptime(str[7], '%m/%d/%Y %I:%M:%S %p'))

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


#TODO: needs refactoring!    
def parse_absence_requests(str: str):
    prsn_id = int(str[2])
    start_dt = datetime.strptime(str[8], '%m/%d/%Y %I:%M:%S %p')
    end_dt = datetime.strptime(str[9], '%m/%d/%Y %I:%M:%S %p')
    recur_end_dt = datetime.strptime(str[11], '%m/%d/%Y %I:%M:%S %p')
    weekday_ptn = str[12]

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

def compute_sorties_for_schedule(solution: ScheduleSolution, person: Person) -> int:
    ct = 0
    for day in solution._schedule.days():
        for commit in day.commitments():
            p = commit.assigned_to()
            if (p != None and p.id() == person.id()):
                ct += 1 
    return ct

def compute_duties_for_schedule(solution: ScheduleSolution, person: Person) -> int:
    ct = 0
    for day in solution._schedule.days():
        for commit in day.commitments(Duty):
            p = commit.assigned_to()
            if (p != None and p.id() == person.id()):
                ct += 1 
    return ct

def compute_max_turn_time_for(solution: ScheduleSolution, person: Person) -> timedelta:
    max_turn = timedelta()

    for day in solution._schedule.days():
        prev_commit = None
        for commit in day.commitments():
            if commit.assigned_to() == person:
                if prev_commit != None:
                    turn_time = time_between(prev_commit, commit)

                    if turn_time > max_turn:
                        max_turn = turn_time

                prev_commit = commit

    return max_turn

class SolutionPrinter(ABC):
    def __init__(self, solution, shell, personnel):
        self._solution = solution
        self._shell = shell
        self._personnel = personnel

    @abstractmethod
    def print(self):
        pass

class ConsoleSolutionPrinter(SolutionPrinter):

    def __init__(self, solution, shell) -> None:
        return super().__init__(solution, shell)

    def print(self):
        if (self._status != cp_model.OPTIMAL):
            print("Solution is infeasible")
            return
            
        for day in self._shell.days():
            for duty in day.commitments(Duty):
                person = self._solution[duty.id()]
                print(duty.name + ': ', end='')

                if self._solution[duty.id()] != None:
                    print("%s, %s" % (person._last_name, person._first_name), end='')
                
                print()

            for line in day.commitments(Line):
                person = self._solution[line.id()]

                print('[%i][%s] brief: %s, takeoff: %s, debrief end: %s -- ' % (line.number, line.flight_org, line.time_brief.strftime('%H%M'), line.time_takeoff.strftime('%H%M'), line.time_debrief_end.strftime('%H%M')), end='')

                if self._solution[line.id()] != None:
                    print("%s, %s" % (person._last_name, person._first_name), end='')
                    
                print()

class HtmlSolutionPrinter(SolutionPrinter):
    def __init__(self, solution, shell, personnel) -> None:
        return super().__init__(solution, shell, personnel)

    def print(self):
        self._print_schedule('index.html')
        self._print_allocation('allocation.html')

    def _print_header(self, out_file):
        print("<html>", file=out_file)
        print("  <body>", file=out_file)

    def _print_footer(self, out_file):
        print("  </body>", file=out_file)
        print("</html>", file=out_file)

    def _print_menu(self, out_file):
        print('    <ul>', file=out_file)
        print('      <li><a href="index.html">Schedule</a></li>', file=out_file)
        print('      <li><a href="allocation.html">Allocation</a></li>', file=out_file)
        print('    </ul>', file=out_file)

    def _print_schedule(self, filename: str):
        with open(filename, 'w') as out_file:
            self._print_header(out_file)
            self._print_menu(out_file)

            if (self._solution._status != cp_model.OPTIMAL):
                print("Solution is infeasible", file=out_file)
            else:
                for day in self._solution._schedule.days():
                    print(f"    <h3>{day.date().strftime('%a, %-m/%-d/%Y')}</h3>", file=out_file)
                    print("    <table>", file=out_file)
                    print("      <th>Line</th>", file=out_file)
                    print("      <th>Organization</th>", file=out_file)
                    print("      <th>Takeoff Time(L)</th>", file=out_file)
                    for line in day.commitments(Line):
                        print("      <tr>", file=out_file)
                        print(f'        <td>{line.number}</td>', file=out_file)
                        print(f'        <td>{line.flight_org}</td>', file=out_file)
                        print(f'        <td>{line.time_takeoff.strftime("%H%M")}</td>', file=out_file)

                        person = line.assigned_to()
                        if person != None:
                            print("        <td>%s, %s</td>" % (person._last_name, person._first_name), file=out_file)
                        print("      </tr>", file=out_file)
                    
                    for duty in day.commitments(Duty):
                        print("      <tr>", file=out_file)
                        print("        <td>", duty.name + ': ', "</td>", file=out_file)

                        person = duty.assigned_to()
                        if person != None:
                            print("        <td>%s, %s</td>" % (person._last_name, person._first_name), file=out_file)
                        
                        print("      </tr>", file=out_file)
                    print("    </table>", file=out_file)

            self._print_footer(out_file)

    def _print_allocation(self, filename):
        with open(filename, 'w') as out_file:
            self._print_header(out_file)
            self._print_menu(out_file)

            print('    <table>', file=out_file)
            print('      <th>Name</th>', file=out_file)
            print('      <th># of Events</th>', file=out_file)
            print('      <th># of Duties</th>', file=out_file)
            print('      <th>Max Turn Time</th>', file=out_file)
            for person in self._personnel:
                print('      <tr>', file=out_file)
                print(f'        <td>{person._last_name}, {person._first_name}</td>', file=out_file)

                sorties_scheduled = compute_sorties_for_schedule(self._solution, person)
                print(f'        <td>{sorties_scheduled}</td>', file=out_file)

                duties_scheduled = compute_duties_for_schedule(self._solution, person)
                print(f'        <td>{duties_scheduled}</td>', file=out_file)

                max_turn_time = compute_max_turn_time_for(self._solution, person)
                print(f'        <td>{max_turn_time}</td>', file=out_file)

                print('      </tr>', file=out_file)
            print('    </table>', file=out_file)
            self._print_footer(out_file)

class ExcelSolutionPrinter():
    def __init__(self, solution: ScheduleSolution, shell: ShellSchedule, personnel: list[Person]):
        self._solution = solution
        self._shell = shell
        self._personnel = personnel

    def print(self, filename:str):
        with xlsxwriter.Workbook(filename) as workbook:
            for day in self._solution._schedule.days():
                worksheet = workbook.add_worksheet(day.date().strftime('%Y%m%d'))
                
                row = 0
                col = 0

                for line in day.commitments(Line):
                    worksheet.write(row, col, line.number)
                    worksheet.write(row, col + 1, line.flight_org.name)
                    worksheet.write(row, col + 2, line.time_takeoff.strftime("%H%M"))
                    
                    person = line.assigned_to()
                    if person != None:
                        worksheet.write(row, col + 3, line._person._last_name + ', ' + line._person._first_name)
                    
                    row = row + 1


def run():
    print("Entering Run")

    config = configparser.ConfigParser()
    config.read("autoscheduler/config.ini")

    duties: list[Duty] = parse_csv(config["FILES"]["duty-schedule"], parse_duties)
    lines: list[Line] = parse_csv(config["FILES"]["flying-schedule"], parse_shell_lines)
    personnel: list[Person] = parse_csv(config["FILES"]["lox"], parse_personnel)
    absences: list[AbsenceRequest] = parse_csv(config["FILES"]["absence-requests"], parse_absence_requests)

    shell = ShellSchedule(lines, duties)
    model = ScheduleModel(shell, personnel, absences)
    model.add_all_contraints()

    solver = ScheduleSolver(model, personnel, shell)
    solution = solver.solve()

    printer = ExcelSolutionPrinter(solution, shell, personnel)
    dir = config['FILES']['output_dir']
    date = solution._schedule.days()[0].date().strftime('%Y%m%d')
    filename = '469_fts_' + date + '.xlsx'
    printer.print(os.path.join(dir, filename))

    print("Exiting Run")

if __name__ == "__main__":
    run()
