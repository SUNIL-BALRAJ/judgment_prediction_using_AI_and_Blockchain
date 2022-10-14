#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
from collections import Counter
from matplotlib import rc

import nltk
# nltk.download('stopwords')
# nltk.download('wordnet')
# from nltk.corpus import stopwords

import re
from nltk.stem import WordNetLemmatizer
stemmer = WordNetLemmatizer()
import transformers
from transformers import XLNetTokenizer, XLNetModel, AdamW, get_linear_schedule_with_warmup
import torch
import numpy as np
import pandas as pd
from collections import defaultdict
from textwrap import wrap
from pylab import rcParams

from torch import nn, optim
from keras_preprocessing.sequence import pad_sequences
from torch.utils.data import TensorDataset,RandomSampler,SequentialSampler
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
from transformers import XLNetTokenizer, XLNetModel
from transformers import XLNetForSequenceClassification

from django.conf import settings
import pickle

fasttext_embed = np.load(settings.MODEL_ROOT +  "/fasttext.npy")
fasttext_word_to_index = pickle.load(open(settings.MODEL_ROOT + "/fasttext_voc", 'rb'))


import pickle

def judgement_pred_bigru(user_text):

    user_text = np.array(user_text)
    user_text = np.expand_dims(user_text,axis=0)


    # In[ ]:


    from keras.preprocessing.text import Tokenizer
    from keras_preprocessing.sequence import pad_sequences

    MAX_WORDS = 20000
    MAX_SEQUENCE_LENGTH = 200
    EMBEDDING_DIM = fasttext_embed.shape[1]
    tokenizer = Tokenizer(num_words=MAX_WORDS,oov_token='__UNK__')
    tokenizer.fit_on_texts(user_text)
    seqs = tokenizer.texts_to_sequences(user_text)
    udata = pad_sequences(seqs, maxlen=MAX_SEQUENCE_LENGTH,padding='post')



    # In[ ]:


    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))


    # In[ ]:


    embedding_matrix = np.zeros((MAX_WORDS+2, EMBEDDING_DIM))
    for word, i in word_index.items():
        if i > MAX_WORDS:
                continue
        try:
            embedding_vector = fasttext_embed[fasttext_word_to_index[word],:]
            embedding_matrix[i] = embedding_vector
        except:
            pass


    # In[ ]:


    # to run tensorflow on mac
    import os
    os.environ['KMP_DUPLICATE_LIB_OK']='True'



    # In[ ]:


    import sklearn.exceptions
    import warnings
    warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)
    from keras.callbacks import ModelCheckpoint
    from tensorflow.keras.layers import Embedding
    #from keras_tqdm import TQDMNotebookCallback
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Bidirectional
    from tensorflow.keras.layers import GRU
    from tensorflow.keras.optimizers import Adam
    from keras import backend as K
    from livelossplot.tf_keras import PlotLossesCallback

    GRU_SIZE = 100
    DENSE = 200

    # create empty sequential model
    model = Sequential()
    # add an embedding layer
    model.add(Embedding(MAX_WORDS+2, EMBEDDING_DIM, weights=[embedding_matrix], 
                        input_length=MAX_SEQUENCE_LENGTH, mask_zero=True, trainable=False))
    # Use 0.2 dropout probabillity
    model.add(Dropout(0.2))
    # add a bidirectional gru layer with 0.2 variational (recurrent) dropout 
    model.add(Bidirectional(GRU(GRU_SIZE, return_sequences=False, recurrent_dropout = 0.2)))
    # add a hidden MLP layer
    model.add(Dropout(0.2))
    model.add(Dense( DENSE, activation='relu' ))
    # add the output MLP layer
    model.add(Dense(1, activation='sigmoid'))
    from livelossplot.tf_keras import PlotLossesCallback

    print(model.summary())

    # In[ ]:



    #load weights from the pre-trained model
    model.load_weights(settings.MODEL_ROOT + "/keras_BiGRU_model.h5")
    model.compile(loss='binary_crossentropy',
                    optimizer=Adam(lr=0.001),)



    # In[ ]:

    print(udata.shape)

    predictions = model.predict(udata)
    predictions = predictions.reshape(len(predictions),)

    # for i in range(len(predictions)):
    #     if predictions[i]<0.5:
    #         predictions[i]=0
    #     else:
    #         predictions[i]=1
    # print(predictions)

    accept_pred = round(float(predictions[0]),2) * 100

    return accept_pred



def judgement_pred_Xlnet(text):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels = 2)
    model.load_state_dict(torch.load("Xlnetmodel"))
    model = model.to(device)

    PRE_TRAINED_MODEL_NAME = 'xlnet-base-cased'
    tokenizer = XLNetTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
    review_text = text

    encoded_review = tokenizer.encode_plus(
    review_text,
    max_length=512,
    add_special_tokens=True,
    return_token_type_ids=False,
    pad_to_max_length=False,
    return_attention_mask=True,
    return_tensors='pt',
    )

    input_ids = pad_sequences(encoded_review['input_ids'], maxlen=512, dtype=torch.Tensor ,truncating="post",padding="post")
    input_ids = input_ids.astype(dtype = 'int64')
    input_ids = torch.tensor(input_ids) 

    attention_mask = pad_sequences(encoded_review['attention_mask'], maxlen=512, dtype=torch.Tensor ,truncating="post",padding="post")
    attention_mask = attention_mask.astype(dtype = 'int64')
    attention_mask = torch.tensor(attention_mask) 
    input_ids = input_ids.reshape(1,512).to(device)
    attention_mask = attention_mask.to(device)

    outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    outputs = outputs[0][0].cpu().detach()

    probs = F.softmax(outputs, dim=-1).cpu().detach().numpy().tolist()
    _, prediction = torch.max(outputs, dim =-1)
    class_names=["rejected","accepted"]
    print("Petition accepted:", probs[1])
    print("petition rejected:", probs[0])
    #print(f'Review text: {review_text}')
    print(f'Sentiment  : {class_names[prediction]}')    

    return probs

# user_text=""
# with open("C2.txt",'r') as f:
#     for line in f.readlines():
#         user_text+=line.strip()
# judgement_pred_bigru(user_text)