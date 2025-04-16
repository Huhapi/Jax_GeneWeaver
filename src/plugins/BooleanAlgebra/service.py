"""
Service namespace for the Boolean Algebra tool
"""
import collections

from plugins.api.geneSetRestAPI import get_geneset_data, fetchSpecies


def get_all_geneweaver_species():
    return fetchSpecies()


def get_all_geneweaver_species_for_boolean():
    all_species_short = {}
    all_species_full = {}
    species_data = fetchSpecies()
    for species in species_data:
        all_species_short[species[0]] = "".join(item[0] for item in species[1].split())
        all_species_full[species[0]] = species[1]
    return all_species_short, all_species_full


# GET_HOMOLOGS_SQL = '''SELECT hom.hom_source_id, g.ode_gene_id, g.ode_ref_id, g.sp_id, gv.gs_id, gs.gs_abbreviation
#                             FROM gene g NATURAL JOIN geneset_value gv NATURAL
#                             JOIN geneset gs LEFT JOIN
#                               (SELECT ode_gene_id, hom_source_id 
#                                     FROM homology 
#                                     WHERE hom_source_name = 'Homologene' 
#                                     AND hom_source_id IN
#                                       (SELECT hom_source_id 
#                                           FROM homology h, geneset_value gv2
#                                           WHERE h.ode_gene_id = gv2.ode_gene_id
#                                           AND gv2.gs_id IN {0}
#                                       )
#                                     AND sp_id IN ({1})
#                               ) hom
#                               ON g.ode_gene_id = hom.ode_gene_id
#                             WHERE gv.gs_id IN {0}
#                             AND g.gdb_id = 7 
#                             AND g.ode_pref = TRUE
#                               ORDER BY hom.hom_source_id, gv.gs_id'''


# def get_homologs_for_geneset(cursor, geneset_ids, species_ids=None):
#     """

#     :param cursor:
#     :param geneset_ids:
#     :param species_ids:
#     :return:
#     """
#     species_ids = species_ids or get_species_in_genesets(cursor, geneset_ids)
#     sql = GET_HOMOLOGS_SQL.format(tuple(geneset_ids), ",".join(str(sid) for sid in species_ids))
#     cursor.execute(sql)
#     results = cursor.fetchall()
#     cursor.close()
#     return results

def get_homologs_for_geneset(geneset_ids, species_ids=None):
    """
    Get gene data for genesets, focusing on same-species gene matching.
    Instead of fetching homologs, we'll just use the ode_gene_id for matching.
    
    :param geneset_ids: List of geneset IDs
    :param species_ids: List of species IDs (optional)
    :return: List of gene data tuples
    """
    species_ids = species_ids or get_species_in_genesets(geneset_ids)
    gene_data = []
    
    # Create a dictionary to store genes by species
    genes_by_species = {}
    
    # First, collect all genes by species
    for gs_id in geneset_ids:
        geneset_info = get_geneset_data(gs_id)
        if 'object' in geneset_info and 'geneset_values' in geneset_info['object']:
            species_id = geneset_info["object"]["geneset"]["species_id"]
            
            if species_id not in genes_by_species:
                genes_by_species[species_id] = []
                
            for gene_value in geneset_info['object']['geneset_values']:
                gene_id = gene_value.get('ode_gene_id')
                if gene_id:
                    # Create a tuple with (gene_id, gene_id, ref_id, species_id, gs_id)
                    # We use gene_id twice to maintain the same structure as before
                    gene_tuple = (
                        gene_id,  # Using gene_id as the key instead of hom_id
                        gene_id,  # The actual gene ID
                        gene_value.get('ode_ref_id', ''),
                        species_id,
                        gs_id
                    )
                    genes_by_species[species_id].append(gene_tuple)
    
    # Now, for each species, add the genes to the result
    for species_id, genes in genes_by_species.items():
        gene_data.extend(genes)
    
    return gene_data

def group_homologs(gene_data, species_ids):
    """
    Group genes by their ID for same-species matching.
    
    :param gene_data: The list of gene data tuples
    :param species_ids: A list of all species ids
    :return: Dictionary of grouped genes
    """
    bool_results = {}
    
    # Group genes by their ID
    for gene in gene_data:
        key = gene[0]  # Use the gene ID as the key
        
        # If we only have one species, use the gene ID directly
        if len(species_ids) == 1:
            key = gene[1]
        
        current_val = bool_results.get(key, [])
        current_val.append(gene[1:5])  # Append the rest of the gene data
        bool_results[key] = current_val
    
    # Sort the results by the number of genes in each group
    bool_results = {i[0]: i[1] for i in sorted(list(bool_results.items()), key=lambda t: len(t[1][0]))}
    
    return bool_results

def get_grouped_homologs_for_genesets(geneset_ids, species_ids=None, gene_data=None):
    """
    Get grouped genes for genesets, focusing on same-species matching.
    
    :param geneset_ids: List of geneset IDs
    :param species_ids: List of species IDs (optional)
    :param gene_data: Pre-fetched gene data (optional)
    :return: Dictionary of grouped genes
    """
    species_ids = species_ids or get_species_in_genesets(geneset_ids)
    gene_data = gene_data or get_homologs_for_geneset(geneset_ids, species_ids)
    return group_homologs(gene_data, species_ids)

