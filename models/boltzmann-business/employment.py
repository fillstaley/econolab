"""...
"""


from __future__ import annotations
from collections import deque

class Employee:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._open_employment_applications: list[EmploymentApplication] = []
        self._closed_employment_applications: list[EmploymentApplication] = []
        
        self._current_employment_contracts: list[EmploymentContract] = []
        self._past_employment_contracts: list[EmploymentContract] = []
    
    @property
    def reviewed_employment_applications(self) -> list[EmploymentApplication]:
        return [a for a in self._open_employment_applications if not a.pending]


class Employer:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.payroll: dict[Employee, EmploymentContract] = {}
        
        self._received_job_applications: dict[Job, deque[EmploymentApplication]] = {}
    
    ##############
    # Properties #
    ##############
    
    @property
    def employees(self) -> list[Employee]:
        return list(self.payroll.keys())
    
    @property
    def open_jobs(self) -> list[Job]:
        return list(self._received_job_applications.keys())
    
    ###########
    # Methods #
    ###########
    
    def begin_hiring(self, job: Job) -> bool:
        """Initializes a queue for receiving applications for an open job."""
        if not job.open_positions:
            return False
        
        if job in self._received_job_applications:
            return False
        
        # we initialize an empty queue for applications
        self._received_job_applications[job] = deque()
        return True
    
    def receive_employment_application(self, application: EmploymentApplication):
        job = application.job
        if job in self._received_job_applications:
            self._received_job_applications[job].append(application)
    
    def next_employment_application(self, job: Job) -> EmploymentApplication | None:
        if job not in self._received_job_applications:
            return None
        
        if not (queue := self._received_job_applications[job]):
            return None
        return queue.popleft()
    
    def end_hiring(self, job: Job) -> bool:
        """Denies all remaining applications for a job and deletes the queue."""
        if job.open_positions:
            return False
        
        if job not in self._received_job_applications:
            return False
        
        # we clear the queue of applications then remove it
        while application := self.next_employment_application(job):
            application.deny()
        del self._received_job_applications[job]
        return True
    
    def hire(self, application: EmploymentApplication, date: int) -> EmploymentContract | None:
        """Adds an employee to the payroll.

        Parameters
        ----------
        application : JobApplication
            An approved employment application.
        date : int
            The date on which the applicant is hired.

        Returns
        -------
        Job | None
            If the application is approved, and the applicant is not already an
            employee, then a new Job instance is returned; otherwise None is returned.
        """
        if application.approved:
            contract = EmploymentContract()
            self.payroll[application.applicant] = contract
            return contract
        return None
    
    
    def fire(self, employee: Employee, date: int) -> bool:
        """Removes an employee from the payroll.

        Parameters
        ----------
        employee : Employee
            The employee to be fired.
        date : int
            The date on which the employee is fired.
        """
        if employee in self.payroll:
            del self.payroll[employee]
            return True
        return False


class Job:
    def __init__(self, employer: Employer, *employees: Employee, max_employees: int = 1):
        self.employer = employer
        self.employees = list(employees)
        self.max_employees = max_employees
    
    @property
    def open_positions(self) -> bool:
        return self.max_employees - len(self.employees)
    
    def apply(self, applicant: Employee) -> EmploymentApplication | None:
        if self.open_positions:
            application = EmploymentApplication(applicant, job=self)
            self.employer.receive_employment_application(application)
            return application
        return None


class EmploymentApplication:
    def __init__(self, applicant: Employee, job: Job) -> None:
        self.applicant = applicant
        self.job = job
        
        # _approved can be True (approved), False (denied), or None (pending)
        self._approved: bool | None = None
    
    @property
    def employer(self) -> Employer:
        return self.job.employer

    @property
    def pending(self) -> bool:
        """Returns True if the application has been neither approved nor denied."""
        return self._approved is None

    @property
    def approved(self) -> bool:
        """Returns True if the application has been approved."""
        return self._approved is True
    
    @property
    def denied(self) -> bool:
        """Returns True if the application has been denied."""
        return self._approved is False
    
    def approve(self):
        """Changes the application from pending to approved."""
        if self._approved is None:
            self._approved = True
    
    def deny(self):
        """Changes the application from pending to denied."""
        if self._approved is None:
            self._approved = False
    
    def accept(self) -> EmploymentContract:
        return self.employer.hire(self)


class EmploymentContract:
    pass
