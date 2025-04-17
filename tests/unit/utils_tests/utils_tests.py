# Test section for utils, accessing genes from GeneWeaver ReST API
from plugins.api.geneSetRestAPI import fetchGeneSymbols_from_geneset
from utils.gene_helpers import extract_genes_from_gw, extract_bg_genes
import os

def test_extract_genes_from_gw():
    """ Testing utils.gene_helpers.extract_genes_from_gw """
    current_dir = os.path.dirname(__file__)
    file_path_1 = os.path.join(current_dir, "ptest_ratus_1")
    with open(file_path_1, "r") as f:
        content1 = f.read()
    genes = extract_genes_from_gw(content1)
    list = [ "Akt1", "Akt",	"Akt2",	"Bax", "Bcl2", "Bcl-2", "Bcl2l1", "Bcl-xl", "Bcl2l", "Bclx", "bcl-X", "Capn1", "CANP 1", "muCANP", "Capn2", "Casp3"]

    passed = True
    for x in range(len(genes)):
        if(not list[x] == genes[x]):
            passed = False
            break
    if(passed):
        print("Extract genes from gw success.")
    else:
        print("Extract genes from gw failed.")



def test_extract_bg_genes():
    """ Testing utils.gene_helpers.extract_bg_genes """
    current_dir = os.path.dirname(__file__)
    file_path_1 = os.path.join(current_dir, "ptest_ratus_bg")
    with open(file_path_1, "r") as f:
        content1 = f.read()
    genes = extract_bg_genes(content1)
    genelist = [
        "Akt1",	
        "Akt",	
        "Akt2",	
        "Bax",	
        "Bcl2",	 
        "Bcl-2",	
        "Bcl2l1",	
        "Bcl-xl",	
        "Bcl2l",	
        "Bclx",	
        "bcl-X",	
        "Capn1",	
        "CANP 1",	
        "muCANP",	
        "Capn2",	
        "Casp3",	
        "CPP32-beta",	
        "Lice",	
        "Yama",	
        "Cycs",	
        "CYCSA",	
        "Cyct",	
        "CYCTA",	
        "Il1a",	
        "IL-1 alpha",	
        "IL-1F1"
    ]
    passed = True
    for x in range(len(genes)):
        if(not genelist[x] == genes[x]):
            passed = False
            break
    if(passed):
        print("Extract bg genes success.")
    else:
        print("Extract bg genes failed.")
    

def test_fetchGeneSymbols():
    symbols=fetchGeneSymbols_from_geneset(233325) # https://www.geneweaver.org/viewgenesetdetails/219249
    print("Gene Symbols: ",((symbols)))


if __name__=="__main__":
    test_extract_genes_from_gw()
    test_extract_bg_genes()