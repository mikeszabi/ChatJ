# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 10:32:44 2023

@author: Szabi
"""


########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '{subscription key}',
}

btr="e551c239-d604-473c-8d48-ebcc46999c41"

params = urllib.parse.urlencode({
    # Request parameters
    'top': '3',
    'pattern': 'fűnyíró',
    'select': 'displayText, price, category, brand',
    #'storeId': '{string}',
})

try:
    conn = http.client.HTTPSConnection('api.prefixbox.com')
    conn.request("GET", "/search/results?btr={btr}&page={page}&%s" % params, "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

####################################