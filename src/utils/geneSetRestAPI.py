import requests, json

def parseGenesFromGeneSet(jsonResponse:dict):
    obj=jsonResponse["object"]
    geneVals=obj["geneset_values"]
    result=[]
    for items in geneVals:
        result.append(items["ode_gene_id"])
    return result

def fetchGeneSets(geneSetID:int):
    url= f'https://geneweaver.jax.org/api/genesets/{geneSetID}'
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url,headers=headers)
    print(response.status_code)
    dic=response.json()
    return parseGenesFromGeneSet(dic)

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
