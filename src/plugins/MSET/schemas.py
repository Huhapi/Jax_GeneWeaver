from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class Response:
    result: Any

@dataclass
class MSETOutput:
    list_1_size: int
    list_2_size: int
    universe_size: int
    list_1_universe_ratio: float
    list_2_universe_ratio: float
    intersection_size: int
    num_trials: int
    alternative: str
    method: str
    trials_gt_intersect: int
    p_value: float
    histogram: Dict[int, int]

@dataclass
class MSETStatus:
    percent_complete: int
    message: str
    current_step: str
    genes_processed: int = 0
    trials_completed: int = 0
    time_elapsed: Optional[float] = None
    time_remaining: Optional[float] = None