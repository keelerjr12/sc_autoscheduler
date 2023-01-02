from abc import  ABC, abstractmethod
from datetime import timedelta
from sqlalchemy import select

from data import Session
from models import AbsenceRequestDto, Pilot, ShellDuty, ShellLine
from scheduler.models import AbsenceRequest, Duty, Line, Person, Qualification

class AutoschedulerRepository(ABC):

    @abstractmethod
    def get_personnel(self) -> list[Person]:
        pass

    def get_duties(self) -> list[Duty]:
        pass

    def get_lines(self) -> list[Line]:
        pass

    def get_absences(self) -> list[AbsenceRequest]:
        pass


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)


class DatabaseRepository(AutoschedulerRepository):

    def get_personnel(self) -> list[Person]:
        with Session() as session:
            result = session.scalars(select(Pilot))
            
            personnel: list[Person] = []

            for user in result:
                person = Person(user.id, user.last_name, user.first_name, user.ausm_tier)

                if (len(user.assigned_org) > 0):
                    org = user.assigned_org[0].name
                    person.assign_to(org)
                for qual in user.quals:
                    person.qual(Qualification(qual.type.name, qual.name))

                personnel.append(person)
        
        return personnel

    def get_duties(self) -> list[Duty]:
        with Session() as session:
            result = session.scalars(select(ShellDuty))

            duties = [Duty(duty_dto.duty.name, duty_dto.duty.duty_type.name, duty_dto.start_date_time, duty_dto.end_date_time) for duty_dto in result]
            return duties

    def get_lines(self) -> list[Line]:
        with Session() as session:
            result = session.scalars(select(ShellLine))

            lines = [Line(line_dto.num, line_dto.org.name, line_dto.start_date_time) for line_dto in result]
            return lines

    def get_absences(self) -> list[AbsenceRequest]:
        ars = []

        with Session() as session:
            result = session.scalars(select(AbsenceRequestDto))

            for ar_dto in result:
                if (ar_dto.day_of_week_ptn == None or ar_dto.day_of_week_ptn == 0):
                    ars.append(AbsenceRequest(ar_dto.person_id, ar_dto.start_date_time, ar_dto.end_date_time))
                else:
                    init_dt = True
                    for single_dt in daterange(ar_dto.start_date_time, ar_dto.occur_end_date_time):

                        if (init_dt == True):
                            ars.append(AbsenceRequest(ar_dto.person_id, single_dt, ar_dto.end_date_time))
                            init_dt = False
                        elif ((1 << single_dt.isoweekday()) & ar_dto.day_of_week_ptn):
                            new_end_dt = ar_dto.end_date_time + timedelta(days = (single_dt - ar_dto.start_date_time).days)
                            ars.append(AbsenceRequest(ar_dto.person_id, single_dt, new_end_dt))

        return ars