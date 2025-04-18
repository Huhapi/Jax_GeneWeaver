from src.plugins.api.geneSetRestAPI import get_species_name, fetchGeneSets_ode_gene_id, get_geneset_data

def test_get_species_name_homo_sapiens():
    """
    Test that species ID 2 returns 'Homo Sapiens'
    """
    species_name = get_species_name(2)
    result = species_name == "Homo Sapiens"
    print("Species name test result:", result)

def test_get_geneset_data():
    """
    Test fetching gene set data for geneset 1256
    """
    print("\nTesting get_geneset_data:")
    result = get_geneset_data(1256)
    print(result)
    return result

def test_fetch_geneset_ode_gene_id():
    """
    Test fetching ode_gene_id for geneset 1256
    """
    print("\nTesting fetchGeneSets_ode_gene_id:")
    result = fetchGeneSets_ode_gene_id(1256)
    print(result)
    return result


if __name__ == "__main__":
    test_get_species_name_homo_sapiens()
    test_get_geneset_data()
    test_fetch_geneset_ode_gene_id()
