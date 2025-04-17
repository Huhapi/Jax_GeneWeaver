# Unit Testing for MSET tool
# Backend Geneuses Daniel, Anushka, Harshit, Kishan
import asyncio
from plugins.MSET import MSET
import os

def edge_case_MSET_test():
    """
    Testing a p value of one case for MSET.

    """
    current_dir = os.path.dirname(__file__)

    file_path_1 = os.path.join(current_dir, "ptest_ratus_1")  
    file_path_2 = os.path.join(current_dir, "ptest_ratus_2")
    background_file_path = os.path.join(current_dir, "ptest_ratus_bg")
    
    input_data = {
        "num_trials": 50,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path_1": background_file_path,
        "background_file_path_2": background_file_path,
        # "representation": "over",  # Optional; if omitted, it defaults to "over"
        "print_to_cli": True,
        "log":True #optional for showing the current status
    }

    # Create an instance of the plugin task and run it asynchronously.
    task = MSET.MSETTask()
    result = asyncio.run(task.run(input_data))
    
    # Print the final result.
    print("Plugin result:")
    print(result.result)

def mid_case_MSET_test():
    """
    Testing a p value of one case for MSET.

    """
    current_dir = os.path.dirname(__file__)

    file_path_1 = os.path.join(current_dir, "ptest_half_1")  
    file_path_2 = os.path.join(current_dir, "ptest_half_2")
    background_file_path = os.path.join(current_dir, "ptest_half_bg")
    
    input_data = {
        "num_trials": 50,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path_1": background_file_path,
        "background_file_path_2": background_file_path,
        # "representation": "over",  # Optional; if omitted, it defaults to "over"
        "print_to_cli": True,
        "log":True #optional for showing the current status
    }

    # Create an instance of the plugin task and run it asynchronously.
    task = MSET.MSETTask()
    result = asyncio.run(task.run(input_data))
    
    # Print the final result.
    print("Plugin result:")
    print(result.result)



def first_run_check():
    # This fetches the current directory and backtracks the file paths from there, please dont modify 
    current_dir = os.path.dirname(__file__)

    file_path_1 = os.path.join(current_dir, "RATUS1")  # 233106 • KEGG Geneset - "Apoptosis" pathway genes
    file_path_2 = os.path.join(current_dir, "ratus2")  # https://geneweaver.org/api/docs#/genesets/get_geneset_api_genesets__geneset_id__get 233325
    background_file_path = os.path.join(current_dir, "KEGGRattusnorvegicusBG.txt")
    
    # Prepare the input data. Notice that we include the background_file_path.
    input_data = {
        "num_trials": 1000,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path_1": background_file_path,
        "background_file_path_2": background_file_path,
        # "representation": "over",  # Optional; if omitted, it defaults to "over"
        "print_to_cli": True,
        "log":True #optional for showing the current status
    }
    
    # Create an instance of the plugin task and run it asynchronously.
    task = MSET.MSETTask()
    result = asyncio.run(task.run(input_data))
    
    # Print the final result.
    print("Plugin result:")
    print(result.result)

if __name__ == "__main__":
    mid_case_MSET_test()
    #edge_case_MSET_test()