import numpy as np
import matplotlib.pyplot as plt

def plot_univariate(data: np.ndarray, title: str, pctiles: dict, outpath):
    """
    Draws a histogram with P50/P90 lines in distinct colors.
    Expects pctiles keys only relevant to this series (e.g. {'P50 Duration':…, 'P90 Duration':…}).
    """
    plt.figure()
    plt.hist(data, bins=50, density=True, alpha=0.7, color='lightgray')

    # assign colors/styles per percentile
    style = {
        list(pctiles.keys())[0]: {'color':'C0','linestyle':'--'},  # P50
        list(pctiles.keys())[1]: {'color':'C1','linestyle':'-.'},  # P90
    }

    for name, val in pctiles.items():
        plt.axvline(val, label=f'{name} = {val:.2f}', **style[name])

    plt.title(title)
    plt.xlabel(title)
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def plot_cdf(data: np.ndarray, title: str, pctiles: dict, outpath):
    """
    Draws a CDF with P50/P90 lines in distinct colors.
    Expects pctiles keys only relevant to this series.
    """
    plt.figure()
    x = np.sort(data)
    y = np.linspace(0,1,len(x))
    plt.plot(x, y, color='black')

    style = {
        list(pctiles.keys())[0]: {'color':'C0','linestyle':'--'},  # P50
        list(pctiles.keys())[1]: {'color':'C1','linestyle':'-.'},  # P90
    }

    for name, val in pctiles.items():
        plt.axvline(val, label=f'{name} = {val:.2f}', **style[name])

    plt.title(title)
    plt.xlabel(title)
    plt.ylabel('CDF')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def plot_joint_scatter(durations: np.ndarray,
                       costs: np.ndarray,
                       pctiles: dict,
                       cost_target: float,
                       time_target: float,
                       outpath):
    
    plt.figure(figsize=(6,6))
    plt.scatter(durations, costs, s=5, alpha=0.3, color='grey')

    # duration P50/P90 (blue)
    plt.axvline(pctiles['P50 Duration'], color='C0', linestyle='--',
                label=f"P50 Dur={pctiles['P50 Duration']:.2f}")
    
    plt.axvline(pctiles['P90 Duration'], color='C0', linestyle=':',
                label=f"P90 Dur={pctiles['P90 Duration']:.2f}")

    # cost P50/P90 (green)
    plt.axhline(pctiles['P50 Cost'], color='C1', linestyle='--',
                label=f"P50 Cost={pctiles['P50 Cost']:.2f}")
    
    plt.axhline(pctiles['P90 Cost'], color='C1', linestyle=':',
                label=f"P90 Cost={pctiles['P90 Cost']:.2f}")

    # user targets (red solid)
    plt.axvline(time_target, color='C2', linestyle='-', label=f"Time tgt={time_target:.2f}")
    plt.axhline(cost_target, color='C3', linestyle='-', label=f"Cost tgt={cost_target:.2f}")

    plt.title('Joint Cost–Duration Scatter')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.legend(loc='best', fontsize='small')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def plot_joint_heatmap(durations: np.ndarray,
                       costs: np.ndarray,
                       outpath,
                       bins: int = 50):
    
    plt.figure(figsize=(6,6))
    plt.hist2d(durations, costs, bins=bins, cmap='Blues')
    plt.colorbar(label='Count')
    plt.title('Joint Cost–Duration Heatmap')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def plot_tornado(corrs: dict, title: str, outpath, top_n: int = 10):
    
    items = sorted(corrs.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    names, vals = zip(*items) if items else ([], [])
    plt.figure(figsize=(8, max(2, len(names)*0.4)))
    y_pos = np.arange(len(names))
    plt.barh(y_pos, vals, align='center', color='C'+str( (hash(title) % 10) ))
    plt.yticks(y_pos, names)
    plt.xlabel('Correlation')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
