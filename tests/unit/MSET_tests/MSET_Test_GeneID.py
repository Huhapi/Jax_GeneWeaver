import asyncio
import os
from plugins.MSET import MSET

async def monitor_status(task, interval=2):
    """
    """
    while True:
        status = task.status().result
        print(f"[STATUS] {status.percent_complete}% - {status.message} ({status.current_step})")
        await asyncio.sleep(interval)

async def run_task_with_monitoring():
    current_dir = os.path.dirname(__file__)
    geneset_id_1 = 1 ## add relavent geneid
    geneset_id_2 = 1
    background_file_path = os.path.join(current_dir, "KEGGRattusnorvegicusBG.txt")

    input_data = {
        "num_trials": 90000,
        "geneset_id_1": geneset_id_1,
        "geneset_id_2": geneset_id_2,
        "background_file_path_1": background_file_path,
        "background_file_path_2": background_file_path,
        "print_to_cli": True
    }

    task = MSET.MSETTask()
    
    task_future = asyncio.create_task(task.run(input_data))
    status_monitor = asyncio.create_task(monitor_status(task))

    result = await task_future
    status_monitor.cancel() 

    print("\nPlugin result:")
    print(result.result)

if __name__ == "__main__":
    asyncio.run(run_task_with_monitoring())