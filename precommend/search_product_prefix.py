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
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
from dotenv import load_dotenv

from tools import translator


load_dotenv(r'../.env')

import openai

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')
subscription_key=os.getenv('PREFIX_SEARCH_API')
headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': subscription_key,
}
btr="e551c239-d604-473c-8d48-ebcc46999c41"

def get_keywords(question):
    response = openai.Completion.create(
      engine="text-davinci-003-chatj",
      prompt=f"List in bullet points what the costumer is looking for in Hungarian: {question}",
      temperature=0.1,
      max_tokens=60,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )
    keywords=response["choices"][0]["text"].replace('\n','').split('• ')
    print(f"keywords extracted:{keywords}")
    return keywords
    # keyword=keywords[1]

def get_topk_related_product(question,top_k):
    print("Searching for similar products...")
    keyword=get_keywords(question)[1]

    params = urllib.parse.urlencode({
        # Request parameters
        'top': str(top_k),
        'pattern': keyword,
        'select': 'displayText, price, category, description, brand, url, imageUrl',
        #'storeId': '{string}',
    })
    page=1
    body=''

    brand_list=[]
    meta_list=[]
    try:
        conn = http.client.HTTPSConnection('api.prefixbox.com')
        conn.request("GET", f"/search/results?btr={btr}&page={page}&%s" % params, body, headers)
        response = conn.getresponse()
        data_json=json.loads(response.read())
        brand_list=[]
        meta_list=[]
        for prod_doc in data_json['documents']:
            # print(prod_doc)
            prod=prod_doc['document']
            soup = BeautifulSoup(prod['displayText']+' '+prod['description']+' '+prod['brand'])
            brand_list.append({'role': "assistant", "content": f"{soup.text}"})
            meta_list.append({'score':prod_doc['score'],'price':prod['price'],'brand':prod['brand'],'url':prod['url'],'image_url':prod['imageUrl']})
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

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