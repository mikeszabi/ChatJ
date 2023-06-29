# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 11:30:43 2023

@author: Szabi
"""


import re
import os
import pandas as pd
import openai

from precommend import search_product_prefix as search
from precommend import search_product_db as search_db
from precommend import openai_recommend as recommend
from dotenv import load_dotenv

load_dotenv(r'../.env')


openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')
subscription_key=os.getenv('PREFIX_SEARCH_API')


search_engine=search.Search()

# chat_handler=recommend.Recommend()
# chat_handler.clear_messages()
top_k=3

conn=search_db.connect2redis()
partner='praktiker'

# headers = {
#     # Request headers
#     'Ocp-Apim-Subscription-Key': subscription_key,
# }

# btr="e551c239-d604-473c-8d48-ebcc46999c41"

questions=[]
questions.append('Hello')
questions.append('Fúrógépet keresek a nappalimban lévő polc felfúrására')
questions.append('Kerti grillezéshez szeretnék faszenet vásárolni')
questions.append('Milyen gömbgrillt ajánlasz?')
questions.append('Kerti padot keresek, segtenél?')
questions.append('Esetleg jól mutatna a kertben egy lampion is')
questions.append('Jó minőségű faszenet keresek')
questions.append('Looking for a knife sharpener')
questions.append('Akkumulátoros fűnyírót keresek')
questions.append('Gyümölcsfát szeretnék venni')
questions.append('I want to buy screws for concrete wall')
questions.append('Do you sell accumulator for Bosch lawn mower?')
questions.append('Melyik a legstrapabíróbb talicska?')
questions.append('Olcsó, akciós rattan kerti bútort keresek')
questions.append('Barkácsolni szeretnék, van ötleted?')


df_res=pd.DataFrame(columns=['query','keywords','attributes','prod_keyword','prod_vs','prod_en_vs','desc_vs','desc_en_vs'])

for i,question in enumerate(questions):
    # chat_handler.append_message({"role": "user", "content": question})
    
    df_res.loc[i,'query']=question
    ########
    # keywords=recommend.get_keywords(question)
    keywords=recommend.get_keywords(question)
    
    keyword_str=''.join('- '+k+',\n' for k in keywords)
    df_res.loc[i,'keywords']=keyword_str
    
    attributes=recommend.get_attributes(question)
    attributes_str=''.join('- '+k+',\n' for k in attributes)
    df_res.loc[i,'attributes']=attributes_str
    
    search_item=search_engine.get_topk_related_product(keywords,top_k,'Praktiker')
    if 'products_found' in search_item:
        prods=[p['document']['displayText'] for p in search_item['products_found']]
        prod_str=''.join('- '+k+',\n' for k in prods)
        df_res.loc[i,'prod_keyword']=prod_str
    
    # search_engine.search_history[0]['keywords']
    # search_engine.search_history[0]['products_found']
    
    ########

    
    query_vector=search_db.get_customer_question_embeddings(question)
    language='hu'
    field='prod'
    brand_list, meta_list=search_db.get_topk_related_product(query_vector, conn, partner, field=field, language='hu', top_k=top_k, sim_tsh=0.25)
    prods=[p['prod'] for p in meta_list]
    prod_str=''.join('- '+k+',\n' for k in prods)
    df_res.loc[i,'prod_vs']=prod_str


    language='en'
    field='prod'
    brand_list, meta_list=search_db.get_topk_related_product(query_vector, conn, partner, field=field, language='en', top_k=top_k, sim_tsh=0.25)
    prods=[p['prod'] for p in meta_list]
    prod_str=''.join('- '+k+',\n' for k in prods)
    df_res.loc[i,'prod_en_vs']=prod_str


    language='hu'
    field='desc'
    brand_list, meta_list=search_db.get_topk_related_product(query_vector, conn, partner, field=field, language='hu', top_k=top_k, sim_tsh=0.25)
    prods=[p['prod'] for p in meta_list]
    prod_str=''.join('- '+k+',\n' for k in prods)
    df_res.loc[i,'desc_vs']=prod_str


    language='en'
    field='desc'
    brand_list, meta_list=search_db.get_topk_related_product(query_vector, conn, partner, field=field, language='en', top_k=top_k, sim_tsh=0.25)
    prods=[p['prod'] for p in meta_list]
    prod_str=''.join('- '+k+',\n' for k in prods)
    df_res.loc[i,'desc_en_vs']=prod_str

df_res.to_csv(r'../data/search_test_20230629.csv',encoding='utf-8-sig',sep=';',)

#############

# chat_handler.append_message(
#     {"role": "assistant", "content": "Ezeket a  termékeket találtam:"})


# products_list, meta_list=chat_handler.append_products(search_item,max_prod=1)

# chat_handler.append_message(
#     {"role": "assistant", "content": "Az ajánlatom: "})

# comp_text=chat_handler.get_recommendation()

# # response = openai.Completion.create(
# #   engine="text-davinci-003-chatj",
# #   prompt=f"Extract product names in relevancy order: {question}",
# #   #prompt=f"Extract keywords in relevancy order: {question}",
# #   temperature=0.3,
# #   max_tokens=60,
# #   top_p=1,
# #   frequency_penalty=0.8,
# #   presence_penalty=0.0
# # )
# # resp=response["choices"][0]["text"].replace('\n','')

# # keywords=re.split(r'\d.\s*',resp)

# # keyword=keywords[1]


# # params = urllib.parse.urlencode({
# #     # Request parameters
# #     'top': '10',
# #     'pattern': keyword,
# #     'select': 'displayText, price, category, description, brand, url, imageUrl',
# #     #'storeId': '{string}',
# # })
# # page=1
# # body=''


# # try:
# #     conn = http.client.HTTPSConnection('api.prefixbox.com')
# #     conn.request("GET", f"/search/results?btr={btr}&page={page}&%s" % params, body, headers)
# #     response = conn.getresponse()
# #     data_json=json.loads(response.read())
# #     for prod_data in data_json['documents']:
# #         print(prod_data)
# #     conn.close()
# # except Exception as e:
# #     print("[Errno {0}] {1}".format(e.errno, e.strerror))
