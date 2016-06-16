import os,sys,csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import *

sf_all = int(sys.argv[1])
num_clusters = int(sys.argv[2])

import gensim
from gensim.models import word2vec
model_path = 'train_data/GoogleNews-vectors-negative300.bin'
w2v_model = word2vec.Word2Vec.load_word2vec_format(model_path, binary=True)
index2word_set = set(w2v_model.index2word)

import re
from nltk.corpus import stopwords

data_path = 'test_data/'
sf_data = pd.read_csv(data_path+"statefarm_facebook_statuses.csv", header=0,sep="," ).fillna('')
fpg_data = pd.read_csv(data_path+"flotheprogressivegirl_facebook_statuses.csv", header=0,sep="," ).fillna('')
geico_data = pd.read_csv(data_path+"geico_facebook_statuses.csv", header=0,sep="," ).fillna('')
lm_data = pd.read_csv(data_path+"libertymutual_facebook_statuses.csv", header=0,sep="," ).fillna('')
nation_data = pd.read_csv(data_path+"nationwide_facebook_statuses.csv", header=0,sep="," ).fillna('')
pro_data = pd.read_csv(data_path+"progressive_facebook_statuses.csv", header=0,sep="," ).fillna('')
as_data = pd.read_csv(data_path+"allstate_facebook_statuses.csv", header=0,sep="," ).fillna('')

def clean_sentence(msg):
    text = re.sub("[^a-zA-Z]"," ", msg)
    words = text.split()
    stops = set(stopwords.words("english"))
    word_vec = [w for w in words if not w in stops]
    return(word_vec)

def load_data(all_data = True):
    if all_data:
        facebook_status = pd.concat([sf_data,fpg_data,geico_data,lm_data,nation_data,pro_data,as_data],ignore_index=True)
    else:
        facebook_status = sf_data
    return facebook_status
    
facebook_status = load_data(sf_all)
num_col = facebook_status.shape[0]
comments = np.zeros([num_col,300]) 

print('data loaded')

numVec = np.zeros((300,),dtype="float32")
denom = 0
for i in range(num_col):
    word_vec = clean_sentence(facebook_status['status_message'][i])
    for word in word_vec:
        if word in index2word_set: 
            denom = denom + 1.
            numVec = np.add(numVec,w2v_model[word])
    comments[i,:] = np.divide(numVec,denom)

print('comments collected')

from sklearn.cluster import KMeans
#num_clusters = 5
kmeans = KMeans( n_clusters = num_clusters , random_state = 701 )
idx = kmeans.fit_predict(comments)
#np.savetxt('idx.data',idx)

if sf_all:
  data_file = 'all_idx.data'
else:
  data_file = 'sf_idx.data'

fw = open(data_file, 'w')
for i in range(num_col):
    if i < sf_data.shape[0]:
        fw.write('StateFarm %d\n'%idx[i])
    elif i < sf_data.shape[0] + fpg_data.shape[0]:
        fw.write('FlotheProgressiveGirl %d\n'%idx[i])
    elif i < sf_data.shape[0] + fpg_data.shape[0] + geico_data.shape[0]:
        fw.write('Geico %d\n'%idx[i])
    elif i < sf_data.shape[0] + fpg_data.shape[0] + geico_data.shape[0] + lm_data.shape[0]:
        fw.write('LibertyMutual %d\n'%idx[i])
    elif i < sf_data.shape[0] + fpg_data.shape[0] + geico_data.shape[0] + lm_data.shape[0] + nation_data.shape[0]:
        fw.write('Nationwide %d\n'%idx[i])
    elif i < sf_data.shape[0] + fpg_data.shape[0] + geico_data.shape[0] + lm_data.shape[0] + nation_data.shape[0] + pro_data.shape[0]:
        fw.write('Progressive %d\n'%idx[i])
    else:
    	fw.write('All State %d\n'%idx[i])
fw.close()

print('clustering completed')
