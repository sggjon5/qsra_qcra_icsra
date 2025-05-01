import click
from pathlib import Path
from .data import load_tasks
from .project import Project
from .dashboard import serve_dashboard

@click.group()
def cli():
    """QSRA/QCRA tool with integrated ICSRA, tornado, decile table, & dashboard."""
    pass

@cli.command()
@click.option('--input',     'input_path',  required=True, type=click.Path(exists=True))
@click.option('--iters',     'n_iters',     default=10_000, show_default=True, type=int)
@click.option('--seed',      'seed',        default=None, type=int)
@click.option('--outdir',    'outdir',      default='results', show_default=True, type=click.Path())
@click.option('--cost-target','cost_target', default=None, type=float)
@click.option('--time-target','time_target', default=None, type=float)
# @click.option('--start-date', 'start_date', default=None, help="Project start date (YYYY-MM-DD) to convert into dates")

def run(input_path, n_iters, seed, outdir, cost_target, time_target):
    """Run static ICSRA, output PNGs + console summary + percentile CSV."""
    tasks = load_tasks(Path(input_path))
    proj  = Project(tasks, n_iters=n_iters, seed=seed)
    proj.simulate()

    # parse start date if required
    # if start_date:
    #     import pandas as pd
    #     start_date = pd.to_datetime(start_date).date()

    summary = proj.summarise()

    click.echo(f"P50 Duration: {summary['P50 Duration']:.2f}")
    click.echo(f"P90 Duration: {summary['P90 Duration']:.2f}")
    click.echo(f"P50 Cost:     {summary['P50 Cost']:.2f}")
    click.echo(f"P90 Cost:     {summary['P90 Cost']:.2f}")

    # if start_date:
    #     from pandas.tseries.offsets import BusinessDay
    #     import numpy as np
    #     # compute P50/P90 completion dates
    #     p50 = int(np.ceil(summary['P50 Duration']))
    #     p90 = int(np.ceil(summary['P90 Duration']))
    #     p50_date = pd.to_datetime(start_date) + BusinessDay(p50)
    #     p90_date = pd.to_datetime(start_date) + BusinessDay(p90)
    #     click.echo(f"P50 Completion Date: {p50_date.date()}")
    #     click.echo(f"P90 Completion Date: {p90_date.date()}")

    if cost_target is not None and time_target is not None:

        jcl  = proj.joint_probability(cost_target, time_target)
        corr = proj.correlation()
        click.echo(f"P(cost ≤ {cost_target} & time ≤ {time_target}) = {jcl*100:.2f}%")
        click.echo(f"Correlation (cost vs. time)    = {corr:.2f}")

    # print decile table
    df = proj.percentiles()
    click.echo("\nDecile percentiles:")
    click.echo(df.to_string(index=False))

    proj.plot_results(outdir, cost_target, time_target) #, start_date = start_date)
    click.echo(f"\nAll outputs written to {outdir}/")

@cli.command()
@click.option('--input',  'input_path', required=True, type=click.Path(exists=True))
@click.option('--iters',  'n_iters',    default=5_000, show_default=True, type=int)
@click.option('--seed',   'seed',       default=None, type=int)
@click.option('--host',   'host',       default='127.0.0.1', type=str)
@click.option('--port',   'port',       default=8050, type=int)
# @click.option('--start-date','start_date', default=None, help="Project start date (YYYY-MM-DD) to convert durations into dates")

def dashboard(input_path, n_iters, seed, host, port):#, start_date):
    """Launch interactive ICSRA dashboard in Dash."""
    
    tasks = load_tasks(Path(input_path))
    proj  = Project(tasks, n_iters=n_iters, seed=seed)
    proj.simulate()
    serve_dashboard(proj, host=host, port=port) #, start_date=start_date)
