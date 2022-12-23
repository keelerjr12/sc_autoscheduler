from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class Qualification:
    def __init__(self, type: str, name: str):
        self._type = type
        self._name = name

    def type(self):
        return self._type

    def name(self):
        return self._name

class Person:
    def __init__(self, id: int, last_name: str, first_name: str, ausm_tier: int):
        self._id = id
        self._first_name = first_name
        self._last_name = last_name

        self._quals = {
            'Duty': set(),
            'Flight': set()
        }

        self._assigned_org = None
        self._ausm_tier = ausm_tier

    def __eq__(self, other):
        if (not isinstance(other, Person)):
            return False

        return self.id() == other.id()

    def id(self) -> int:
        return self._id

    def assign_to(self, org: str | None):
        self._assigned_org = org

    def qual(self, qualification: Qualification):
        self._quals[qualification.type()].add(qualification.name())

    def is_qualified_for(self, qualification: Qualification) -> bool:
        return qualification.name() in self._quals[qualification.type()]

class Commitment(ABC):
    #    TODO: issue with absence request; need to migrate to entity class
    #    @abstractmethod
    #    def id(self):
    #        pass

    @abstractmethod
    def start_dt(self) -> datetime:
        pass

    @abstractmethod
    def end_dt(self) -> datetime:
        pass

    def assign(self, person: Person) -> None:
        self._person = person

    def assigned_to(self) -> Person:
        return self._person

    def is_conflict(self, other) -> bool:
        return other.end_dt() > self.start_dt() and other.start_dt() < self.end_dt()

class Line(Commitment):

    def __init__(self,number: int, org: str, time_takeoff: datetime):
        self.number = number
        self.flight_org = org

        self.time_takeoff = time_takeoff
        self.time_brief = time_takeoff - timedelta(hours=1, minutes=15)
        self.time_debrief_end = self.time_brief + timedelta(hours=3, minutes=30)

    def id(self):
        return str(self.number) + self.start_dt().strftime("%m/%d/%Y")

    def start_dt(self) -> datetime:
        return self.time_brief

    def end_dt(self) -> datetime:
        return self.time_debrief_end

class Duty(Commitment):

    def __init__(self, name: str, type: str, sign_in_dt: datetime, sign_out_dt: datetime):
        assert(sign_in_dt <= sign_out_dt)

        self.name = name
        self.type = type
        self._sign_in_dt = sign_in_dt
        self._sign_out_dt = sign_out_dt

    def id(self):
        return self.name + self._sign_in_dt.strftime("%m/%d/%Y")

    def is_type(self, duty_types: str | list[str]) -> bool:
        if (not isinstance(duty_types, list)):
            return self.type == duty_types

        for type in duty_types:
            if type == self.type:
                return True 

        return False

    def start_dt(self) -> datetime:
        return self._sign_in_dt

    def end_dt(self) -> datetime:
        return self._sign_out_dt

class AbsenceRequest(Commitment):

    def __init__(self, prsn_id: int, start_dt: datetime, end_dt: datetime):
        assert(start_dt <= end_dt)

        self._prsn_id = prsn_id
        self._start_dt = start_dt
        self._end_dt = end_dt

    def __eq__(self, other):
        if (not isinstance(other, AbsenceRequest)):
            return NotImplemented

        return other._prsn_id == self._prsn_id and other._start_dt == self._start_dt and other._end_dt == self._end_dt

    def __str__(self) -> str:
        return self._start_dt.strftime('%m/%d/%Y %I:%M:%S %p') + " " + self._end_dt.strftime('%m/%d/%Y %I:%M:%S %p')

    def start_dt(self) -> datetime:
        return self._start_dt

    def end_dt(self) -> datetime:
        return self._end_dt

    def assigned_to(self, prsn: Person) -> bool:
        return self._prsn_id == prsn.id

class Day:

    def __init__(self, date: datetime.date):
        self._date = date
        self._commitments = {}

    def insert(self, commitment: Commitment) -> None:
        commit_type = type(commitment)

        if (commit_type not in self._commitments):
            self._commitments[commit_type] = []

        self._commitments[commit_type].append(commitment)

    def commitments(self, commit_type: None | Commitment = None) -> list[Commitment]:
        if (commit_type == None):
            return [commit for l in self._commitments.values() for commit in l]

        if commit_type not in self._commitments:
            return []
        
        return self._commitments[commit_type]

    def date(self) -> datetime.date:
        return self._date