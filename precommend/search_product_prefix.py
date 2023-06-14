# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:06:58 2023

@author: Szabi
"""

################search
import sys
sys.path.append(r'../')
import os
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
from dotenv import load_dotenv

load_dotenv(r'../.env')


class Search:
    def __init__(self):
        # API parameters
        load_dotenv(r'../.env')

        
        # PREFIX
        # self.subscription_key=os.getenv('PREFIX_SEARCH_API')
        self.headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': os.getenv('PREFIX_SEARCH_API'),
        }
        self.btr="e551c239-d604-473c-8d48-ebcc46999c41"
        self.conn = http.client.HTTPSConnection('api.prefixbox.com')
        
        self.search_history=[]

    
    def __del__(self):
        self.conn.close()
 

    def get_topk_related_product(self,keywords,top_k):
        # The main seacrh function
        print("Searching for similar products...")
        search_item={}
        search_item['keywords']=keywords
        keyword=keywords[0]
    
        params = urllib.parse.urlencode({
            # Request parameters
            'top': str(top_k),
            'pattern': keyword,
            'select': 'displayText, price, category, description, brand, url, imageUrl',
            #'storeId': '{string}',
        })
    
        search_item['products_found']=[]
        # products_list=[]
        # meta_list=[]
        try:
            self.conn.request("GET", f"/search/results?btr={self.btr}&page={1}&%s" % params, '', self.headers)
            response = self.conn.getresponse()
            data_json=json.loads(response.read())
            search_item['products_found']=[]
            for prod_json in data_json['documents']:
                search_item['products_found'].append(prod_json)
            
            
            # products_list=[]
            # meta_list=[]
            # for prod_doc in data_json['documents']:
            #     # print(prod_doc)
            #     prod=prod_doc['document']
            #     soup = BeautifulSoup(prod['displayText']+' '+prod['description']+' '+prod['brand'])
            #     products_list.append({'role': "assistant", "content": f"{soup.text}"})
            #     meta_list.append({'score':prod_doc['score'],'price':prod['price'],'brand':prod['brand'],'url':prod['url'],'image_url':prod['imageUrl']})
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
        self.search_history.append(search_item)
        
        return search_item
            

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