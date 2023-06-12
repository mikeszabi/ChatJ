# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:06:58 2023

@author: Szabi
"""

################search
import sys
sys.path.append(r'../')
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
 
 
def search_vectors(query_vector, conn, partner='praktiker', field='prod', top_k=3):
    db_index = f"{partner}_{field}"
    if field=='prod':
        base_query = f"*=>[KNN {top_k} @embedding_product $vector AS vector_score]"
    else:
        base_query = f"*=>[KNN {top_k} @embedding_description $vector AS vector_score]"
    redis_query = Query(base_query).return_fields("vector_score", "brand", "product", "description", 'url', 'image_url','price').sort_by("vector_score").dialect(2)    
 
    try:
        results = conn.ft(db_index).search(redis_query, query_params={"vector": query_vector})
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
   trans_q = translator.translate_openai(query)
   query_vector = get_embedding(trans_q, engine='text-embedding-ada-002')
    
   # Convert the vector to a numpy array
   query_vector = np.array(query_vector).astype(np.float32).tobytes()
   return query_vector


def get_topk_related_product(query_vector, conn, partner='praktiker', field='prod', language='hu', top_k=3, sim_tsh=0.2):
    print("Searching for similar products...")
    results = search_vectors(query_vector, conn, partner=partner, field=field, top_k=top_k)
    brand_list=[]
    meta_list=[]
    for i, prod in enumerate(results.docs):
        # print(prod.vector_score)
        if float(prod.vector_score)<sim_tsh:
            soup = BeautifulSoup(prod.description+' '+prod.product+' '+prod.brand)
            brand_list.append({'role': "assistant", "content": f"{soup.text}"})
            meta_list.append({'score':prod.vector_score,'price':prod.price,'brand':prod.brand,'prod':prod.product,'url':prod.url,'image_url':prod.image_url})
    return brand_list, meta_list

def get_recommendation(chat_history,language='hu'):
    completion = openai.ChatCompletion.create(
        engine="gpt-35-turbo-deployment",
        messages=chat_history
    )
    comp_text=completion.choices[0].message['content']
    if language=='en':
        comp_text=translator.translate_ms(comp_text)
    return comp_text


# def inv_text(text):
#     n=text.find('<p>')
#     if n>0:
#         newtext=text[n+3:]+text[:n]
#     else:
#         newtext=text
#     return newtext

####
# partner='praktiker'
# field='prod'

# message_objects = []
# message_objects.append({"role": "system",
#                         "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})


# conn=connect2redis()
# query='Gömbgrillt keresek'
# query_vector=get_customer_question_embeddings(query)
# brand_list, meta_list=get_topk_related_product(query_vector, conn, partner, field='prod', language='hu', top_k=5, sim_tsh=0.25)

# if len(brand_list)<4:
#     brand_list_2, meta_list_2=get_topk_related_product(query_vector, conn, partner, field='desc', language='hu', top_k=5, sim_tsh=0.25)
#     brand_list.extend(brand_list_2)
#     meta_list.extend(meta_list_2)
    

# if len(brand_list)>0:
#     message_objects.append({"role": "assistant", "content": "A következő releváns termékeket találtam"})
#     message_objects.extend(brand_list)
#     message_objects.append({"role": "assistant", "content": "Íme az ajánlásom"})
# else:
#     message_objects.append({"role": "assistant", "content": "Pontosítsd a kérdést, erre nem volt találat"})

# result = get_recommendation(message_objects,language='hu')

# k=10
# conn.hget(f"prod:{k}",'image_url')