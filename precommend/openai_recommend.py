# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 14:06:32 2023

@author: Szabi
"""
import os
import re
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
import openai
from tools import translator


load_dotenv(r'../.env')

openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')

initial_message_objects={}
initial_message_objects['Praktiker']={"role": "system", 
                             "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."}

# 'I want you to act as a DIY expert. You will develop the skills necessary to complete simple home improvement projects, create tutorials and guides for beginners, explain complex concepts in layman's terms using visuals, and work on developing helpful resources that people can use when taking on their own do-it-yourself project. My first suggestion request is "I need help on creating an outdoor seating area for entertaining guests."

initial_message_objects['Rossmann']={"role": "system", 
                             "content": "Egy chatbot vagy, aki egy drogéria termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."}

class Recommend():
    def __init__(self):
        self.store='Praktiker'
        self.initial_message_object=initial_message_objects['Praktiker']

        self.questions=[]
        self.message_objects=[]
        self.message_objects.append(self.initial_message_object)
        self.search_history=[]
        
    def clear_messages(self):
        self.message_objects = []
        print(initial_message_objects[self.store])
        self.message_objects.append(initial_message_objects[self.store])
    
    # def trim_messages(self,max_l=10):
    #     message_objects_trimmed=self.message_objects[len(self.message_objects)-max_l:]
    #     self.message_objects = []
    #     self.message_objects.append(self.initial_message_object)
    #     self.message_objects.extend(message_objects_trimmed)
        
    def append_message(self,new_message_object):
        self.message_objects.append(new_message_object)
        
    def append_products(self,search_item,max_prod=3):
        products_list=[]
        meta_list=[]
        i=0
        if 'products_found' in search_item:
            for prod_json in search_item['products_found']:
                if i>=max_prod:
                    break
                prod=prod_json['document']
                if 'description' in prod.keys():
                    soup = BeautifulSoup(prod['displayText']+' '+prod['description']+' '+prod['brand'])
                else:
                    soup = BeautifulSoup(prod['displayText']+' '+prod['brand'])                
                new_message_object={'role': "assistant", "content": f"{soup.text}"}
                self.append_message(new_message_object)
                products_list.append(new_message_object)
                meta_list.append({'score':prod_json['score'],'price':prod['price'],'brand':prod['brand'],'url':prod['url'],'image_url':prod['imageUrl']})
                i+=1
                self.search_hist_item={}
                self.search_hist_item['search_item']=search_item
                self.search_hist_item['products_list']=products_list
                self.search_hist_item['meta_list']=meta_list
            
        return products_list, meta_list
        

    def get_recommendation(self,language='Hungarian',max_message=10):
        completion = openai.ChatCompletion.create(
            engine="gpt-35-turbo-deployment",
            messages=self.message_objects[-max_message:]
        )
        comp_text=completion.choices[0].message['content']
        if language=='English':
            comp_text=translator.translate_openai(comp_text)
        return comp_text
    
def get_keywords(question):
    response = openai.Completion.create(
      engine="text-davinci-003-chatj",
      #prompt=f"Extract product name keywords in relevancy order in Hungarian: {question}",
      prompt=f"Listázz magyarul 3 kulcsszót, amit keres a vásárló: {question}",
      temperature=0.1,
      max_tokens=60,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )
    resp=response["choices"][0]["text"].replace('\n','')

    keywords=re.split(r'\d.\s*',resp)[1:]

    print(f"keywords extracted from {question}:{keywords}")
    return keywords

def get_attributes(question):
    response = openai.Completion.create(
      engine="text-davinci-003-chatj",
      prompt=f"Listázz magyarul 3 termék jellemző kulcsszót, ami fontos a vásárlónak: {question}",
      temperature=0.1,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.8,
      presence_penalty=0.0
    )
    resp=response["choices"][0]["text"].replace('\n','')

    keywords=re.split(r'\d.\s*',resp)[1:]

    print(f"attributes extracted from {question}:{keywords}")
    return keywords
