#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 13:00:31 2023

@author: szabi
"""

import re
import os
import pandas as pd
import openai

from precommend import openai_recommend as recommend
from dotenv import load_dotenv

load_dotenv(r'../.env')


openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')


prompt="""
You will be provided with webshop queries. Classify each query into one or two primary categories and secondary categories. Provide your output in json format with the keys: primary and secondary.

Primary categories: General, Product Search, Product Information

General secondary categories:
- Welcoming
- Just chatting
- Not related to shopping


Product Search secondary categories:
- Having no clear idea
- search for a product category
- Search for a specific product
- Search for a product with specific price
- Search for a product with a specific attribute

Product Information secondary categories:
- General information about a product
- Specific information about a product
- Comparism of products
- How to use the product?
"""        

message_0=[{"role":"system","content":prompt}]

def identify_phase(messages):   
    cur_message=message_0 + messages
    response = openai.ChatCompletion.create(
      engine="gpt-35-turbo-deployment",
      messages = cur_message,
      temperature=0.7,
      max_tokens=800,
      top_p=0.95,
      frequency_penalty=0,
      presence_penalty=0,
      stop=None)
    return response['choices'][0]['message']['content']


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
questions.append('25000Ft alatti kerékpárt vásárolnék a feleségemnek')
questions.append('Bosch márkájút preferálom')
questions.append('Van esetleg piros is?')




df_res=pd.DataFrame(columns=['query','keywords','attributes','phases'])

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
    
    messages=[{"role":"user","content":question}]
    phase=identify_phase(messages)
    df_res.loc[i,'phases']=phase

   

