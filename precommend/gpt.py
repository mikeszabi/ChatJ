import openai
import pandas as pd
from openai.embeddings_utils import get_embedding,cosine_similarity
import json
import os
import ast
import streamlit as st
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv(r'../.env')

openai.api_type = "azure"
openai.api_key = os.getenv('ITQS_AZURE_OPENAI_KEY')
openai.api_base = os.getenv('ITQS_AZURE_API_BASE')
openai.api_version = os.getenv('ITQS_AZURE_API_VERSION')

data_path=r'../data'
tqdm.pandas()

partner='praktiker'

def prepare_dataset(df):
    df['Category'] = df['Category'].apply(lambda x: x.replace("/", " "))
    df['combined'] = df.apply(lambda row: f"{row['Category']}, {row['Description']}", axis=1)
    df['text_embedding'] = df.combined.progress_apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))
    return df

def get_customer_question_embeddings(customer_input):
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
@st.experimental_memo
def get_dataset():
    if os.path.exists(r"../data/prep_products_"+partner+".csv"):
        prep_data = pd.read_csv(r"../data/prep_products_"+partner+".csv")
        prep_data["text_embedding"] = prep_data["text_embedding"].apply(lambda x: ast.literal_eval(x))
    else:
        print("Preparing dataset, it may takes a few minutes....")
        product_data_df = pd.read_json(os.path.join(data_path,"products_"+partner+".json"))
        prep_data = prepare_dataset(product_data_df)
        prep_data.to_csv("../data/prep_products_"+partner+".csv")

    print("Loaded...")
    return prep_data


if __name__ == '__main__':
    
    ### read and preprocess data
    product_data_df = pd.read_json(os.path.join(data_path,"products_"+partner+".json"))
    #product_data_df = product_data_df[product_data_df["Availability"]=="in stock"]
    if os.path.exists(r"../data/prep_products_"+partner+".csv"):
        prep_data = pd.read_csv(r"../data/prep_products_"+partner+".csv")
    else:
        prep_data = prepare_dataset(product_data_df)
        prep_data.to_csv("../data/prep_products_"+partner+".csv")