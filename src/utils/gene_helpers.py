from typing import List


def extract_genes_from_gw(file_content: str) -> List[str]:
    """
    This extracts genes from the contents of a gene set file.
    It assumes the first 16 lines are unuseful data for genes.
    It also avoids the line starting with the characters below.
    """
    genes = []
    skip_chars = ("#", ":", "=", "+", "@", "%", "!")
    count = 0
    for line in file_content.splitlines():
        count+= 1
        if(count > 16):
            line = line.strip()
            if not line or line.startswith(skip_chars):
                continue
            line_split = line.split()
            gene = line_split[0]
            if(len(line_split)>2):
                gene += " "+line_split[1]
            genes.append(gene)
    return genes

def extract_bg_genes(file_content: str) -> List[str]:
    """
    Extracts genes from the content of a background gene file which only has genes
    in it.
    """
    genes = []
    for line in file_content.splitlines():
        line = line.strip()
        split_line = line.split()
        if(len(split_line)>0):
            gene = split_line[0]
            if(len(split_line)>1):
                gene += " "+split_line[1]
            genes.append(gene)
            
    return genes