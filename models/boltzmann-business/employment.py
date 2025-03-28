"""...
"""


from __future__ import annotations
from collections import deque, defaultdict

from econolab import BaseAgent

class Employee(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._open_employment_applications: list[EmploymentApplication] = []
        self._closed_employment_applications: list[EmploymentApplication] = []
        
        self._current_employment_contracts: list[EmploymentContract] = []
        self._past_employment_contracts: list[EmploymentContract] = []
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def reviewed_employment_applications(self) -> list[EmploymentApplication]:
        return [a for a in self._open_employment_applications if not a.pending]
    
    @property
    def applied_jobs(self) -> set[Job]:
        return {app.job for app in self._open_employment_applications}
    
    @property
    def number_of_jobs(self) -> int:
        return len(self._current_employment_contracts)


class Employer(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.payroll: dict[Employee, EmploymentContract] = {}
        
        self._received_job_applications: dict[Job, deque[EmploymentApplication]] = {}
        self._outstanding_job_offers: dict[Job, list[EmploymentApplication]] = {}
    
    ##############
    # Properties #
    ##############
    
    @property
    def employees(self) -> set[Employee]:
        return set(self.payroll.keys())
    
    @property
    def open_jobs(self) -> set[Job]:
        return set(self._received_job_applications.keys())
    
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
        self._outstanding_job_offers[job] = []
        return True
    
    
    def receive_employment_application(self, application: EmploymentApplication):
        
        job = application.job
        if job in self._received_job_applications:
            self._received_job_applications[job].append(application)
    
    
    def review_employment_applications(
        self, 
        open_jobs: list[Job], 
        review_limit: int | None = None
    ) -> int:
        
        apps_reviewed: int = 0
        for job in open_jobs:
            # determine how many applications can be accepted and get application queue
            offers_outstanding = len(self._outstanding_job_offers[job])
            offers_available = job.open_positions
            queue = self._received_job_applications[job]
            while (
                (review_limit is None or apps_reviewed >= review_limit)
                and offers_available
                and queue
            ):
                # increment the counter and get the next application
                apps_reviewed += 1
                application = queue.popleft()
                
                # decide whether to approve or deny the application
                if self.decide_employment(application):
                    application.approve()
                    offers_available -= 1
                    self._outstanding_job_offers[job].append(application)
                else:
                    application.deny()
            
            # if we hit our review limit, break out of the for loop over open jobs
            if review_limit is None or apps_reviewed >= review_limit:
                break
        return apps_reviewed
    
    
    def decide_employment(self, application: EmploymentApplication) -> bool:
        """
        Default decision method for an application.
        Returns True if the application is approved, False otherwise.
        The default behavior might be a simple random coin flip.
        """
        # Default: approve based on a random probability.
        return self.random.random() < self.approval_probability
    
    
    def end_hiring(self, job: Job) -> bool:
        """Denies all remaining applications for a job and deletes the queue."""
        if job.open_positions:
            return False
        
        if job not in self._received_job_applications:
            return False
        
        # ensure that the list of outstanding job offers is empty
        if self._outstanding_job_offers[job]:
            return False
        
        # clear the application queue by denying all applications
        queue = self._received_job_applications[job]
        while queue:
            application = queue.popleft()
            application.deny()
        
        # remove both the application queue and the outstanding jobs list
        del self._received_job_applications[job]
        del self._outstanding_job_offers[job]
        return True
    
    
    def hire(self, application: EmploymentApplication, date: int = 0) -> EmploymentContract | None:
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
            
            employee = application.applicant
            job = application.job
            
            contract = EmploymentContract(self, employee)
            self.payroll[employee] = contract
            
            job.employees.append(employee)
            if not job.open_positions:
                self.end_hiring(job)
            
            return contract
        return None
    
    
    def fire(self, employee: Employee, date: int = 0) -> bool:
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
    
    
    def record_attendance(self, employees: list[Employee]) -> None:
        for employee in employees:
            if employee not in self.employees:
                raise ValueError(f"{employee} is not employed by this employer.")
            self.payroll[employee].steps_worked += 1


class Job:
    def __init__(self, employer: Employer, *employees: Employee, max_employees: int = 1):
        self.employer = employer
        self.employees = list(employees)
        self.max_employees = max_employees
    
    @property
    def open_positions(self) -> bool:
        return max(0, self.max_employees - len(self.employees))
    
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
    def __init__(self, employer: Employer, employee: Employee):
        self.employer = employer
        self.employee = employee
        
        self.steps_worked: int = 0
