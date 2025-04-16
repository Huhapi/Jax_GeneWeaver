"""
Tool Class Definition for Boolean Algebra. See service.py for the heavy lifting.
"""
import json
from plugins.BooleanAlgebra import service
from ATS import ATS_Plugin
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class Response:
    result: Any

@dataclass
class BooleanAlgebraStatus:
    message: str

class BooleanAlgebra(ATS_Plugin.implement_plugins):
    
    # Name of the tool
    name = "BooleanAlgebra"

    # === Styling Constants ===
    COLORS = ['#58D87E', '#588C7E', '#F2E394', '#1F77B4', '#F2AE72', '#F2AF28', 'empty', '#D96459',
              '#D93459', '#5E228B', '#698FC6']
    TT = ['Mus musculus', 'Homo sapiens', 'Rattus norvegicus', 'Danio rerio', 'Drosophila melanogaster',
          'Macaca mulatta', 'empty', 'Caenorhabditis elegans', 'Saccharomyces cerevisiae', 'Gallus gallus',
          'Canis familiaris']
    BG = ['#fae4db', '#f9fac5', '#b5faf5', '#fae3e9', '#f5fee1', '#f4dfff', '#78c679', '#41b6c4', '#7bccc4',
          '#8c96c6', '#fc8d59']
    BORDERS = ['#eeb44f', '#d7c000', '#44fcf7', '#fca5b7', '#8fcb0a', '#b4d1fb', '#41ab5d', '#1d91c0',
               '#4eb3d3', '#8c6bb1', '#ef6548']
    # ===

    def __init__(self, *args, **kwargs):
        self.name = "BooleanAlgebra"
        self._parameters = {}
        self._results = {}
        self._gsids = []
        self.urlroot = ''
        self._status = BooleanAlgebraStatus(
            message="Initialized Boolean Algebra"
        )

    def _update_status(self, message: str) -> None:
        self._status.message = message

    async def run(self, input_data: Dict[str, Any]) -> Response:
        # Extract parameters from input_data
        self._parameters = {
            'BooleanAlgebra_Relation': input_data.get('relation', 'intersect'),
            'at_least': input_data.get('at_least', 2)
        }
        
        # Extract geneset IDs from input_data
        self._gsids = input_data.get('geneset_ids', [])
        
        # Get parameters for tool run
        relation = self._parameters['BooleanAlgebra_Relation'].lower()
        at_least = self._parameters['at_least']
        
        # Strip 'GS' from gsids arguments to get ode gene ids
        geneset_ids = [g[2:] for g in self._gsids]
        
        self._update_status("Boolean Algebra Tool Running")
        
        # Results we know on submission
        result_dict = {
            # ---Styling Constants
            # Tool Tip
            'tt': self.TT,
            # Box Colors
            'colors': self.COLORS,
            # Background Colors
            'bg': self.BG,
            # Border Colors
            'borders': self.BORDERS,
            # ---Submission Info
            # Minimum number of gene sets
            'at_least': at_least,
            # Relation name -> Union, Inter., or Except
            'type': relation.title(),
            # Number of genesets in the current run of the tool
            'numGS': len(geneset_ids),
        }
        
        # Species for tool results page
        all_species_short, all_species_full = service.get_all_geneweaver_species_for_boolean()
        # Species for tool run
        species_in_genesets = service.get_species_in_genesets(geneset_ids)
        
        self._update_status("Fetching homolog data")
        
        # Get gene data
        homolog_data = service.get_homologs_for_geneset(geneset_ids, species_ids=species_in_genesets)
        bool_results = service.group_homologs(homolog_data, species_in_genesets)

        # Geneset Ids returned in the query
        result_geneset_ids = list(set([item[4] for item in homolog_data]))
        
        # Add tool results to result dict
        result_dict.update({
            # Number of genesets in the current run of the tool
            'numGS': len(geneset_ids),
            # Number of species in the current run of the tool
            'numSpecies': len(species_in_genesets),
            # All species for the header
            'all_species': all_species_short,
            # Like all species, but full name
            'all_species_full': all_species_full,
            'gsids': result_geneset_ids,
            'bool_results': bool_results,
        })

    
        # Initialize intersection_sizes as empty
        intersection_sizes = {}
        
        if relation != 'union':
            self._update_status("Computing intersection")
            # In case of Intersect, create dictionary of only
            # elements in bool_results with > than intersect
            intersection_sizes = service.intersect(bool_results, at_least)
            result_dict['intersect_results'] = intersection_sizes

            if relation == 'except':
                self._update_status("Computing except operation")
                # If except then perform union minus the union of the intersections.
                # For GS A, B, C = (A U B U C)-((A N B) U (A N C) U (B N C))
                result_dict['bool_except'] = service.bool_except(bool_results)

        self._update_status("Clustering genes")
        # Cluster result genes based on shared and unique genes per species
        # This will be placed in a d3 graph on the site
        #
        # it will report:
        # A. the number of genes unique to each species
        # B. the number of genes/species/intersection
        # B. the number of genes per species
        bool_cluster_raw = service.cluster_genes(homolog_data, species_in_genesets)
        
        # Convert bool_cluster to only include counts instead of actual gene values
        bool_cluster_counts = {}
        for species_id, data in bool_cluster_raw.items():
            bool_cluster_counts[species_id] = {
                'unique': len(data['unique']),
                'species': len(data['species'])
            }
            
            # Calculate the correct intersection count based on intersection_sizes
            if intersection_sizes:
                # Count the total number of genes in all intersection groups
                total_intersection_genes = 0
                for size, group in intersection_sizes.items():
                    # Count the number of genes in each group
                    for gene_id, gene_data in group.items():
                        total_intersection_genes += 1
                
                # Set the intersection count for this species
                bool_cluster_counts[species_id]['intersection'] = total_intersection_genes
            else:
                # If no intersection_sizes (e.g., for union operation), use the raw intersection count
                bool_cluster_counts[species_id]['intersection'] = len(data['intersection'])
        
        result_dict['bool_cluster'] = bool_cluster_counts

        # Update the results of the tool
        self._results.update(result_dict)

        self._update_status("Boolean Algebra Tool Completed")
        
        # Return the response with serializable data
        return Response(result={"boolean_algebra_output": result_dict, "info": {"task_type": "boolean_algebra"}})

    def status(self) -> Response:
        return Response(result=self._status)

