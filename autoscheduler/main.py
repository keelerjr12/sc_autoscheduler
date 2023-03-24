import configparser
from repository import AutoschedulerRepository, CSVRepository, DatabaseRepository 
from scheduler.solver import ScheduleModel, ScheduleSolution, ScheduleSolver, ShellSchedule
from printers import ConsoleSolutionPrinter, DatabaseSolutionPrinter, ExcelSolutionPrinter, HtmlSolutionPrinter, SolutionPrinter

from ortools.sat.python import cp_model

def get_repo(repo_type: str, config: configparser.ConfigParser) -> AutoschedulerRepository:
    if (repo_type.lower() == 'database'):
        return DatabaseRepository()
    else:
        return CSVRepository(config['FILES'])

def get_printer(printer_type: str, config: configparser.ConfigParser, solution: ScheduleSolution) -> SolutionPrinter:
    if (printer_type.lower() == 'html'):
        dir = config['FILES']['output_dir']
        return HtmlSolutionPrinter(solution, dir)
    elif (printer_type.lower() == 'excel'):
        dir = config['FILES']['output_dir']
        return ExcelSolutionPrinter(solution, dir)
    elif (printer_type.lower() == 'database'):
        print('hey')
        db_repo = DatabaseRepository()
        return DatabaseSolutionPrinter(solution, db_repo)
    
    return ConsoleSolutionPrinter(solution)

def run():
    print("Entering Run")

    REPO_TYPE = 'Database'
    PRINTER_TYPE = 'Database'

    config = configparser.ConfigParser()
    config.read("autoscheduler/config.ini")

    repo = get_repo(REPO_TYPE, config)

    personnel = repo.get_personnel()
    lines = repo.get_lines()
    duties = repo.get_duties()
    absences = repo.get_absences()
   
    shell = ShellSchedule(lines, duties)
    model = ScheduleModel(shell, personnel, absences)
    model.add_all_contraints()

    solver = ScheduleSolver(model, personnel, shell)
    #solution = solver.solve()
    solution = ScheduleSolution(cp_model.OPTIMAL, ShellSchedule([], [])) # TODO: make sure to remove this after testing!

    printer = get_printer(PRINTER_TYPE, config, solution)
    printer.print()

    print("Exiting Run")

if __name__ == "__main__":
    run()
