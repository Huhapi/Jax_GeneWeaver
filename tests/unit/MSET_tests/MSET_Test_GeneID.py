import asyncio
import os
import matplotlib.pyplot as plt
from plugins.MSET import MSET

async def monitor_status(task, interval=2):
    """
    Periodically prints the status of the task.
    """
    while True:
        status = task.status().result
        print(f"[STATUS] {status.percent_complete}% - {status.message} ({status.current_step})")
        await asyncio.sleep(interval)

async def run_task_with_monitoring():
    current_dir = os.path.dirname(__file__)
    geneset_id_1 = 233106  # Add relevant gene ID
    geneset_id_2 = 233325
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

    # Plotting histogram from result
    histogram = result.result.get("histogram")
    if isinstance(histogram, dict):
        x = list(histogram.keys())
        y = list(histogram.values())

        plt.bar(x, y, width=0.7, edgecolor='black')
        plt.title("MSET Simulation Result Histogram")
        plt.xlabel("Intersection Size")
        plt.ylabel("Frequency")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
    else:
        print("⚠️ Histogram data not found or not in expected format.")

if __name__ == "__main__":
    asyncio.run(run_task_with_monitoring())