# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:42:35 2023

@author: Szabi
"""

#https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/

import sys
sys.path.append(r'../')

import pandas as pd
from tqdm import tqdm
import os
import numpy as np
import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import openai
from openai.embeddings_utils import get_embedding
from tools import translator

# import json
# import ast
from dotenv import load_dotenv

load_dotenv(r'../.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')
redis_host = os.getenv('PREFIX_AZURE_REDIS_HOST_ENDPOINT')
redis_port = os.getenv('PREFIX_AZURE_REDIS_PORT')
redis_password = os.getenv('PREFIX_AZURE_REDIS_KEY')


data_path=r'../data'
tqdm.pandas()

partner='praktiker' # rossman

MAX_TEXT_LENGTH = 2048
NUMBER_PRODUCTS = 32901  


def prepare_dataset_praktiker(df):
 
    # df['Category'] = df['Category'].apply(lambda x: x.replace("/", " "))
    df.fillna('None', inplace=True)
    df.replace(["^\s*$"], 'None', regex=True, inplace=True)
    df['Product'] = df.apply(lambda row: f"{row['DisplayText']}, {row['Category']}, {row['Synonyms']}", axis=1)
    df['Description'] = df['Description'].str.slice(0,MAX_TEXT_LENGTH)
    #max(product_data_df.Description.str.len())
    #df['primary_key'] = df['Identifier']
    df.reset_index(drop=True, inplace=True)
    product_metadata = (df.head(NUMBER_PRODUCTS).to_dict(orient='index'))
    return product_metadata

def main():

    product_data_df = pd.read_json(os.path.join(data_path,"products_"+partner+".json"))  
    product_metadata = prepare_dataset_praktiker(product_data_df)
    
    
    # Connect to the Redis server
    conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
    
    # Delete all keys
    # keys = conn.keys('*')
    # conn.delete(*keys)
    # conn.flushdb()
    
    
    p = conn.pipeline(transaction=False)
    
    for k,v in tqdm(product_metadata.items()):
       
        transq=v['Product'] #translator.translate_ms(v['Product'])
        vector_product = get_embedding(transq, engine='text-embedding-ada-002')
        # convert to numpy array and bytes
        vector_product = np.array(vector_product).astype(np.float32).tobytes()
        # print the embedding (length = 1536)
        transq=v['Description'] #translator.translate_ms(v['Description'])
        vector_description = get_embedding(transq, engine='text-embedding-ada-002')
        # convert to numpy array and bytes
        vector_description = np.array(vector_description).astype(np.float32).tobytes()
     
        # Create a new hash with url and embedding
        post_hash = {
            "id":v['Identifier'],
            "url": v['Url'],
            "image_url": v['ImageUrl'],
            "brand": v['Brand'],
            "product": v['Product'],
            "description": v['Description'],
            "price": v['Price'],
            "embedding_product": vector_product,
            "embedding_description": vector_description
        }
     
        # create hash
        conn.hset(name=f"{partner}:{v['Identifier']}", mapping=post_hash)
    
    p.execute()
    
    #### creating indices
    SCHEMA = [
        VectorField("embedding_product", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}),
    ]
    
    conn.ft(f"{partner}_prod").create_index(fields=SCHEMA, definition=IndexDefinition(prefix=[f"{partner}"], index_type=IndexType.HASH))
    
    
    SCHEMA = [
        VectorField("embedding_description", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}),
    ]
    
    conn.ft(f"{partner}_desc").create_index(fields=SCHEMA, definition=IndexDefinition(prefix=[f"{partner}"], index_type=IndexType.HASH))
    
    
    conn.close()

if __name__ == "__main__":
    main()

#### add image url-s
# for k,v in tqdm(product_metadata.items()):
#     conn.hset(f"prod:{k}",'image_url',v['ImageUrl'])
    