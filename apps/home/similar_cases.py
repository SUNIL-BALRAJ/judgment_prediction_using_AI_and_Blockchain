from audioop import reverse
import pickle
import pandas as pd
from rank_bm25 import BM25Okapi
import numpy as np
from django.conf import settings

import re
import nltk
# lst_stopwords = nltk.corpus.stopwords.words("english")

ps = nltk.stem.porter.PorterStemmer()
lem = nltk.stem.wordnet.WordNetLemmatizer()


# nltk.download('wordnet')
# lem = nltk.stem.wordnet.WordNetLemmatizer()

open_file = open(settings.MODEL_ROOT + "/tokenized_corpus", "rb")
tokenized_corpus = pickle.load(open_file)
n=pd.read_csv(settings.MODEL_ROOT + "/corpus_names.csv")
bm25 = BM25Okapi(tokenized_corpus)

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
    # if flg_lemm == True:
    lst_text = [lem.lemmatize(word) for word in lst_text]

        
    # back to string from list
    text = " ".join(lst_text)
    return text

def similarcase(a):
     b = utils_preprocess_text(a, flg_stemm = False, flg_lemm=True)
     open_file.close()
          
     name=n["Name"]
     print(len(tokenized_corpus))
     print(len(name))
     sim_cases, case_probs = bm25.get_top_n(b.split(" "),name, n=10), bm25.get_scores(b.split(" "))
     case_probs = (case_probs - np.min(case_probs)) / (np.max(case_probs) - np.min(case_probs))
     case_probs = case_probs.tolist()
     case_probs.sort(reverse=True)
     case_probs = case_probs[0:10]
     
     for i in range(0,10):
         case_probs[i] = int(round(case_probs[i],2) * 100)

     print(len(case_probs), len(sim_cases))

     similarcases = []
     for i in range(0,10):
         similarcases.append((sim_cases[i], case_probs[i]))

     print(similarcases)
     

     return similarcases, sim_cases, case_probs

# user_text=""
# with open("C2.txt",'r') as f:
#     for line in f.readlines():
#         user_text+=line.strip()
# similarcase(user_text)