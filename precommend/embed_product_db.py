# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:42:35 2023

@author: Szabi
"""

#https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/

import pandas as pd
from tqdm import tqdm
import os
import numpy as np
import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import openai
from openai.embeddings_utils import get_embedding
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

partner='praktiker'

MAX_TEXT_LENGTH = 2048
NUMBER_PRODUCTS = 32901  


def prepare_dataset_praktiker(df):
 
    df['Category'] = df['Category'].apply(lambda x: x.replace("/", " "))
    df['text'] = df.apply(lambda row: f"{row['Category']}, {row['Description']}", axis=1)
    df['text'] = df['text'].str.slice(0,MAX_TEXT_LENGTH)
    #max(product_data_df.Description.str.len())
    df['primary_key'] = df['Identifier']
    df.reset_index(drop=True, inplace=True)
    product_metadata = (df.head(NUMBER_PRODUCTS).to_dict(orient='index'))
    return product_metadata


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
   
    # print the embedding (length = 1536)
    vector = get_embedding(v['text'], engine='text-embedding-ada-002')
    # convert to numpy array and bytes
    vector = np.array(vector).astype(np.float32).tobytes()
    
 
    # Create a new hash with url and embedding
    post_hash = {
        "url": v['Url'],
        "image_url": v['ImageUrl'],
        "text": v['text'],
        "price": v['Price'],
        "embedding": vector
    }
 
    # create hash
    conn.hset(name=f"prod:{k}", mapping=post_hash)
 
p.execute()


SCHEMA = [
    TextField("text"),
    VectorField("embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}),
]

conn.ft("prods").create_index(fields=SCHEMA, definition=IndexDefinition(prefix=["prod:"], index_type=IndexType.HASH))

conn.close()

#### add image url-s
# for k,v in tqdm(product_metadata.items()):
#     conn.hset(f"prod:{k}",'image_url',v['ImageUrl'])
    