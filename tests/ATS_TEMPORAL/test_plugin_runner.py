import asyncio
import os
from temporalio.client import Client
from plugins.MSET.activities import MSETInput
from plugins.MSET.workflows import run_mset_workflow

async def monitor_status(client, workflow_id: str):
    while True:
        handle = client.get_workflow_handle(workflow_id)
        percent = await handle.query("status")
        print(f"Workflow {workflow_id} status: {percent}%")
        if percent == 100:
            break
        await asyncio.sleep(2)

async def main():
    if os.environ.get("USE_TEMPORAL") != "1":
        print("This demo requires Temporal. Set USE_TEMPORAL=1.")
        return

    client = await Client.connect("localhost:7233")

    jobs = [
        MSETInput("data/1.gw", "data/2.gw", num_trials=200),
        MSETInput("data/3.gw", "data/4.gw", num_trials=453),
    ]

    tasks = []
    for i, job in enumerate(jobs):
        workflow_id = f"mset-job-{i+1}"
        handle = await client.start_workflow(
            run_mset_workflow,
            job,
            id=workflow_id,
            task_queue="mset-tasks"
        )
        tasks.append((workflow_id, handle))

    await asyncio.gather(*[monitor_status(client, wid) for wid, _ in tasks])

    print("\n=== All workflows complete ===")
    for workflow_id, handle in tasks:
        result = await handle.result()
        print(f"{workflow_id} Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
