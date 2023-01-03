
from abc import ABC, abstractmethod
from scheduler.models import Duty, Line, Person
from scheduler.solver import ScheduleSolution, time_between
import xlsxwriter
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

class SolutionPrinter(ABC):
    @abstractmethod
    def print(self):
        pass

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

class ConsoleSolutionPrinter(SolutionPrinter):

    def __init__(self, solution: ScheduleSolution) -> None:
        self._solution = solution

    def print(self):
        if (self._solution._status != cp_model.OPTIMAL):
            print("Solution is infeasible")
            return
            
        for day in self._solution._schedule.days():
            for duty in day.commitments(Duty):
                print(duty.name + ': ', end='')

                person = duty.assigned_to()
                if person != None:
                    print("%s, %s" % (person._last_name, person._first_name), end='')
                
                print()

            for line in day.commitments(Line):
                print('[%i][%s] brief: %s, takeoff: %s, debrief end: %s -- ' % (line.number, line.flight_org, line.time_brief.strftime('%H%M'), line.time_takeoff.strftime('%H%M'), line.time_debrief_end.strftime('%H%M')), end='')

                person = line.assigned_to() 
                if person != None:
                    print("%s, %s" % (person._last_name, person._first_name), end='')
                    
                print()

class HtmlSolutionPrinter(SolutionPrinter):
    def __init__(self, solution, dir) -> None:
        self._solution = solution
        self._dir = dir

    def print(self):
        self._print_schedule(os.path.join(self._dir, 'index.html'))
        self._print_allocation(os.path.join(self._dir, 'allocation.html'))

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
    def __init__(self, solution: ScheduleSolution, dir: str):
        self._solution = solution
        self._dir = dir

    def print(self):
        solution_date = self._solution._schedule.days()[0].date().strftime('%Y%m%d')
        created_date = datetime.today().strftime('%Y%m%d')
        filename = f'469_fts_%s_%s_.xlsx' % (solution_date, created_date)
        filepath = os.path.join(self._dir, filename)

        with xlsxwriter.Workbook(filepath) as workbook:
            for day in self._solution._schedule.days():
                worksheet = workbook.add_worksheet(day.date().strftime('%Y%m%d'))
                
                row = 0
                col = 0

                for line in day.commitments(Line):
                    worksheet.write(row, col, line.number)
                    worksheet.write(row, col + 1, line.flight_org)
                    worksheet.write(row, col + 2, line.time_takeoff.strftime("%H%M"))
                    
                    person = line.assigned_to()
                    if person != None:
                        worksheet.write(row, col + 3, line._person._last_name + ', ' + line._person._first_name)
                    
                    row = row + 1
