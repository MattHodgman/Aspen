import pickle
from graphviz import Digraph
import sys

# PARAMETERS: (1) the name or ChEMBL ID of a drug (2) Output dir where tree .png files are written

## GET RESOURCES

# load in MeSH pickle files
f = open("mesh_headings.pkl", "rb")
mesh_headings = pickle.load(f)

f = open("mesh_numbers.pkl", "rb")
mesh_numbers = pickle.load(f)

# load in ChEMBL
import pandas as pd
chembl = pd.read_csv('chembl_indications.tsv', sep='\t')
chembl_mesh_headings = set(chembl.mesh_heading)


## GET DATA

drug = sys.argv[1]
out = sys.argv[2]

# get indications
if 'CHEMBL' in drug:
    indications = chembl[chembl['chembl_id'] == drug.upper()]
else:
    indications = chembl[chembl['pref_name'] == drug.upper()]
headings = list(indications.mesh_heading)

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