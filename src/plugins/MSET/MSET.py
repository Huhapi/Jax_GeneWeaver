import random
import time
from collections import Counter
from dataclasses import asdict
from typing import Any, Dict, List, Optional
from ATS import ATS_Plugin
from plugins.api.geneSetRestAPI import fetchGeneSymbols_from_geneset
from utils.gene_helpers import extract_genes_from_gw
from plugins.MSET.schemas import Response, MSETOutput, MSETStatus
from plugins.MSET.simulation import run_trials   # Heavy simulation moved to its own module

class MSETTask(ATS_Plugin.implement_plugins):
    """
    A plugin for performing Modular Single-set Enrichment Test (MSET).
    MSET was developed to compare gene lists. From four character lists (gene_list1, gene_list2, background1, background2), 
    it computes a randomization-based p-value describing the likelihood that the intersect of gene_list1 and gene_list2 is underexpressed or overexpressed relative to randomness alone    
    """  

    def __init__(self):
        self._status = MSETStatus(percent_complete=0, message="Initializing", current_step="")

    async def run(self, input_data: Dict[str, Any]) -> Response:
        log = input_data.get("log")
        # Get parameters from input_data
        num_trials = int(input_data.get("num_trials", 1000))
        geneset_id_1 = input_data.get("geneset_id_1")  # Will be used if geneset ids are provided
        geneset_id_2 = input_data.get("geneset_id_2")  # Will be used if geneset ids are provided

        file_path_1 = input_data.get("file_path_1")
        file_path_2 = input_data.get("file_path_2")
        background_file_path_1 = input_data.get("background_file_path_1")
        background_file_path_2 = input_data.get("background_file_path_2")

        representation = input_data.get("representation", "over").lower()  # "over" or "under"
        print_to_cli = input_data.get("print_to_cli", False)

        self._update_status(percent=10, message="Retrieving gene sets", current_step="Loading data", log=log)

        # Retrieve gene set for group 1
        if geneset_id_1:
            group_1_genes = fetchGeneSymbols_from_geneset(geneset_id_1)
        elif file_path_1:
            with open(file_path_1, "r") as f:
                content1 = f.read()
            group_1_genes = extract_genes_from_gw(content1)
        else:
            return Response(result="Error: Provide either file_path_1 or geneset_id_1")

        # Retrieve gene set for group 2
        if geneset_id_2:
            group_2_genes = fetchGeneSymbols_from_geneset(geneset_id_2)
        elif file_path_2:
            with open(file_path_2, "r") as f:
                content2 = f.read()
            group_2_genes = extract_genes_from_gw(content2)
        else:
            return Response(result="Error: Provide either file_path_2 or geneset_id_2")

        self._update_status(percent=30, message="Processing background gene sets", current_step="Background Processing", log=log)

        # Process background gene sets if provided
        if background_file_path_1:
            with open(background_file_path_1, "r") as f:
                background_content_1 = f.read()
            background_genes_1 = sorted(set(extract_genes_from_gw(background_content_1)))
        else:
            background_genes_1 = None

        if background_file_path_2:
            with open(background_file_path_2, "r") as f:
                background_content_2 = f.read()
            background_genes_2 = sorted(set(extract_genes_from_gw(background_content_2)))
        else:
            background_genes_2 = None

        list_1_pre = sorted(set(group_1_genes))
        list_2_pre = sorted(set(group_2_genes))
        # Use the background file if provided; otherwise, use the pre gene lists as background.
        if background_genes_1 is not None:
            list_1_background = background_genes_1
        else:
            list_1_background = list_1_pre

        if background_genes_2 is not None:
            list_2_background = background_genes_2
        else:
            list_2_background = list_2_pre

        # Uncomment the following if you want to check for missing genes
        # missing_genes = set(list_1_pre) - set(list_1_background)
        # if missing_genes:
        #     print("These genes are missing in the background:")
        #     for gene in sorted(missing_genes):
        #         print(gene)
        
        # Compute the universe as the intersection of the two background sets
        universe = sorted(set(list_1_background).intersection(list_2_background))
        # Filter the pre lists to include only genes that are in the universe
        list_1 = sorted(set(list_1_pre).intersection(universe))
        list_2 = sorted(set(list_2_pre).intersection(universe))

        # Calculate sizes and the observed intersection size
        list_1_size = len(list_1)
        list_2_size = len(list_2)
        universe_size = len(universe)
        comp_intersect_size = len(set(list_1).intersection(list_2))
        
        # Uncomment these checks if you want to enforce that pre gene lists are subsets of their backgrounds:
        # if not set(list_2_pre).issubset(set(list_2_background)):
        #     return Response(result="Error: list_2 not subset of its background")
        # if not set(list_1_pre).issubset(set(list_1_background)):
        #     return Response(result="Error: list_1 not subset of its background")
        
        self._update_status(percent=50, message="Randomly sampling genes", current_step="Running trials", log=log)

        # Run trials using the simulation function
        trials: List[int] = run_trials(universe, list_1_size, list_2_size, num_trials, mode='auto', threshold=1000)

        self._update_status(percent=80, message="Calculating results", current_step="Analysis", log=log)

        # Count the number of trials with intersection sizes at least as high as the observed
        above = sum(1 for t in trials if t >= comp_intersect_size)

        # Compute the p-value based on the representation type
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
        
        # Histogram of the intersection sizes.
        hist = dict(Counter(trials))
        
        # Prepare the output dictionary.
        mset_output = MSETOutput(
            list_1_size=list_1_size,
            list_2_size=list_2_size,
            universe_size=universe_size,
            list_1_universe_ratio=list_1_size / universe_size,
            list_2_universe_ratio=list_2_size / universe_size,
            intersection_size=comp_intersect_size,  
            num_trials=num_trials,
            alternative=alternative,
            method=method,
            trials_gt_intersect=above,
            p_value=pvalue,
            histogram=hist
        )
        
        self._update_status(percent=100, message="Analysis complete", current_step="Completed", log=log)

        if print_to_cli:
            print("\nMSET Output:")
            for key, value in asdict(mset_output).items():
                print(f"{key}: {value}")
            print("\nHistogram:")
            for key, value in sorted(hist.items()):
                print(f"{key}: {value}")
        
        # Return the computed results.
        return Response(result={"mset_output": mset_output, "histogram": hist, "info": {"task_type": "mset_analysis"}})
    
    def _update_status(self, percent: int, message: str, current_step: str, log: Optional[bool] = None) -> None:
        self._status.percent_complete = percent
        self._status.message = message
        self._status.current_step = current_step
        if log:
            print(f"[STATUS] {percent}% - {message} ({current_step})")  
    
    def status(self) -> Response:
        """
        Returns the current status of the MSET task.

        Returns:
            Response: Object containing the progress and message.
        """
        return Response(result=self._status)