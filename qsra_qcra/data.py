import pandas as pd
from pathlib import Path
from .task import Task

def load_tasks(path: Path):

    path = Path(path)

    if path.suffix in ('.xls', '.xlsx'):
        df = pd.read_excel(path)

    else:
        df = pd.read_csv(path)

    # columns needed to work    
    required = {
        'task_id','name',
        'a_dur','m_dur','b_dur',
        'a_cost','m_cost','b_cost',
        'dist_type','is_critical'
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f'Missing columns in input: {missing}')
    
    tasks = []

    for _, row in df.iterrows():

        # create a task object with all the required info
        tasks.append(Task(
            task_id=row['task_id'],
            name=row['name'],
            a_dur=float(row['a_dur']),
            m_dur=float(row['m_dur']),
            b_dur=float(row['b_dur']),
            a_cost=float(row['a_cost']),
            m_cost=float(row['m_cost']),
            b_cost=float(row['b_cost']),
            dist_type=row['dist_type'],
            is_critical=bool(row['is_critical'])
        ))

    return tasks
