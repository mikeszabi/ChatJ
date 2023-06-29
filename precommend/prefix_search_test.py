# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 10:32:44 2023

@author: Szabi
"""

import os
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
from dotenv import load_dotenv

load_dotenv(r'../.env')

subscription_key=os.getenv('PREFIX_SEARCH_API')

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': subscription_key,
}

btr="e551c239-d604-473c-8d48-ebcc46999c41"

params = urllib.parse.urlencode({
    # Request parameters
    'top': '3',
    'pattern': 'fűnyíró',
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
    len(data_json['documents'])
    data_json['documents'][0]
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################