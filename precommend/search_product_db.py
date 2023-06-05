# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:06:58 2023

@author: Szabi
"""

################search
from bs4 import BeautifulSoup
import os
import numpy as np
import pandas as pd
# import ast
import redis
from redis.commands.search.query import Query
from openai.embeddings_utils import get_embedding
from dotenv import load_dotenv

from tools import translator


load_dotenv(r'../.env')

import openai

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')
redis_host = os.getenv('PREFIX_AZURE_REDIS_HOST_ENDPOINT')
redis_port = os.getenv('PREFIX_AZURE_REDIS_PORT')
redis_password = os.getenv('PREFIX_AZURE_REDIS_KEY')
 
Top_K=3
 
def search_vectors(query_vector, conn, top_k=3):
    base_query = f"*=>[KNN {top_k} @embedding $vector AS vector_score]"
    query = Query(base_query).return_fields("text", "vector_score", 'url', 'image_url','price').sort_by("vector_score").dialect(2)    
 
    try:
        results = conn.ft("prods").search(query, query_params={"vector": query_vector})
    except Exception as e:
        print("Error calling Redis search: ", e)
        return None
 
    return results
 


def connect2redis():
    # Connect to the Redis server
    conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
     
    if conn.ping():
        print("Connected to Redis")
    return conn

def get_customer_question_embeddings(query):
   # Get embedding
   trans_q = translator.translate_ms(query)
   query_vector = get_embedding(trans_q, engine='text-embedding-ada-002')
    
   # Convert the vector to a numpy array
   query_vector = np.array(query_vector).astype(np.float32).tobytes()
   return query_vector

def get_topk_related_product(query_vector, conn, language='hu', k=3):
    print("Searching for similar posts...")
    results = search_vectors(query_vector, conn, top_k=k)
    brand_list=[]
    meta_list=[]
    for i, prod in enumerate(results.docs):
       # score = 1 - float(prod.vector_score)
        soup = BeautifulSoup(inv_text(prod.text))
        brand_list.append({'role': "assistant", "content": f"{soup.text}"})
        meta_list.append({'score':prod.vector_score,'price':prod.price,'url':prod.url,'image_url':prod.image_url})
    return brand_list, meta_list

def get_recommendation(chat_history,language='hun'):
    completion = openai.ChatCompletion.create(
        engine="gpt-35-turbo-deployment",
        messages=chat_history
    )
    comp_text=completion.choices[0].message['content']
    if language=='en':
        comp_text=translator.translate_ms(comp_text)
    return comp_text


def inv_text(text):
    n=text.find('<p>')
    if n>0:
        newtext=text[n+3:]+text[:n]
    else:
        newtext=text
    return newtext

####
# conn=connect2redis()
# query='Milyen nagyteljesítményű ütvefúrókat javasolsz?'
# trans_q = translator.translate_ms(query)
# query_vector=get_customer_question_embeddings(trans_q)
# results=get_topk_related_product(query_vector, conn, language='hu', k=3)

# brand_list=[]
# meta_list=[]
# for i, prod in enumerate(results.docs):
#    # score = 1 - float(prod.vector_score)
#     soup = BeautifulSoup(inv_text(prod.text))
#     brand_list.append({'role': "assistant", "content": f"{soup.text}"})
#     meta_list.append({'price':prod.price,'url':prod.url,'image_url':prod.image_url})

# df_brand=pd_brand=pd.e(results.docs)

# # k=10
# # conn.hget(f"prod:{k}",'image_url')