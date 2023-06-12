# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 11:30:43 2023

@author: Szabi
"""
import os
from dotenv import load_dotenv


load_dotenv(r'../.env')

import openai

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')


question='Fúrógépet keresek a nappalimban lévő polc felfúrására'
question='Kerti grillezéshez szeretnék faszenet vásárolni'
question='Milyen gömbgrillt ajánlasz?'


response = openai.Completion.create(
  engine="text-davinci-003-chatj",
  prompt=f"Translate this DIY product text into English:{question}",
  temperature=0.3,
  max_tokens=100,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
)
question=response["choices"][0]["text"]

response = openai.Completion.create(
  engine="text-davinci-003-chatj",
  prompt=f"Extract keywords from this text: {question}",
  temperature=0.5,
  max_tokens=60,
  top_p=1.0,
  frequency_penalty=0.8,
  presence_penalty=0.0
)
response["choices"][0]["text"].replace('\n','').split('-')

response["choices"][0]["text"]