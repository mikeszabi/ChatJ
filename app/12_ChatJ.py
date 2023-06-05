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
col1, col2, col3= st.columns(3)


def clear_text_input():
    # clear_chat_data()
    with col1:
        st.session_state['question'] = st.session_state['input']
        st.session_state['input'] = ""
    message_objects = st.session_state['messages']
    products_list = []

def clear_chat_data():
    message_objects = []
    message_objects.append({"role": "system", 
                            "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})
    
    with col1:
        st.session_state['input'] = ""
        st.session_state['chat_history'] = []
        st.session_state['messages'] = []

conn=search.connect2redis()

# Initialize chat history
if 'question' not in st.session_state:
    with col1:
        st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    with col1:
        st.session_state['chat_history'] = []
if 'messages' not in st.session_state:
    message_objects = []
    message_objects.append({"role": "system",
                            "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})
    with col1:
        st.session_state['messages'] = message_objects
else:
    message_objects = st.session_state['messages']

# Chat 
with col1:
    st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

with st.sidebar:
    add_radio = st.radio(
        "Choose a language",
        ("Hungarian", "English")
    )

if add_radio == 'English':
    lang='en'
else:
    lang='hun'

if st.session_state['question']:
    question = st.session_state['question']
    print("Object before run: ", message_objects)
    message_objects.append({"role": "user", "content": question})
    query_vector = search.get_customer_question_embeddings(question)
    brand_list, meta_list = search.get_topk_related_product(query_vector, conn, language=lang, k=3)
    products_list.extend(brand_list)
    
    message_objects.append({"role": "assistant", "content": "Ezeket a termékeket találtam:"})
    message_objects.extend(products_list)
    message_objects.append({"role": "assistant", "content": "Ezek közül a következőt ajánlom: "})

    result = search.get_recommendation(message_objects,language=lang)
    message_objects.append({"role": "assistant", "content": result})
    with col1:
        st.session_state['chat_history'].append((question, result))
        st.session_state['messages'] = message_objects
        print("Result: ", result)
        print("Messages object: ", message_objects)
    with col2:
        df_meta=pd.DataFrame(meta_list)
        st.dataframe(df_meta)
    with col3:    
        for i, row in df_meta.iterrows():
            st.image(
            row['image_url'],
            width=100, # Manually Adjust the width of the image as per requirement
        )

if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        with col1:
            message(st.session_state['chat_history'][i][1], key=str(i))
            message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')
