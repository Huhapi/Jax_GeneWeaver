# Test section for utils, accessing genes from GeneWeaver ReST API
from utils import geneSetRestAPI as ReSTAPI

if __name__=="__main__":
    geneIds=ReSTAPI.fetchGeneSets(219249)
    print("Geneset length: "+str(len(geneIds)))
    print(geneIds)