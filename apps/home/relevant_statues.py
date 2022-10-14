import pickle
import pandas as pd
from rank_bm25 import BM25Okapi
import numpy as np
import re
import nltk

from django.conf import settings

open_file = open(settings.MODEL_ROOT + "/tokenized_statute", "rb")
tokenized_corpus = pickle.load(open_file)
open_file.close()
bm25 = BM25Okapi(tokenized_corpus)
bm25
n=pd.read_csv(settings.MODEL_ROOT + "/statute_names.csv")

lst_stopwords = nltk.corpus.stopwords.words("english")

ps = nltk.stem.porter.PorterStemmer()

nltk.download('wordnet')
lem = nltk.stem.wordnet.WordNetLemmatizer()

def utils_preprocess_text(text, flg_stemm=True, flg_lemm =True, lst_stopwords=None ):
    text = re.sub(r'[^\w\s]', '', str(text).lower().strip())
    
    #tokenization(convert from string to List)
    lst_text = text.split()
    
    #remove stopwords
    if lst_stopwords is not None:
        lst_text = [word for word in lst_text if word not in
                   lst_stopwords]
        
     #stemming
    if flg_stemm == True:
        ps = nltk.stem.porter.PorterStemmer()
        lst_text = [ps.stem(word) for word in lst_text]
        
    #Lemmentization
    if flg_lemm == True:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) for word in lst_text]
        
    # back to string from list
    text = " ".join(lst_text)
    return text

def similarstat(a):
     b = utils_preprocess_text(a, flg_stemm = False, flg_lemm=True)
     name=n["Name"]
     print(len(tokenized_corpus))
     print(len(name))
     
     sim_statues, statue_probs = bm25.get_top_n(b.split(" "),name, n=10), bm25.get_scores(b.split(" "))
     statue_probs = (statue_probs - np.min(statue_probs)) / (np.max(statue_probs) - np.min(statue_probs))
     statue_probs = statue_probs.tolist()
     statue_probs.sort(reverse=True)
     statue_probs = statue_probs[0:10]
     
     for i in range(0,10):
         statue_probs[i] = int(round(statue_probs[i],2) * 100)

     print(len(statue_probs), len(sim_statues))

     sim_prob_statues = []
     for i in range(0,10):
         sim_prob_statues.append((sim_statues[i], statue_probs[i]))

     print(sim_prob_statues)
     

     return sim_prob_statues, sim_statues, statue_probs

# user_text=""
# user_text=""
# with open("C2.txt",'r') as f:
#     for line in f.readlines():
#         user_text+=line.strip()
# similarstat(user_text)
# backgroundColor:["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850","#3e95cd", "#8e5ea2", "#c45850", "#e8c3b9", "#3e95cd"] ,