#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 13:15:03 2023

@author: szabi
"""
import os
import requests, uuid
from dotenv import load_dotenv

load_dotenv(r'../config/.env')

def translate_ms(text):
    # Add your key and endpoint
    key = os.getenv('ITQS_AZURE_MSTRANSLATOR_KEY')
    endpoint = os.getenv('ITQS_AZURE_MSTRANSLATOR_ENDPOINT')

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "westeurope"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'hu',
        'to': ['en']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()
    
#     return json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    return response[0]["translations"][0]["text"]