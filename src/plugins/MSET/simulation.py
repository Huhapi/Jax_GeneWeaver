import random
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict

def run_trial(universe: List[str], list_1_size: int, list_2_size: int) -> int:
    """
    Perform a trial by randomly sampling genes from the universe for both lists,
    and return the intersection size.
    """
    sample1 = set(random.sample(universe, list_1_size))
    sample2 = set(random.sample(universe, list_2_size))
    return len(sample1.intersection(sample2))

def run_trials_basic(universe: List[str], list_1_size: int, list_2_size: int, num_trials: int) -> List[int]:
    """
    Run trials sequentially.
    Returns a sorted list of trial intersection sizes.
    """
    trials = []
    for _ in range(num_trials):
        trials.append(run_trial(universe, list_1_size, list_2_size))
    trials.sort()
    return trials

def run_trials_parallel(universe: List[str], list_1_size: int, list_2_size: int, num_trials: int, workers: int = None) -> List[int]:
    """
    Run trials using parallel processing with ProcessPoolExecutor.
    Returns a sorted list of trial intersection sizes.
    
    Parameters:
      - workers: Optional; number of worker processes to use. If None, the executor
                 will choose the default of your cpu
    """
    trials = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_trial, universe, list_1_size, list_2_size) for _ in range(num_trials)]
        for future in as_completed(futures):
            trials.append(future.result())
    trials.sort()
    return trials

def run_trials(universe: List[str], list_1_size: int, list_2_size: int,
               num_trials: int, mode: str = 'auto', workers: int = None,
               threshold: int = 1000) -> List[int]:
    """
    Run trials using one of two methods: basic (sequential) or parallel.
    
    Parameters:
      - mode: 'basic', 'parallel', or 'auto'. 
              If 'auto', the function will choose parallel execution if num_trials >= threshold.
      - workers: Number of parallel worker processes (if using parallel mode).
      - threshold: The number of trials above which the function will automatically choose parallel execution.
    
    Returns:
      A sorted list of trial intersection sizes.
    """
    #could have any check for auto(this is exxtendable)
    if mode == 'auto':
        if num_trials >= threshold:
            return run_trials_parallel(universe, list_1_size, list_2_size, num_trials, workers=workers)
        else:
            return run_trials_basic(universe, list_1_size, list_2_size, num_trials)
    elif mode == 'parallel':
        return run_trials_parallel(universe, list_1_size, list_2_size, num_trials, workers=workers)
    else:
        return run_trials_basic(universe, list_1_size, list_2_size, num_trials)