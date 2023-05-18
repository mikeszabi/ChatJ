import openai
import pandas as pd
from openai.embeddings_utils import get_embedding,cosine_similarity
import requests, uuid, json
import os
import ast
import streamlit as st

openai.api_type = "azure"
openai.api_key = "c4a1d51a3b974ac6b0ac45b3db2cd7b4"
openai.api_base = "https://cheppy.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

def translate(text):
    # Add your key and endpoint
    key = "c3cc6068a4664a27ab85c48d39082489"
    endpoint = "https://api.cognitive.microsofttranslator.com/"

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

def prepare_dataset(df):
    df['Category'] = df['Category'].apply(lambda x: x.replace("/", " "))
    df['combined'] = df.apply(lambda row: f"{row['Category']}, {row['Description']}", axis=1)
    df['text_embedding'] = df.combined.apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))
    return df

def get_cutomer_question_embeddings(customer_input):
    response = openai.Embedding.create(
        input=customer_input,
        engine="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def get_topk_related_product(df, k, embeddings_customer_question):
    df['search_products'] = df.text_embedding.apply(
        lambda x: cosine_similarity(x, embeddings_customer_question))
    products_available = df.sort_values('search_products', ascending=False)
    return products_available.head(k)

def get_recommendation(chat_history):
    completion = openai.ChatCompletion.create(
        engine="GPT35",
        messages=chat_history
    )

    return completion.choices[0].message['content']
@st.cache_data
def get_dataset():
    if os.path.exists("data/prep_data.csv"):
        prep_data = pd.read_csv("data/prep_data.csv")
        prep_data["text_embedding"] = prep_data["text_embedding"].apply(lambda x: ast.literal_eval(x))
    else:
        "Preparing dataset, it may takes a few minutes...."
        product_data_df = pd.read_json("data/data.json")
        products_available = product_data_df[product_data_df["Availability"] == "in stock"]
        prep_data = prepare_dataset(products_available)
        prep_data.to_csv("data/prep_data.csv")

    print("Loaded...")
    return prep_data





if __name__ == '__main__':
    product_data_df = pd.read_json("/media/itqs/10_TB_Hdd/Tamas/chatgpt-product-recommendation-embeddings/data/data.json")
    products_available = product_data_df[product_data_df["Availability"]=="in stock"]
    if os.path.exists("../data/prep_data.csv"):
        prep_data = pd.read_csv("../data/prep_data.csv")
    else:
        prep_data = prepare_dataset(products_available)
        prep_data.to_csv("../data/prep_data.csv")