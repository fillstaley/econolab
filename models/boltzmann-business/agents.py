"""...
"""


from __future__ import annotations

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
            sample_size = min(3, len(self.model.job_board))
            jobs_sample = self.random.sample(self.model.job_board, sample_size)
            for job in jobs_sample:
                if application := job.apply(self):
                    self._open_employment_applications.append(application)

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()


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
        
        self.employment_apps_reviewed = 0
        
        open_jobs = self.open_jobs
        self.random.shuffle(open_jobs)
        
        # loop over the open jobs and review as many applications as possible
        for job in open_jobs:
            # each job has only so many open positions, 
            # we don't want to offer more jobs than are available
            offers_available = job.open_positions
            
            while (
                (
                    self.employment_apps_review_limit is None
                    or self.employment_apps_reviewed < self.employment_apps_review_limit
                )
                and offers_available > 0
                and (application := self.next_employment_application(job))
            ):
                self.employment_apps_reviewed += 1
                
                # for now, randomly decide whether to approve or deny the application
                if self.random.random() < self.approval_probability:
                    application.approve()
                    offers_available -= 1
                else:
                    application.deny()
            
            # if we hit our review limit, break out of the for loop over open jobs
            if (
                self.employment_apps_review_limit is None
                or self.employment_apps_reviewed >= self.employment_apps_review_limit
            ):
                break

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
