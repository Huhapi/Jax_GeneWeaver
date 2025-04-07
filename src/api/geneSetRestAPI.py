import requests

VALID_SPECIES_NAMES = [
    "All", "Mus Musculus", "Homo Sapiens", "Rattus Norvegicus", "Danio Rerio",
    "Drosophila Melanogaster", "Macaca Mulatta", "Caenorhabditis Elegans",
    "Saccharomyces Cerevisiae", "Gallus Gallus", "Canis Familiaris",
    "Xenopus Tropicalis", "Xenopus Laevis"
]

def fetchGeneSymbols_from_geneset(geneset_id):
    """
    Fetch gene symbols for a gene set.
    Retrieves gene set data, extracts source IDs, and returns gene symbols.
    If source IDs are non-numeric, returns them directly; otherwise maps them.
    
    Args:
        geneset_id: Gene set identifier.
    
    Returns:
        List of gene symbols.
    
    Raises:
        Exception on API errors.
    """
    geneset_data = get_geneset_data(geneset_id)
    species_id = geneset_data["object"]["geneset"]["species_id"]
    
    gsv_source_lists = [
        item["gsv_source_list"]
        for item in geneset_data.get("object", {}).get("geneset_values", [])
    ]
    source_ids = [source_id for sublist in gsv_source_lists for source_id in sublist]

    # Check if source_ids are already gene symbols
    all_look_like_symbols = all(not source_id.isnumeric() for source_id in source_ids)

    if all_look_like_symbols:
        return source_ids  # Directly return symbols, skip mapping

    # Else, proceed with mapping
    species_name = get_species_name(species_id)
    gene_symbols = get_gene_symbols(source_ids, species_name)
    
    return gene_symbols

def get_geneset_data(geneset_id):
    """
    Retrieve gene set data from the API.
    
    Args:
        geneset_id: Gene set identifier.
    
    Returns:
        Dictionary with gene set data.
    
    Raises:
        Exception if the API request fails.
    """
    url = f"https://geneweaver.org/api/genesets/{geneset_id}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching geneset: {response.text}")
    return response.json()

def get_species_name(species_id):
    """
    Get standardized species name by ID.
    
    Args:
        species_id: Species identifier.
    
    Returns:
        Standardized species name.
    
    Raises:
        Exception if species not found.
    """
    url = "https://geneweaver.org/api/species"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error fetching species list: {response.text}")

    species_list = response.json().get("data", [])
    for species in species_list:
        if species["id"] == species_id:
            for valid_name in VALID_SPECIES_NAMES:
                if valid_name.lower() == species["name"].strip().lower():
                    return valid_name
    raise Exception(f"Species ID {species_id} not matched with valid names.")

def get_gene_symbols(source_ids, species_name):
    """
    Map source IDs to gene symbols via the API.
    
    Args:
        source_ids: List of source IDs.
        species_name: Standardized species name.
    
    Returns:
        List of gene symbols.
    
    Raises:
        Exception if the API mapping fails.
    """
    url = "https://geneweaver.org/api/genes/mappings"
    payload = {
        "source_ids": source_ids,
        "target_gene_id_type": "Gene Symbol",
        "species": species_name
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error fetching gene mappings: {response.text}")
    
    data = response.json()
    return [entry["mapped_ref_id"] for entry in data.get("gene_ids_map", [])]

def parse_ode_gene_id_FromGeneSet(jsonResponse:dict):
    obj=jsonResponse["object"]
    geneVals=obj["geneset_values"]
    result=[]
    for items in geneVals:
        result.append(items["ode_gene_id"])
    return result

def fetchGeneSets_ode_gene_id(geneSetID:int):
    url= f'https://geneweaver.jax.org/api/genesets/{geneSetID}'
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url,headers=headers)
    dic=response.json()
    return parse_ode_gene_id_FromGeneSet(dic)

def fetchSpecies():
    url = 'https://geneweaver.jax.org/api/species'
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    species_data = response.json()['data']
    result = []
    for species in species_data:
        if species['id'] != 0:
            result.append((species['id'], species['name']))
    return result
