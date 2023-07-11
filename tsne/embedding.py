# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 22:22:38 2023

@author: Szabi
"""
import requests
import sys
sys.path.append(r'../')

import pandas as pd
from tqdm import tqdm
import os
import numpy as np
import redis


# import json
# import ast
from dotenv import load_dotenv

load_dotenv(r'../.env')

redis_host = os.getenv('PREFIX_AZURE_REDIS_HOST_ENDPOINT')
redis_port = os.getenv('PREFIX_AZURE_REDIS_PORT')
redis_password = os.getenv('PREFIX_AZURE_REDIS_KEY')


data_path=r'../data'
tqdm.pandas()

partner='praktiker' # rossmann


base_dir=r'd:\WEB'
project='praktiker'

image_dir=os.path.join(base_dir,'Images',project)

vector_out_folder=os.path.join(base_dir,'Outputs',project,'output','image_vectors')

    
# Connect to the Redis server
conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

not_downloaded=[]

for key in tqdm(conn.scan_iter("praktiker*")): # in conn.keys()
    image_name=key.decode('utf-8').split(':')[1]+'.png'
    vector_name=key.decode('utf-8').split(':')[1]+'.npy'
    image_path=os.path.join(image_dir,image_name)
    vector_path=os.path.join(vector_out_folder,vector_name)
    
    if not os.path.exists(image_path):
        h=conn.hgetall(key)  
        image_url=h[b'image_url']
    
    # print(image_url)
        try:
            response = requests.get(image_url)
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            image_vector=np.frombuffer(h[b'embedding_description_en'],dtype=np.float32)
            np.save(vector_path, image_vector)
        except:
            not_downloaded.append(key)
    
    
conn.close()  