# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:06:58 2023

@author: Szabi
"""

################search
from bs4 import BeautifulSoup
import os
import numpy as np
import ast
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
 
def search_vectors(query_vector, client, top_k=3):
    base_query = "*=>[KNN 3 @embedding $vector AS vector_score]"
    query = Query(base_query).return_fields("text", "vector_score").sort_by("vector_score").dialect(2)    
 
    try:
        results = client.ft("prods").search(query, query_params={"vector": query_vector})
    except Exception as e:
        print("Error calling Redis search: ", e)
        return None
 
    return results
 

# # Connect to the Redis server
# conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
 
# if conn.ping():
#     print("Connected to Redis")
 
# # Enter a query
# query = input("Enter your query: ")
 
# # Vectorize the query using OpenAI's text-embedding-ada-002 model
# print("Vectorizing query...")
# embedding = openai.Embedding.create(input=[query],engine="text-embedding-ada-002")
# query_vector = embedding["data"][0]["embedding"]
 
# # Convert the vector to a numpy array
# trans_q = translator.translate_ms(query)
# query_vector=get_embedding(trans_q, engine='text-embedding-ada-002')
# query_vector = np.array(query_vector).astype(np.float32).tobytes()
 
# # Perform the similarity search
# print("Searching for similar posts...")
# results = search_vectors(query_vector, conn)
 
# if results:
#     print(f"Found {results.total} results:")
     # for i, prod in enumerate(results.docs):
     #     score = 1 - float(post.vector_score)
     #     print(f"\t{i}. {prod.text} (Score: {round(score ,3) })")
# else:
#     print("No results found")


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

def get_topk_related_product(query_vector, conn, k=3):
    print("Searching for similar posts...")
    results = search_vectors(query_vector, conn, top_k=3)
    for i, prod in enumerate(results.docs):
        score = 1 - float(prod.vector_score)
        soup = BeautifulSoup(prod.text)
        print(f"\t{i}. {soup.text} (Score: {round(score ,3) })")
    return results

def get_recommendation(chat_history):
    completion = openai.ChatCompletion.create(
        engine="gpt-35-turbo-deployment",
        messages=chat_history
    )
    return completion.choices[0].message['content']