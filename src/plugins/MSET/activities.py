# ----------------------------
# File: plugins/MSET/activities.py
# ----------------------------

from dataclasses import dataclass
from temporalio import activity
from plugins.MSET.MSET import MSETTask, Response

@dataclass
class MSETInput:
    file_path_1: str
    file_path_2: str
    representation: str = "over"
    num_trials: int = 1000
    print_to_cli: bool = False
    background_file_path: str = ""

@dataclass
class MSETOutput:
    summary: str
    pvalue: float

@activity.defn
async def run_mset(input_data: MSETInput) -> MSETOutput:
    # 🔗 Use your actual plugin logic from MSET.py
    task = MSETTask()
    result: Response = await task.run(input_data.__dict__)

    # 🧼 Basic output formatting (or extend as needed)
    pval = result.result["mset_output"]["P-Value"]
    return MSETOutput(
        summary="MSET Run Complete",
        pvalue=pval
    )