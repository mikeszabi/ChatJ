# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

from bs4 import BeautifulSoup

import sys
sys.path.append(r'../')

import pandas as pd
import streamlit as st
from streamlit_chat import message
from precommend import search_product_db as search

st.set_page_config(layout="wide")

products_list = []
partner='praktiker'
col1, col2, col3= st.columns(3)
initial_message_object={"role": "system", "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."}


def clear_text_input():
    # clear_chat_data()
    with col1:
        st.session_state['question'] = st.session_state['input']
        st.session_state['input'] = ""
    message_objects = st.session_state['messages']
    products_list = []

def clear_chat_data():
    message_objects = []
    message_objects.append(initial_message_object)
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
    st.session_state['messages'] = []
        
def trim_messages(message_objects,max_l=10):
    message_objects_trimmed=message_objects[len(message_objects)-max_l:]
    message_objects = []
    message_objects.append(initial_message_object)
    message_objects.extend(message_objects_trimmed)
    return message_objects
    

# Initialize state variables
if 'conn' not in st.session_state:
    st.session_state['conn']=search.connect2redis()
    print('###############')
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'messages' not in st.session_state:
    message_objects = []
    message_objects.append(initial_message_object)
    st.session_state['messages'] = message_objects
else:
    message_objects = st.session_state['messages']


# Sidebars
with st.sidebar:
    bt_lang_selector = st.radio(
        "Choose a language",
        ("Hungarian", "English")
    )
    bt_prod_selector = st.radio(
        "Choose a partner",
        ("Praktiker", "Rossman")
    )

if bt_lang_selector == 'English':
    lang='en'
else:
    lang='hu'
    
if bt_prod_selector == 'Praktiker':
    partner='praktiker'
elif bt_prod_selector == 'Rossman':
    partner='rossman'


# Chat input
with col1:
    st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
    clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

# QUESTION PROCESSING
if st.session_state['question']:
    question = st.session_state['question']
    print("Messages object before run: ", len(message_objects))
    message_objects.append({"role": "user", "content": question})
    
    query_vector=search.get_customer_question_embeddings(question)
    brand_list, meta_list=search.get_topk_related_product(query_vector, st.session_state['conn'], partner, 'prod', language=lang, top_k=5, sim_tsh=0.25)

    if len(brand_list)<4:
        brand_list_2, meta_list_2=search.get_topk_related_product(query_vector, st.session_state['conn'], partner, 'desc', language=lang, top_k=5,sim_tsh=0.25)
        brand_list.extend(brand_list_2)
        meta_list.extend(meta_list_2)
        
    if len(brand_list)>0:
        message_objects.append({"role": "assistant", "content": "A következő releváns termékeket találtam"})
        message_objects.extend(brand_list)
        message_objects.append({"role": "assistant", "content": "Íme az ajánlásom"})
    else:
        message_objects.append({"role": "assistant", "content": "Pontosítsd a kérdést, erre nem volt találat"})

    result = search.get_recommendation(message_objects,language=lang)
    message_objects.append({"role": "assistant", "content": result})
    
    st.session_state['chat_history'].append((question, result))
    st.session_state['messages'] = message_objects
    
    #print("Result: ", result)
    print("Messages object after run: ", len(message_objects))
    
    with col2:
        df_meta=pd.DataFrame(meta_list)
        st.dataframe(df_meta)
    with col3:    
        for i, row in df_meta.iterrows():
            st.image(
            row['image_url'],
            width=100, # Manually Adjust the width of the image as per requirement
        )

if len(message_objects)>15:
    message_objects=trim_messages(message_objects,max_l=8)
    st.session_state['messages']= message_objects

if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        with col1:
            message(st.session_state['chat_history'][i][1], key=str(i))
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
