from typing import List


def extract_genes_from_gw(file_content: str) -> List[str]:
    genes = []
    skip_chars = ("#", ":", "=", "+", "@", "%", "A", "!", "Q", )
    for line in file_content.splitlines():
        line = line.strip()
        if not line or line.startswith(skip_chars):
            continue
        gene = line.split()[0]
        genes.append(gene)
    return genes