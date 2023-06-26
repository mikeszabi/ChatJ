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


def prepare_dataset_praktiker(product_data_df):
 
    # df['Category'] = df['Category'].apply(lambda x: x.replace("/", " "))
    product_data_df.fillna('None', inplace=True)
    product_data_df.replace(["^\s*$"], 'None', regex=True, inplace=True)
    product_data_df['Product'] =  product_data_df['DisplayText'] #product_data_df.apply(lambda row: f"{row['DisplayText']}, {row['Category']}", axis=1)
    product_data_df['Description']=product_data_df.apply(lambda row: f"{row['Category']}, {row['Description']}", axis=1)   
    product_data_df['Description'] = product_data_df['Description'].str.slice(0,MAX_TEXT_LENGTH)
    #max(product_data_df.Description.str.len())
    #df['primary_key'] = df['Identifier']
    product_data_df.reset_index(drop=True, inplace=True)
    product_metadata = (product_data_df.head(NUMBER_PRODUCTS).to_dict(orient='index'))
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
       
        product=v['Product']
        product_en=translator.translate_openai(product).replace('\n','')
        vector_product = get_embedding(product, engine='text-embedding-ada-002')
        vector_product_en = get_embedding(product_en, engine='text-embedding-ada-002')
        # convert to numpy array and bytes
        vector_product = np.array(vector_product).astype(np.float32).tobytes()
        vector_product_en = np.array(vector_product_en).astype(np.float32).tobytes()
        # print the embedding (length = 1536)
        description=v['Description'] #translator.translate_ms(v['Description'])
        description_en=translator.translate_openai(description).replace('\n','')
        vector_description = get_embedding(description, engine='text-embedding-ada-002')
        vector_description_en = get_embedding(description_en, engine='text-embedding-ada-002')
        # convert to numpy array and bytes
        vector_description = np.array(vector_description).astype(np.float32).tobytes()
        vector_description_en = np.array(vector_description_en).astype(np.float32).tobytes()
     
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
            "embedding_description": vector_description,
            "embedding_product_en": vector_product_en,
            "embedding_description_en": vector_description_en
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
    
    SCHEMA = [
        VectorField("embedding_product_en", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}),
    ]   
    conn.ft(f"{partner}_prod_en").create_index(fields=SCHEMA, definition=IndexDefinition(prefix=[f"{partner}"], index_type=IndexType.HASH))
    
    
    SCHEMA = [
        VectorField("embedding_description_en", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}),
    ]
    conn.ft(f"{partner}_desc_en").create_index(fields=SCHEMA, definition=IndexDefinition(prefix=[f"{partner}"], index_type=IndexType.HASH))
    
    
    
    conn.close()

if __name__ == "__main__":
    main()

#### add image url-s
# for k,v in tqdm(product_metadata.items()):
#     conn.hset(f"prod:{k}",'image_url',v['ImageUrl'])
    