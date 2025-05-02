import numpy as np
import matplotlib.pyplot as plt

def plot_univariate(data: np.ndarray, title: str, pctiles: dict, outpath):
    """
    Draws a histogram of `data` with vertical lines for P50 and P90 percentiles.

    Parameters:
    data (np.ndarray): array of values to plot
    title (str): title and xlabel of the plot
    pctiles (dict): dictionary with two keys (e.g., 'P50 Duration', 'P90 Duration') mapping to percentile values
    outpath: file path where the plot image will be saved
    """
    # create a new figure
    plt.figure()

    # plot normalised histogram 
    plt.hist(data, bins=50, density=True, alpha=0.7, color='lightgray')

    # assign colors/styles per percentile
    style = {
        list(pctiles.keys())[0]: {'color':'C0','linestyle':'--'},  # P50
        list(pctiles.keys())[1]: {'color':'C1','linestyle':'-.'},  # P90
    }

    # add vertical lines for each percentile 
    for name, val in pctiles.items():
        plt.axvline(val, label=f'{name} = {val:.2f}', **style[name])

    # plotting admin
    plt.title(title)
    plt.xlabel(title)
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()

    # save figure to where it needs to go and close it
    plt.savefig(outpath)
    plt.close()

def plot_cdf(data: np.ndarray, title: str, pctiles: dict, outpath):
    """
    Draws a cumulative distribution function (CDF) with P50 and P90 lines.

    Parameters:
    data (np.ndarray): array of values to plot
    title (str): title and xlabel of the plot
    pctiles (dict): dictionary with percentile names and values
    outpath: file path for saving the plot
    """
    # create new fig
    plt.figure()

    # order data for cdf line
    x = np.sort(data)
    y = np.linspace(0,1,len(x))

    # plot cdf
    plt.plot(x, y, color='black')

    # define styles for percentile lines
    style = {
        list(pctiles.keys())[0]: {'color':'C0','linestyle':'--'},  # P50
        list(pctiles.keys())[1]: {'color':'C1','linestyle':'-.'},  # P90
    }
     # plot percentile lines
    for name, val in pctiles.items():
        plt.axvline(val, label=f'{name} = {val:.2f}', **style[name])

    # plotting admin and saving
    plt.title(title)
    plt.xlabel(title)
    plt.ylabel('CDF')
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()



def plot_joint_scatter(durations: np.ndarray,costs: np.ndarray,pctiles: dict,cost_target: float,time_target: float, outpath):
    """
    Draws a scatter plot of durations vs. costs with lines for percentiles and user targets.

    Parameters:
    durations (np.ndarray): array of project durations
    costs (np.ndarray): array of project costs
    pctiles (dict): contains 'P50 Duration', 'P90 Duration', 'P50 Cost', 'P90 Cost'
    cost_target (float): user-defined cost threshold to mark on plot
    time_target (float): user-defined time threshold to mark on plot
    outpath: location to save the scatter plot image
    """
    # create new square figure
    plt.figure(figsize=(6,6))

    # plot particles as scatter
    #TODO change colouuring of this so that below both targets is green, above both targets is red and if only one below target is grey
    plt.scatter(durations, costs, s=5, alpha=0.3, color='grey')

    # duration P50/P90 (blue)
    plt.axvline(pctiles['P50 Duration'], color='C0', linestyle='--',label=f"P50 Dur={pctiles['P50 Duration']:.2f}")
    plt.axvline(pctiles['P90 Duration'], color='C0', linestyle=':',label=f"P90 Dur={pctiles['P90 Duration']:.2f}")

    # cost P50/P90 (green)
    plt.axhline(pctiles['P50 Cost'], color='C1', linestyle='--',label=f"P50 Cost={pctiles['P50 Cost']:.2f}")
    plt.axhline(pctiles['P90 Cost'], color='C1', linestyle=':',label=f"P90 Cost={pctiles['P90 Cost']:.2f}")


    # user targets for cost and duration
    plt.axvline(time_target, color='purple', linestyle='-', label=f"Time tgt={time_target:.2f}")
    plt.axhline(cost_target, color='purple', linestyle='-', label=f"Cost tgt={cost_target:.2f}")

    # plotting admin and saving
    plt.title('Joint Cost–Duration Scatter')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.legend(loc='best', fontsize='small')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()



def plot_joint_heatmap(durations: np.ndarray,costs: np.ndarray,outpath,bins: int = 50):
    """
    Draws a 2D histogram (heatmap) of durations vs. costs.

    Parameters:
    durations (np.ndarray): array of durations
    costs (np.ndarray): array of costs
    outpath: filepath to save the heatmap image
    bins (int): number of bins for both axes in the histogram
    """
    # create new square figure
    plt.figure(figsize=(6,6))

    # 2d histogram with blue colourmap
    plt.hist2d(durations, costs, bins=bins, cmap='Blues')
    plt.colorbar(label='Count') # schow colour bar legend
    plt.title('Joint Cost–Duration Heatmap')
    plt.xlabel('Duration')
    plt.ylabel('Cost')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()



def plot_tornado(corrs: dict, title: str, outpath, top_n: int = 10):
    """
    Draws a horizontal bar chart (tornado plot) of the top_n correlations.

    Parameters:
    corrs (dict): mapping of item names to correlation values
    title (str): title of the plot
    outpath: file path for saving the tornado plot
    top_n (int): number of top items (by absolute correlation) to display
    """
    # sort items by correlation descending and select top_n
    items = sorted(corrs.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]
    names, vals = zip(*items) if items else ([], [])

    # height based on number of bars
    plt.figure(figsize=(8, max(2, len(names)*0.4)))
    y_pos = np.arange(len(names))

    plt.barh(y_pos, vals, align='center', color='purple')
    plt.yticks(y_pos, names)
    plt.xlabel('Correlation')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
