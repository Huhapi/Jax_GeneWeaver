file_path_1 = "/Users/kishan/Jax_GeneWeaver/src/plugins/MSET/RATUS1"
file_path_2 = "/Users/kishan/Jax_GeneWeaver/src/plugins/MSET/ratus2"


with open(file_path_1, "r") as f:
    ratus1_content = f.read()


with open(file_path_2, "r") as f:
    ratus2_content = f.read()

print(ratus1_content[500:1000])  # print first 500 characters

print(ratus2_content[500:1000])  # print first 500 characters



# Let's extract full gene lists from both files
def extract_genes_from_gw(file_content):
    genes = []
    for line in file_content.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ":", "=", "+", "@", "%", "A", "!", "Q")):
            continue
        gene = line.split()[0]
        genes.append(gene)
    return genes

# group_2_genes = extract_genes_from_gw(ratus1_content)  # Apoptosis
group_1_genes = extract_genes_from_gw(ratus1_content)  # Alzheimer's
group_2_genes = extract_genes_from_gw(ratus2_content)  # Alzheimer's





