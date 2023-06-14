#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 13:15:03 2023

@author: szabi
"""
import os
import requests, uuid
from dotenv import load_dotenv
# from argostranslate import translate
import openai

load_dotenv(r'../.env')
openai.api_type = "azure"
openai.api_key = os.getenv('PREFIX_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('PREFIX_AZURE_API_BASE')
openai.api_version = os.getenv('PREFIX_AZURE_API_VERSION')

def translate_ms(text):
    # Add your key and endpoint
    key = os.getenv('AZURE_MSTRANSLATOR_KEY')
    endpoint = os.getenv('AZURE_MSTRANSLATOR_ENDPOINT')

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



def translate_openai(text,instruction='Translate this text to English:'):
    response = openai.Completion.create(
      engine="text-davinci-003-chatj",
      prompt=f"{instruction}:{text}",
      temperature=0.3,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    return(response["choices"][0]["text"])


#https://www.argosopentech.com/argospm/index/

# def translate_argos(text):
    
    
# from_code = "hu"
# to_code = "en"
    
# import argostranslate.package
# argostranslate.package.update_package_index()
# available_packages = argostranslate.package.get_available_packages()
# package_to_install = next(
#     filter(
#         lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
#     )
# )
# argostranslate.package.install_from_path(package_to_install.download())

# translatedText = argostranslate.translate.translate("Észrevettem, hogy kalimpálok a lábaimmal és veszettül kényelmetlenül érzem magam", from_code, to_code)
