# Unit Testing for MSET tool
# Backend Geneuses Daniel, Anushka, Harshit, Kishan
import asyncio
from plugins.MSET import MSET
import os

if __name__ == "__main__":
    # Define your file paths.
    file_path_1 = os.path.abspath("../Jax_GeneWeaver/src/tests/unit/MSET_tests/RATUS1")
    file_path_2 = os.path.abspath("../Jax_GeneWeaver/src/tests/unit/MSET_tests/ratus2")
    background_file_path = os.path.abspath("../Jax_GeneWeaver/src/tests/unit/MSET_tests/KEGGRattusnorvegicusBG.txt")
    
    # Prepare the input data. Notice that we include the background_file_path.
    input_data = {
        "num_trials": 1000,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path": background_file_path,
        # "representation": "over",  # Optional; if omitted, it defaults to "over"
        "print_to_cli": True
    }
    
    # Create an instance of the plugin task and run it asynchronously.
    task = MSET.MSETTask()
    result = asyncio.run(task.run(input_data))
    
    # Print the final result.
    print("Plugin result:")
    print(result.result)