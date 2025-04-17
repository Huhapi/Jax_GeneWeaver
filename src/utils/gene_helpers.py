from typing import List


def extract_genes_from_gw(file_content: str) -> List[str]:
    genes = []
    skip_chars = ("#", ":", "=", "+", "@", "%", "!", "Q")
    count = 0
    for line in file_content.splitlines():
        count+= 1
        if(count > 16):
            line = line.strip()
            if not line or line.startswith(skip_chars):
                continue
            gene = line.split()[0]
            genes.append(gene)
    return genes

def extract_bg_genes(file_content: str) -> List[str]:
    genes = []
    for line in file_content.splitlines():
        line = line.strip()
        gene = line.split()[0]
        genes.append(gene)
    return genes