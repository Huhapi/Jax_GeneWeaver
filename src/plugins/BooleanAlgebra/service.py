"""
Service namespace for the Boolean Algebra tool
"""
import collections
from src.utils.geneSetRestAPI import fetchGeneSets, fetchSpecies


# def get_all_geneweaver_species(cursor):
#     """

#     :return: list of tuples sp_id, sp_name
#     """
#     # TODO: Use sqlalchemy for this relation
#     cursor.execute(SELECT_ALL_SPECIES_SQL)
#     result = cursor.fetchall()
#     cursor.close()
#     return result
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
    species_ids = species_ids or get_species_in_genesets(geneset_ids)
    homolog_data = []
    for gs_id in geneset_ids:
        gene_data = fetchGeneSets(gs_id)
        if 'homologs' in gene_data:
            for homolog in gene_data['homologs']:
                homolog_tuple = (
                    homolog.get('hom_source_id'),
                    homolog.get('ode_gene_id'),
                    homolog.get('ode_ref_id'),
                    homolog.get('sp_id'),
                    gs_id
                )
                homolog_data.append(homolog_tuple)
    return homolog_data

def group_homologs(homologs, species_ids):
    """

    :param homologs: The tuple of tuples returned by cursor.fetchall() on the homolog query.
    :param species_ids: A list of all species ids
    :return:
    """
    bool_results = {}
    for homolog in homologs:
        key = homolog[0]
        if len(species_ids) == 1:
            key = homolog[1]
        elif not homolog[0]:
            key = -1*homolog[1]
        current_val = bool_results.get(key, [])
        current_val.append(homolog[1:5])
        bool_results[key] = current_val
    bool_results = {i[0]: i[1] for i in sorted(list(bool_results.items()), key=lambda t: len(t[1][0]))}
    return bool_results


def get_grouped_homologs_for_genesets(geneset_ids, species_ids=None, homolog_data=None):
    """

    :param geneset_ids:
    :param species_ids:
    :param homolog_data:
    :return:
    """
    species_ids = species_ids #or get_species_in_genesets(cursor, geneset_ids)
    homolog_data = homolog_data or get_homologs_for_geneset(geneset_ids, species_ids)
    return group_homologs(homolog_data, species_ids)


# def get_species_in_genesets(cursor, geneset_ids):
#     """
#     Get a unique list of species ids found in the genesets ids provided
#     :param cursor:
#     :param geneset_ids:
#     :return:
#     """
#     species_ids = []
#     for g_id in geneset_ids:
#         cursor.execute('''SELECT DISTINCT sp_id FROM production.geneset WHERE gs_id=%s''' % g_id, )
#         res = cursor.fetchall()
#         for r in res:
#             species_ids.append(int(r[0]))
#     return list(set(species_ids))

def get_species_in_genesets(geneset_ids):
    species_ids = set()
    for gs_id in geneset_ids:
        gene_data = fetchGeneSets(gs_id)
        species_ids.append(gene_data['species'])
    return list(species_ids)

def cluster_genes(homolog_data, species_ids):
    """
    Cluster result genes based on shared and unique genes per species
    This will be placed in a d3 graph on the site

    It will report:
    A. the number of genes unique to each species
    B. the number of genes/species/intersection
    C. the number of genes per species
    :param homolog_data:
    :param species_ids:
    :return:
    """
    genes_per_geneset = {sp: {'unique': [], 'intersection': [], 'species': []} for sp in species_ids}

    for homolog in homolog_data:
        genes_per_geneset[homolog[3]]['species'].append(homolog[0])

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

    # Loop through this set to find all genes that appear in another species
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

    :param bool_results:
    :param at_least:
    :return:
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
            gs_array.append(str(value[i][3]))
            gs_list = "|".join(gs_array)
        compare[gs_list].append(key)
        del gs_array[:]

    # make the groups numbered 1 - n
    i = 0
    for key, value in compare.items():
        for j in range(0, len(value)):
            # bool_intersect[i] = {}
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

    :param bool_results:
    :param intersection_sizes:
    :return:
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


def create_circle_code(bool_results):
    gps = collections.defaultdict(list)
    for key, value in bool_results.items():
        for k in bool_results[key]:
            gps[key].append(k[3])
    return gps