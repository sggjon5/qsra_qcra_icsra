import numpy as np

class Task:

    def __init__(self,
                 task_id: str,
                 name: str,
                 a_dur: float, m_dur: float, b_dur: float,
                 a_cost: float, m_cost: float, b_cost: float,
                 dist_type: str,
                 is_critical: bool):
        
        self.task_id = task_id
        self.name = name
        self.a_dur, self.m_dur, self.b_dur = a_dur, m_dur, b_dur
        self.a_cost, self.m_cost, self.b_cost = a_cost, m_cost, b_cost
        self.dist_type = dist_type.lower()
        self.is_critical = is_critical
        self._derive_params()

    def _derive_params(self):

        # common PERT formulas
        self.mean_dur = (self.a_dur + 4*self.m_dur + self.b_dur) / 6
        self.std_dur  = (self.b_dur - self.a_dur) / 6
        self.min_dur, self.max_dur = self.a_dur, self.b_dur

        self.mean_cost = (self.a_cost + 4*self.m_cost + self.b_cost) / 6
        self.std_cost  = (self.b_cost - self.a_cost) / 6
        self.min_cost, self.max_cost = self.a_cost, self.b_cost

        if self.dist_type == 'beta':

            lambda_ = 4.0
            self.alpha_dur = 1 + lambda_*(self.m_dur - self.a_dur)/(self.b_dur - self.a_dur)
            self.beta_dur  = 1 + lambda_*(self.b_dur - self.m_dur)/(self.b_dur - self.a_dur)
            self.alpha_cost = 1 + lambda_*(self.m_cost - self.a_cost)/(self.b_cost - self.a_cost)
            self.beta_cost  = 1 + lambda_*(self.b_cost - self.m_cost)/(self.b_cost - self.a_cost)

    def sample_duration(self, rng: np.random.Generator, size: int):

        dt = self.dist_type

        if dt == 'point':
            return np.full(size, self.mean_dur)
        
        if dt == 'normal':
            return rng.normal(self.mean_dur, self.std_dur, size)
        
        if dt == 'uniform':
            return rng.uniform(self.min_dur, self.max_dur, size)
        
        if dt == 'beta':
            u = rng.beta(self.alpha_dur, self.beta_dur, size)
            return self.min_dur + u*(self.max_dur - self.min_dur)
        
        if dt == 'triangular':
            # left=a_dur, mode=m_dur, right=b_dur
            return rng.triangular(self.a_dur, self.m_dur, self.b_dur, size)
        
        raise ValueError(f'Unknown dist_type "{dt}"')
    


    def sample_cost(self, rng: np.random.Generator, size: int):

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
