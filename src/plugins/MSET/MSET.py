import asyncio
import random
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List
import os

# Define a simple Response dataclass to wrap the result.
@dataclass
class Response:
    result: Any

class MSETTask:
    async def run(self, input_data: Dict[str, Any]) -> Response:

        # Get parameters from input_data
        num_trials = int(input_data.get("num_trials", 1000))
        file_path_1 = input_data.get("file_path_1")
        file_path_2 = input_data.get("file_path_2")
        representation = input_data.get("representation", "over").lower()  # "over" or "under"
        print_to_cli = input_data.get("print_to_cli", False)
        
        with open(file_path_1, "r") as f:
            content1 = f.read()
        with open(file_path_2, "r") as f:
            content2 = f.read()
        
        # If a background file is provided, read it.
        background_file_path = input_data.get("background_file_path")
        if background_file_path:
            with open(background_file_path, "r") as f:
                background_content = f.read()
            background_genes = sorted(set(self.extract_genes_from_gw(background_content)))
        else:
            background_genes = None
        
        # Extract gene lists from the file contents
        group_1_genes = self.extract_genes_from_gw(content1)
        group_2_genes = self.extract_genes_from_gw(content2)

        # print(group_1_genes)     
        # print(group_2_genes)     
   
        list_1_pre = sorted(set(group_1_genes))
        list_2_pre = sorted(set(group_2_genes))
        
        # Use the background file if provided; otherwise, use the pre gene lists as background.
        if background_genes is not None:
            list_1_background = background_genes
            list_2_background = background_genes
        else:
            list_1_background = list_1_pre
            list_2_background = list_2_pre
        
        missing_genes = set(list_1_pre) - set(list_1_background)
        # if missing_genes:
            # print("These gensets are missing in the background")
            # for gene in sorted(missing_genes):
            #     # print(gene)
            #     # print()
        
        # Compute the universe as the intersection of the two background sets
        universe = sorted(set(list_1_background).intersection(list_2_background))
        
        # Filter the pre lists to include only genes that are in the universe
        list_1 = sorted(set(list_1_pre).intersection(universe))
        list_2 = sorted(set(list_2_pre).intersection(universe))
        print(list_1)
        print(list_2)

        # Calculate sizes and the observed intersection size
        list_1_size = len(list_1)
        list_2_size = len(list_2)
        universe_size = len(universe)
        comp_intersect_size = len(set(list_1).intersection(list_2))
        
        # # Verify that the pre lists are subsets of their backgrounds
        # if not set(list_2_pre).issubset(set(list_2_background)):
        #     return Response(result="Error: list_2 not subset of its background")
        # if not set(list_1_pre).issubset(set(list_1_background)):
        #     return Response(result="Error: list_1 not subset of its background")
        
        # Run simulation trials: randomly sample genes from the universe and count intersection sizes.
        trials: List[int] = []
        for _ in range(num_trials):
            sample1 = set(random.sample(universe, list_1_size))
            sample2 = set(random.sample(universe, list_2_size))
            intersection_size = len(sample1.intersection(sample2))
            trials.append(intersection_size)
        
        # Sort trial results and count how many trials have an intersection size at least as high as observed.
        trials.sort()
        above = sum(1 for t in trials if t >= comp_intersect_size)
        
        # Compute the p-value based on the representation type.
        if representation == "over":
            pvalue = above / float(num_trials)
            alternative = "Greater"
            method = "Over"
        elif representation == "under":
            pvalue = (num_trials - above) / float(num_trials)
            alternative = "Less"
            method = "Under"
        else:
            return Response(result="Error: representation must be either 'over' or 'under'")
        
        # Create a histogram of the simulated intersection sizes.
        hist = dict(Counter(trials))
        
        # Prepare the output dictionary.
        mset_output = {
            "List 1 Size": list_1_size,
            "List 2 Size": list_2_size,
            "Universe Size": universe_size,
            "List 1 / Universe": list_1_size,
            "List 2 / Universe": list_2_size,
            "List 1/2 Intersect": comp_intersect_size,
            "Num Trials": num_trials,
            "Alternative": alternative,
            "Method": method,
            "Trials gt intersect": above,
            "P-Value": pvalue
        }
        
        # Optionally print the results to the CLI.
        if print_to_cli:
            print("\nMSET Output:")
            for key, value in mset_output.items():
                print(f"{key}: {value}")
            print("\nHistogram:")
            for key, value in sorted(hist.items()):
                print(f"{key}: {value}")
        
        # Return the computed results.
        return Response(result={"mset_output": mset_output, "histogram": hist})
    
    def extract_genes_from_gw(self, file_content: str) -> List[str]:
        """
        need to make thi better        """
        genes = []
        skip_chars = ("#", ":", "=", "+", "@", "%", "A", "!", "Q")
        for line in file_content.splitlines():
            line = line.strip()
            if not line or line.startswith(skip_chars):
                continue
            gene = line.split()[0]
            genes.append(gene)
        return genes
    
    def status(self) -> Response:

        @dataclass
        class Status:
            percent_complete: int
        return Response(result=Status(percent_complete=100))


if __name__ == "__main__":
    # Define your file paths.
    file_path_1 = os.path.abspath("../Jax_GeneWeaver/src/plugins/MSET/RATUS1")
    file_path_2 = os.path.abspath("../Jax_GeneWeaver/src/plugins/MSET/ratus2")
    background_file_path = os.path.abspath("../Jax_GeneWeaver/src/plugins/MSET/KEGGRattusnorvegicusBG.txt")
    
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
    task = MSETTask()
    result = asyncio.run(task.run(input_data))
    
    # Print the final result.
    print("Plugin result:")
    print(result.result)