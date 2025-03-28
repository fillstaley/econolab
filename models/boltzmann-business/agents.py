"""...
"""


from __future__ import annotations
from collections import deque

import mesa

from econolab import banking

import employment


class Individual(employment.Employee, banking.Agent, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)
        
    
    ##############
    # Properties #
    ##############
    
    
    ##############
    # Act Method #
    ##############
    
    def act(self) -> None:
        
        # process reviewed employment applications
        for app in self.reviewed_employment_applications:
            if app.approved and not self._current_employment_contracts:
                if contract := app.accept():
                    self._current_employment_contracts.append(contract)
            self._open_employment_applications.remove(app)
            self._closed_employment_applications.append(app)
        
        # if unemployed, search and apply for open jobs
        if not self._current_employment_contracts and getattr(self.model, "job_board", None):
            for job in self.search_for_jobs(self.model.job_board, num_jobs=3):
                if (application := job.apply(self)) is None:
                    continue
                self._open_employment_applications.append(application)

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()
    
    def search_for_jobs(
        self, 
        job_board: list[employment.Job], 
        num_jobs: int, 
        max_attempts: int | None = None
    ) -> list[employment.Job]:
        """Returns a list of jobs for which the individual can and would like to apply."""
        preferred_jobs = []
        
        # create a copy of the list of jobs
        # later: filter for jobs for which the individual is qualified
        # later: filter by some coarse desirability conditions
        suitable_jobs = list(job_board)
        
        # Shuffle the qualified jobs and convert them into a deque (for sampling without replacement)
        self.random.shuffle(suitable_jobs)
        jobs_deque = deque(suitable_jobs)
        
        # If max_attempts isn't provided, default to len(job_board)
        if max_attempts is None:
            max_attempts = len(jobs_deque)
        
        attempts = 0
        while len(preferred_jobs) < num_jobs and attempts < max_attempts and jobs_deque:
            attempts += 1
            job = jobs_deque.popleft()
            
            # skip jobs for which the individual has already applied
            if job in self.applied_jobs:
                continue
            
            # later: apply some finer desirability conditions
            preferred_jobs.append(job)

        return preferred_jobs


class Business(employment.Employer, banking.Agent, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)
        
        self.employment_apps_review_limit: int | None = None
        
        self.approval_probability = 1.0
        
        # for now, create 10 jobs with 1 position each
        for _ in range(10):
            job = employment.Job(self, max_employees=1)
            self.begin_hiring(job)
    
    ##############
    # Properties #
    ##############

    
    ##############
    # Act Method #
    ##############
    
    def act(self) -> None:
        
        self.record_attendance(self.employees)
        
        # create a list of open jobs and prioritize (for now, shuffle) them
        open_jobs = list(self.open_jobs)
        self.random.shuffle(open_jobs)
        # and then review employment applications for them
        self.review_employment_applications(open_jobs)
    
    
    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()
    
    def begin_hiring(self, job):
        super().begin_hiring(job)
        
        if getattr(self.model, "job_board", None) is not None:
            self.model.job_board.append(job)
    
    def end_hiring(self, job):
        super().end_hiring(job)
        
        if getattr(self.model, "job_board", None) is not None and job in self.model.job_board:
            self.model.job_board.remove(job)


class Bank(banking.Bank, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)


    ##############
    # Properties #
    ##############


    ##############
    # Act Method #
    ##############

    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()


class ReserveBank(banking.ReserveBank, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)


    ##############
    # Properties #
    ##############


    ##############
    # Act Method #
    ##############

    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()
