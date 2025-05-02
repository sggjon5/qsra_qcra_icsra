import pandas as pd
from pathlib import Path
from .task import Task

def load_tasks(path: Path):
    """
    Load task definitions from a CSV or Excel file and return a list of Task objects.

    Parameters:
    path (Path): Path to the input file (CSV, XLS, or XLSX)

    Returns:
    List[Task]: List of Task instances populated with data from the file
    """

    # make sure path is right object type
    path = Path(path)

    # if excel, read as that, otherwise read as csv, could maybe functionise this if we use it elsewhere in the future.
    if path.suffix in ('.xls', '.xlsx'):
        df = pd.read_excel(path)

    else:
        df = pd.read_csv(path)


    # columns required for a valid input  
    required = {
        'task_id','name',
        'a_dur','m_dur','b_dur',
        'a_cost','m_cost','b_cost',
        'dist_type','is_critical'
    }

    # identify missing columns  and raise anerror if any missing
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f'Missing columns in input: {missing}')
    
    # empty list to collect Task objects
    tasks = []

    # for every row in the dataframe
    for _, row in df.iterrows():

        # create a task object with all the required info
        tasks.append(Task(
            task_id=row['task_id'],
            name=row['name'],
            a_dur=float(row['a_dur']), # optimistic duration
            m_dur=float(row['m_dur']), # most likely duration
            b_dur=float(row['b_dur']), # pessemistic duration
            a_cost=float(row['a_cost']), # optimistic cost
            m_cost=float(row['m_cost']), # most likely cost
            b_cost=float(row['b_cost']), # pessimistic cost
            dist_type=row['dist_type'], # distribution type
            is_critical=bool(row['is_critical']) # critial path flag, this may be needed to also allow for yes and no?
        ))

    # reutn list of task objects for use in project sim
    return tasks
