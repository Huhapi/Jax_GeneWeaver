from temporalio import workflow
from datetime import timedelta
from plugins.MSET.activities import MSETInput, MSETOutput, run_mset

@workflow.defn
class MSETWorkflow:
    def __init__(self):
        self.percent_complete = 0

    @workflow.query
    def status(self) -> int:
        return self.percent_complete

    @workflow.run
    async def run(self, input_data: MSETInput) -> MSETOutput:
        self.percent_complete = 25
        await workflow.sleep(2)
        self.percent_complete = 75
        result = await workflow.execute_activity(
            run_mset,
            input_data,
            start_to_close_timeout=timedelta(seconds=60)
        )
        self.percent_complete = 100
        return result

run_mset_workflow = MSETWorkflow.run