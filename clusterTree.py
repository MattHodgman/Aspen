from graphviz import Digraph
import sys
import pandas as pd

# PARAMETERS: (1) file containing a list of drugs in a cluster (2) output dir

# read the drug list file (one drug per line) into a list
def readDrugList(file_name):
    with open(file_name) as f:
        drug_list = f.readlines()
        drug_list = [x.strip() for x in drug_list]
    return drug_list


# get the indications of all the drugs
def getIndications(drug_list):
    chembl = chembl[chembl['pref_name'].isin(drug_list)]
    chembl.mesh_heading


if __name__ == "__main__":
    # load in ChEMBL
    chembl = pd.read_csv('chembl_indications.tsv', sep='\t')

    # get args
    drug_file_name = sys.argv[1] # a file that contains a list of drugs (one per line) that are in a single cluster
    out = sys.argv[2] # the output dir

    drug_list = readDrugList(drug_file_name) # get list of drugs in cluster
    indications = getIndications(drug_list) # get indications of all drugs in cluster

    # get indications


    # check if drug is in chembl_indications.tsv
    if len(headings) == 0:
        print(f'{drug} not found.')
        sys.exit()

    # get drug indications' heading numbers
    numbers = []
    for h in headings:
        numbers.extend(mesh_headings[h])
    numbers = sorted(numbers) # sort them


    ## MAKE GRAPH

    # create graph
    dot = Digraph(comment=f'{drug} indications', strict=True)

    # add nodes
    s = '.'
    for n in numbers:
        n_list = n.split('.') # split number into list

        # add root nodes
        roots = {'A' : 'Anatomy',
                'B' : 'Organisms',
                'C' : 'Diseases',
                'D' : 'Chemicals and Drugs',
                'E' : 'Analytical, Diagnostic and Therapeutic Techniques, and Equipment',
                'F' : 'Psychiatry and Psychology',
                'G' : 'Phenomena and Processes',
                'H' : 'Disciplines and Occupations',
                'I' : 'Anthropology, Education, Sociology, and Social Phenomena',
                'J' : 'Technology, Industry, and Agriculture',
                'K' : 'Humanities',
                'L' : 'Information Science',
                'M' : 'Named Groups',
                'N' : 'Health Care',
                'V' : 'Publication Characteristics',
                'Z' : 'Geographicals'}
        
        root = n[0]
        if root not in dot.body:
            dot.node(root, roots[root])

        # add rest of nodes and edges
        for i in range(len(n_list)):
            num = s.join(n_list[:i+1]) # get first i elements in list to create heading ID's
            id = num.replace('.','')

            # add node with id if doesn't already exist
            if id not in dot.body:
                if num in numbers:
                    dot.node(id, mesh_numbers[num], color = 'red')
                else:
                    dot.node(id, mesh_numbers[num])

            # add edges
            # if has next number
            if i != len(n_list) - 1:
                id_next = ''.join(n_list[:i+2])
                dot.edge(id, id_next)
            # add edges to roots
            if i == 0:
                dot.edge(id[0],id)

    # save results
    dot.render(f'{out}/{drug}.gv', view=False)