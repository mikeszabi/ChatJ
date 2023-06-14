# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 11:30:43 2023

@author: Szabi
"""


import re
import os
from precommend import search_product_prefix as search
from precommend import openai_recommend as recommend
import openai
from dotenv import load_dotenv

load_dotenv(r'../.env')


openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')
subscription_key=os.getenv('PREFIX_SEARCH_API')

def get_keywords(question):
    response = openai.Completion.create(
      engine="text-davinci-003-chatj",
      prompt=f"Extract product name keywords in relevancy order in Hungarian: {question}",
      temperature=0.5,
      max_tokens=60,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )
    resp=response["choices"][0]["text"].replace('\n','')

    keywords=re.split(r'\d.\s*',resp)[1:]

    print(f"keywords extracted from {question}:{keywords}")
    return keywords



search_engine=search.Search()
chat_handler=recommend.Recommend()
chat_handler.clear_messages()

top_k=10

# headers = {
#     # Request headers
#     'Ocp-Apim-Subscription-Key': subscription_key,
# }

# btr="e551c239-d604-473c-8d48-ebcc46999c41"


question='Fúrógépet keresek a nappalimban lévő polc felfúrására'
question='Kerti grillezéshez szeretnék faszenet vásárolni'
question='Milyen gömbgrillt ajánlasz?'
question='Kerti padot keresek, segtenél?'
question='Esetleg jól mutatna a kertben egy lampion is'
question='Jó minőségű faszenet keresek'
question='Looking for a knife sharpener'


chat_handler.append_message({"role": "user", "content": question})

keywords=recommend.get_keywords(question)
keywords=get_keywords(question)


search_item=search_engine.get_topk_related_product(keywords,top_k)

search_engine.search_history[0]['keywords']
search_engine.search_history[0]['products_found']

chat_handler.append_message(
    {"role": "assistant", "content": "Ezeket a  termékeket találtam:"})


products_list, meta_list=chat_handler.append_products(search_item,max_prod=1)

chat_handler.append_message(
    {"role": "assistant", "content": "Az ajánlatom: "})

comp_text=chat_handler.get_recommendation()

# response = openai.Completion.create(
#   engine="text-davinci-003-chatj",
#   prompt=f"Extract product names in relevancy order: {question}",
#   #prompt=f"Extract keywords in relevancy order: {question}",
#   temperature=0.3,
#   max_tokens=60,
#   top_p=1,
#   frequency_penalty=0.8,
#   presence_penalty=0.0
# )
# resp=response["choices"][0]["text"].replace('\n','')

# keywords=re.split(r'\d.\s*',resp)

# keyword=keywords[1]


# params = urllib.parse.urlencode({
#     # Request parameters
#     'top': '10',
#     'pattern': keyword,
#     'select': 'displayText, price, category, description, brand, url, imageUrl',
#     #'storeId': '{string}',
# })
# page=1
# body=''


# try:
#     conn = http.client.HTTPSConnection('api.prefixbox.com')
#     conn.request("GET", f"/search/results?btr={btr}&page={page}&%s" % params, body, headers)
#     response = conn.getresponse()
#     data_json=json.loads(response.read())
#     for prod_data in data_json['documents']:
#         print(prod_data)
#     conn.close()
# except Exception as e:
#     print("[Errno {0}] {1}".format(e.errno, e.strerror))
