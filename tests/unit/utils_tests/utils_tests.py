# Test section for utils, accessing genes from GeneWeaver ReST API
from utils.geneSetRestAPI import fetchGeneSymbols_from_geneset

if __name__=="__main__":
    symbols=fetchGeneSymbols_from_geneset(356407) # https://www.geneweaver.org/viewgenesetdetails/219249
    print("Gene Symbols: ",((symbols)))