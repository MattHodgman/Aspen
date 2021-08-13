from graphviz import Digraph
import sys
import pandas as pd
import pickle
import matplotlib.pyplot as plt

# PARAMETERS: (1) cluster label tsv (2) cluster id (3) output dir

# read the drug list file (one drug per line) into a list
def readDrugList(file_name):
    with open(file_name) as f:
        drug_list = f.readlines()
        drug_list = [x.strip() for x in drug_list]
    return drug_list


# get the indications of all the drugs
def getIndications(drug_list, chembl):
    chembl = chembl[chembl['pref_name'].isin(drug_list)] # subset to only drugs in cluster
    indications = chembl.groupby('mesh_heading').count()['mesh_id'].to_frame() # get dataframe of the number of times each indication appears
    return indications


# make a color map for indications
def makeColorMap(indications):
    from matplotlib import colors
    norm = colors.Normalize(indications.min(), indications.max())
    return norm
    

# make a DAG of mesh headings
def makeGraph(numbers, indications):

    # get color gradient
    norm = makeColorMap(indications)

    # create graph
    dot = Digraph(comment='cluster indications', strict=True)

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
                    heading = mesh_numbers[num]
                    count = indications.loc[heading]['mesh_id']
                    rgba = plt.cm.autumn(norm(count))
                    hsv = ' '.join(map(str,rgba))
                    dot.node(id, f'{mesh_numbers[num]} ({count})', color='red')
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
    dot.render(f'{out}/cluster_{cluster}.gv', view=False)


# main
if __name__ == "__main__":

    ## GET DATA

    # load in ChEMBL
    chembl = pd.read_csv('chembl_indications.tsv', sep='\t')

    # load in MeSH pickle files
    f = open("mesh_headings.pkl", "rb")
    mesh_headings = pickle.load(f)

    f = open("mesh_numbers.pkl", "rb")
    mesh_numbers = pickle.load(f)

    # get args
    clusters = pd.read_csv(sys.argv[1],delimiter='\t') # a file that contains a list of drugs (one per line) that are in a single cluster
    cluster = sys.argv[2] # the id of the cluster
    out = sys.argv[3] # the output dir


    ## GET INDICATIONS

    drug_list = clusters[clusters['Cluster'] == int(cluster)]['Drug'].tolist() # get list of drugs in cluster

    indications = getIndications(drug_list, chembl) # get indications of all drugs in cluster
    headings = indications.index.tolist()

    # get drug indications' heading numbers
    numbers = []
    for h in headings:
        numbers.extend(mesh_headings[h])
    numbers = sorted(numbers) # sort them


    ## GRAPH

    # make graph
    makeGraph(numbers, indications)

    