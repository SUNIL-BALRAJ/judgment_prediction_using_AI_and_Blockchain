# pip install transformers
# pip install -U sentence-transformers
# pip install word2number


from django.conf import settings
from word2number import w2n
from sentence_transformers import SentenceTransformer, util

import pandas as pd
import numpy as np

a=pd.read_csv(settings.MODEL_ROOT  + "/timeline.csv",encoding= 'unicode_escape')
# a.drop(a.columns[[2,3, 4]], axis=1, inplace=True)
# dict = {'For the balance due on a mutual, open and current account, where there have been recipro­cal demands between the par­ties.':'text','Three years':'time'}
# a.rename(columns=dict,inplace=True)

docs=[]
for i in a.text:
  docs.append(i)

model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')
doc_emb = np.load(settings.MODEL_ROOT + "/docemb.npy")


def get_timeline_pred(query):
  query_emb = model.encode(query)
  scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()

  doc_score_pairs = list(zip(docs, scores))
  doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)

  timeline = 0  
  
  #Output passages & scores
  for doc, score in doc_score_pairs:
      print(score, doc)
      for i in range(len(a)):
        if a.text[i]==doc:
          b=a.time[i].split()
          res = w2n.word_to_num(b[0]) 
          timeline = str(res) + " " + str(b[1])
          # count = str(res)
          # value = str(b[1])

      break

  return timeline


# query = "to a High Court from any decree or order;"
# timeline = get_timeline_pred(query)
# print(timeline)