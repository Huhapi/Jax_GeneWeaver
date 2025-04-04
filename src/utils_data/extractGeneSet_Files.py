def extract_genes_from_gw(file_content):
    genes = []
    for line in file_content.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ":", "=", "+", "@", "%", "A", "!", "Q")):
            continue
        gene = line.split()[0]
        genes.append(gene)
    return genes