def get_species_in_genesets(geneset_ids):
    species_ids = set()
    for gs_id in geneset_ids:
        gene_data = get_geneset_data(gs_id)
        species_ids.add(gene_data["object"]["geneset"]["species_id"])
    return list(species_ids)

def cluster_genes(gene_data, species_ids):
    """
    Cluster result genes based on shared and unique genes per species.
    This will be placed in a d3 graph on the site.

    It will report:
    A. the number of genes unique to each species
    B. the number of genes/species/intersection
    C. the number of genes per species
    
    :param gene_data: The list of gene data tuples
    :param species_ids: List of species IDs
    :return: Dictionary of genes per geneset
    """
    genes_per_geneset = {sp: {'unique': [], 'intersection': [], 'species': []} for sp in species_ids}

    # First, collect all genes by species
    for gene in gene_data:
        species_id = gene[3]  # Get the species ID
        gene_id = gene[1]     # Get the gene ID
        if species_id in genes_per_geneset:  # Only process if we know about this species
            genes_per_geneset[species_id]['species'].append(gene_id)

    # Find unique genes for each species
    gene_comparision_list_all = []
    gene_comparision_list_sp = []
    for outer_species_id in species_ids:
        for inner_species_id in species_ids:
            if outer_species_id != inner_species_id:
                gene_comparision_list_all.extend(genes_per_geneset[inner_species_id]['species'])
            else:
                gene_comparision_list_sp.extend(genes_per_geneset[inner_species_id]['species'])
        genes_per_geneset[outer_species_id]['unique'].extend(
            list(set(gene_comparision_list_sp) - set(gene_comparision_list_all)))
        del gene_comparision_list_all[:]
        del gene_comparision_list_sp[:]

    # Find intersection genes (genes that appear in multiple species)
    gene_intersection_list = []
    for i in range(0, len(species_ids)):
        for j in range(0, len(genes_per_geneset[species_ids[i]]['species'])):
            for k in range(0, len(species_ids)):
                if i != k:
                    if genes_per_geneset[species_ids[i]]['species'][j] in genes_per_geneset[species_ids[k]]['species']:
                        gene_intersection_list.append(genes_per_geneset[species_ids[i]]['species'][j])
        genes_per_geneset[species_ids[i]]['intersection'].extend(gene_intersection_list)
        del gene_intersection_list[:]

    return genes_per_geneset


def intersect(bool_results, at_least=2):
    """
    Find genes that appear in at least the specified number of genesets.
    
    :param bool_results: Dictionary of grouped genes
    :param at_least: Minimum number of genesets a gene must appear in
    :return: Dictionary of intersection results
    """
    bool_intersect = collections.defaultdict(dict)
    intersect_results = {key: value for key, value in bool_results.items() if len(value) >= int(at_least)}

    # Create groups of intersection, first creating
    # a backwards array of values
    compare = collections.defaultdict(list)
    gs_array = []
    gs_list = 'empty'
    for key, value in intersect_results.items():
        for i in range(0, len(value)):
            gs_array.append(str(value[i][3]))  # Add geneset ID
            gs_list = "|".join(gs_array)
        compare[gs_list].append(key)
        del gs_array[:]

    # make the groups numbered 1 - n
    i = 0
    for key, value in compare.items():
        for j in range(0, len(value)):
            local_array = []
            for k, v in intersect_results.items():
                del local_array[:]
                if int(k) == int(value[j]):
                    for m in range(0, len(v)):
                        local_array.append(str(v[m][3]))
                        temp = "|".join(local_array)
                    if str(temp) == str(key):
                        bool_intersect[i][value[j]] = v
        i += 1

    intersection_sizes = {}
    for key, value in bool_intersect.items():
        for k in value:
            if value[k]:
                if len(value[k]) not in intersection_sizes:
                    intersection_sizes[len(value[k])] = value
                else:
                    intersection_sizes[len(value[k])].update(value)

    return intersection_sizes


def bool_except(bool_results):
    """
    Find genes that appear in only one geneset (not in intersections).
    
    :param bool_results: Dictionary of grouped genes
    :return: Dictionary of except results
    """
    bool_except = collections.defaultdict(dict)
    intersects = {key: value for key, value in bool_results.items() if len(value) >= int(2)}

    # make a dict of all values in the except list
    except_results = {key: value for key, value in bool_results.items() if key not in intersects}

    # We need to re-sort this list so that genesets are
    # grouped together
    compare = collections.defaultdict(list)
    for key, value in except_results.items():
        compare[value[0][3]].append(key)

    # make the groups numbered 1 - n, this is easier than
    # the intersect case because we do not need to take
    # into account a list
    i = 0
    for key, value in compare.items():
        for j in range(0, len(value)):
            for k, v in except_results.items():
                if int(k) == int(value[j]):
                    bool_except[i][value[j]] = v
        i += 1
    return bool_except
