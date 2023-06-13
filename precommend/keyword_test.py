# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 11:30:43 2023

@author: Szabi
"""
import os
from dotenv import load_dotenv
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
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


question='Fúrógépet keresek a nappalimban lévő polc felfúrására'
question='Kerti grillezéshez szeretnék faszenet vásárolni'
question='Milyen gömbgrillt ajánlasz?'

response = openai.Completion.create(
  engine="text-davinci-003-chatj",
  prompt=f"Extract keywords from this text: {question}",
  temperature=0.5,
  max_tokens=60,
  top_p=1.0,
  frequency_penalty=0.8,
  presence_penalty=0.0
)
keywords=response["choices"][0]["text"].replace('\n','').split('-')

keyword=keywords[1]


params = urllib.parse.urlencode({
    # Request parameters
    'top': '3',
    'pattern': keyword,
    'select': 'displayText, price, category, description, brand, url, imageUrl',
    #'storeId': '{string}',
})
page=1
body=''


try:
    conn = http.client.HTTPSConnection('api.prefixbox.com')
    conn.request("GET", f"/search/results?btr={btr}&page={page}&%s" % params, body, headers)
    response = conn.getresponse()
    data_json=json.loads(response.read())
    for prod_data in data_json['documents']:
        print(prod_data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))
