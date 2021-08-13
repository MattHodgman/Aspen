import pandas as pd
import sys
import pickle

# PARAMETERS: (1) cluster label table

# load in MeSH pickle files
# f = open("mesh_headings.pkl", "rb")
# mesh_headings = pickle.load(f)

# f = open("mesh_numbers.pkl", "rb")
# mesh_numbers = pickle.load(f)

# load in ChEMBL
chembl = pd.read_csv('chembl_indications.tsv', sep='\t')
# chembl_mesh_headings = set(chembl.mesh_heading)

# get clusters
data = pd.read_csv(sys.argv[1], delimiter='\t')

# get all the drugs in each cluster
cluster_dict = data.set_index('Drug').groupby('Cluster').groups

# loop through each cluster
for label, drugs in cluster_dict.items():
    cluster_chembl = chembl[chembl['pref_name'].isin(drugs)] # get all the chembl info for the drugs in this cluster
    indications = cluster_chembl.groupby('mesh_heading').count()['pref_name'].sort_values(ascending=False) # get the frequency of indications in this cluster
    
    # format to get proportion of drugs that have each indication
    indications = indications.to_frame()
    indications['proportion'] = indications['pref_name'] / len(drugs)
    indications = indications.drop('pref_name',axis=1)

    # get the mean number of indications per drug
    mean = cluster_chembl.groupby('pref_name')['mesh_heading'].count().mean()

    print(f'\n\nCluster: {label}\nNumber of Drugs: {len(drugs)}\nMean Number of Indications: {mean}\n{indications}')

    

# for each cluster
#   make a tree with all the indications in all the drugs
#   count how much each indication appears
#   make a graph
#   color each node by how often its indication appears
