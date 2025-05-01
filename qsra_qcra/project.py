import numpy as np
import pandas as pd
from pathlib import Path
# from pandas.tseries.offsets import BusinessDay

from .viz import (
    plot_univariate,
    plot_cdf,
    plot_joint_scatter,
    plot_joint_heatmap,
    plot_tornado
)

class Project:

    def __init__(self, tasks, n_iters=10_000, seed=None):

        self.tasks = tasks
        self.n_iters = n_iters
        self.rng = np.random.default_rng(seed)

    def simulate(self):
        # sample all at once, store per-task arrays
        mats_dur = []
        mats_cost = []

        for t in self.tasks:
            ds = t.sample_duration(self.rng, self.n_iters)
            cs = t.sample_cost(self.rng, self.n_iters)
            mats_dur.append(ds)
            mats_cost.append(cs)

        dur_matrix  = np.vstack(mats_dur)   # shape: (ntasks, n_iters)
        cost_matrix = np.vstack(mats_cost)

        # aggregate
        crit_mask = np.array([t.is_critical for t in self.tasks])
        self.durations = dur_matrix[crit_mask].sum(axis=0)
        self.costs     = cost_matrix.sum(axis=0)

        # keep raw samples for sensitivity
        self._dur_matrix  = dur_matrix
        self._cost_matrix = cost_matrix

        return self.durations, self.costs

    def summarise(self):

        p50_d, p90_d = np.percentile(self.durations, [50, 90])
        p50_c, p90_c = np.percentile(self.costs,     [50, 90])

        return {
            'P50 Duration': p50_d,
            'P90 Duration': p90_d,
            'P50 Cost':     p50_c,
            'P90 Cost':     p90_c
        }

    def percentiles(self):
        # every 10th percentile (10–90)
        perc = list(range(10, 100, 10))
        p_d = np.percentile(self.durations, perc)
        p_c = np.percentile(self.costs,     perc)

        df = pd.DataFrame({
                'Percentile': [f"P{p}" for p in perc],
                'Duration':   p_d,
                'Cost':       p_c
            })
        
        return df

    def joint_probability(self, cost_target: float, duration_target: float) -> float:

        return float(np.mean((self.costs <= cost_target) &
                             (self.durations <= duration_target)))

    def correlation(self) -> float:
        # guard against zero‐variance
        if np.std(self.durations)==0 or np.std(self.costs)==0:
            return 0.0
        
        return float(np.corrcoef(self.durations, self.costs)[0,1])

    def sensitivity(self, top_n: int = 10):

        names    = [t.name for t in self.tasks]
        crit_mask = np.array([t.is_critical for t in self.tasks])

        corr_dur = {}
        corr_cost = {}

        # overall zero‐variance guard
        std_dur = np.std(self.durations)
        std_cos = np.std(self.costs)

        for i, name in enumerate(names):
            row_d = self._dur_matrix[i]
            row_c = self._cost_matrix[i]

            # duration sens only if on critical path
            if crit_mask[i] and std_dur>0 and np.std(row_d)>0:
                corr_dur[name] = float(np.corrcoef(row_d, self.durations)[0,1])

            else:
                corr_dur[name] = 0.0

            # cost sens
            if std_cos>0 and np.std(row_c)>0:
                corr_cost[name] = float(np.corrcoef(row_c, self.costs)[0,1])

            else:
                corr_cost[name] = 0.0

        top_dur  = dict(sorted(corr_dur.items(),  key=lambda x: abs(x[1]), reverse=True)[:top_n])
        top_cost = dict(sorted(corr_cost.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n])

        return top_dur, top_cost

    def plot_results(self, outdir: Path, cost_target=None, time_target=None):#, start_date = None):
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        pct = self.summarise()

        # filter for each series
        dur_pct  = {'P50 Duration': pct['P50 Duration'], 'P90 Duration': pct['P90 Duration']}
        cost_pct = {'P50 Cost': pct['P50 Cost'],       'P90 Cost': pct['P90 Cost']}

        # univariate
        # plot_univariate(self.durations, 'Duration', dur_pct, outdir/'duration_hist.png')
        # plot_cdf(self.durations, 'Duration CDF', dur_pct, outdir/'duration_cdf.png')

        # if start_date given, convert durations → business-day dates
        # if start_date:
        #     import pandas as pd, numpy as np
        #     days = np.ceil(self.durations).astype(int)
        #     # compute a numpy array of Timestamps
        #     dates = np.array([pd.to_datetime(start_date) + BusinessDay(n=d) for d in days])
        #     # date percentiles for P50/P90
        #     p50d = pd.to_datetime(start_date) + BusinessDay(int(np.ceil(pct['P50 Duration'])))
        #     p90d = pd.to_datetime(start_date) + BusinessDay(int(np.ceil(pct['P90 Duration'])))
        #     date_pct = {'P50 Date': p50d, 'P90 Date': p90d}
        #     plot_univariate(dates, 'Completion Date', date_pct,
        #                     outdir/'completion_date_hist.png')
        #     plot_cdf(dates, 'Completion Date CDF', date_pct,
        #              outdir/'completion_date_cdf.png')
        # else:
        plot_univariate(self.durations, 'Duration', dur_pct, outdir/'duration_hist.png')
        plot_cdf(self.durations, 'Duration CDF', dur_pct, outdir/'duration_cdf.png')

        plot_univariate(self.costs,     'Cost',     cost_pct, outdir/'cost_hist.png')
        plot_cdf(self.costs,     'Cost CDF',     cost_pct, outdir/'cost_cdf.png')

        # joint
        if cost_target is not None and time_target is not None:
            
            plot_joint_scatter(self.durations, self.costs, pct,
                               cost_target, time_target,
                               outdir/'joint_scatter.png')
            
            plot_joint_heatmap(self.durations, self.costs,
                               outdir/'joint_heatmap.png')

        # tornado
        td, tc = self.sensitivity(top_n=10)
        plot_tornado(td, "Duration Sensitivity (top 10)", outdir/'tornado_duration.png')
        plot_tornado(tc, "Cost Sensitivity (top 10)",     outdir/'tornado_cost.png')

        # percentiles table
        df = self.percentiles()
        df.to_csv(outdir/'percentiles_table.csv', index=False)
