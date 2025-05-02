import numpy as np

class Task:
    """
    Represents a single project task with duration and cost distributions.
    Supports sampling from various distribution types (point, normal, uniform, beta, triangular).
    """

    def __init__(self,task_id: str,name: str,a_dur: float, m_dur: float, b_dur: float,a_cost: float, m_cost: float, b_cost: float,dist_type: str,is_critical: bool):
        """
        Init Task with PERT parameters and distribution type.

        task_id: unique identifier for the task
        name: descriptive task name
        a_dur, m_dur, b_dur: optimistic, most-likely, pessimistic durations
        a_cost, m_cost, b_cost: optimistic, most-likely, pessimistic costs
        dist_type: sampling distribution ('point', 'normal', 'uniform', 'beta', 'triangular')
        is_critical: whether this task is on the critical path
        """

        self.task_id = task_id
        self.name = name
        # duration estimates storage
        self.a_dur, self.m_dur, self.b_dur = a_dur, m_dur, b_dur
        # cost estimates storage
        self.a_cost, self.m_cost, self.b_cost = a_cost, m_cost, b_cost

        # force lower case 
        self.dist_type = dist_type.lower()

        #citical path or not
        self.is_critical = is_critical

        # calculate distrivution params based on these estimates
        self._derive_params()

    def _derive_params(self):

        # PERT formulas for mean and standard deviation of a beta-like distribution
        self.mean_dur = (self.a_dur + 4*self.m_dur + self.b_dur) / 6
        self.std_dur  = (self.b_dur - self.a_dur) / 6
        self.min_dur, self.max_dur = self.a_dur, self.b_dur

        self.mean_cost = (self.a_cost + 4*self.m_cost + self.b_cost) / 6
        self.std_cost  = (self.b_cost - self.a_cost) / 6
        self.min_cost, self.max_cost = self.a_cost, self.b_cost

        # If Beta distribution is selected, derive alpha and beta parameters
        if self.dist_type == 'beta':

            lambda_ = 4.0 # shape parameter multiplier used in PERT-beta
            # duration shape params
            self.alpha_dur = 1 + lambda_*(self.m_dur - self.a_dur)/(self.b_dur - self.a_dur)
            self.beta_dur  = 1 + lambda_*(self.b_dur - self.m_dur)/(self.b_dur - self.a_dur)

            # cost shape params
            self.alpha_cost = 1 + lambda_*(self.m_cost - self.a_cost)/(self.b_cost - self.a_cost)
            self.beta_cost  = 1 + lambda_*(self.b_cost - self.m_cost)/(self.b_cost - self.a_cost)

    def sample_duration(self, rng: np.random.Generator, size: int):
        """
        Sample durations for this task using the specified distribution type.

        rng: numpy random generator
        size: number of samples to draw
        returns: array of length `size`
        """
        dt = self.dist_type

        if dt == 'point':
            # constant (point) distribution at the mean
            return np.full(size, self.mean_dur)
        
        if dt == 'normal':
            # Gaussian around mean with calculated std
            return rng.normal(self.mean_dur, self.std_dur, size)
        
        if dt == 'uniform':
            # uniform between min and max
            return rng.uniform(self.min_dur, self.max_dur, size)
        
        if dt == 'beta':
            # scale a beta-distributed varaible to min,max
            u = rng.beta(self.alpha_dur, self.beta_dur, size)
            return self.min_dur + u*(self.max_dur - self.min_dur)
        
        if dt == 'triangular':
            # triangular distribution with left=a_dur, mode=m_dur, right=b_dur
            return rng.triangular(self.a_dur, self.m_dur, self.b_dur, size)
        
        # error if requested dist is not in this list
        raise ValueError(f'Unknown dist_type "{dt}"')
    

    #TODO check if this is redundant, it may be identical to the one above it and therefore should just call that?
    def sample_cost(self, rng: np.random.Generator, size: int):
        """
        Sample costs for this task using the specified distribution type.

        rng: numpy random generator
        size: number of samples to draw
        returns: array of length `size`
        """

        dt = self.dist_type

        if dt == 'point':
            return np.full(size, self.mean_cost)
        
        if dt == 'normal':
            return rng.normal(self.mean_cost, self.std_cost, size)
        
        if dt == 'uniform':
            return rng.uniform(self.min_cost, self.max_cost, size)
        
        if dt == 'beta':
            u = rng.beta(self.alpha_cost, self.beta_cost, size)
            return self.min_cost + u*(self.max_cost - self.min_cost)
        
        if dt == 'triangular':
            return rng.triangular(self.a_cost, self.m_cost, self.b_cost, size)
        
        raise ValueError(f'Unknown dist_type "{dt}"')
