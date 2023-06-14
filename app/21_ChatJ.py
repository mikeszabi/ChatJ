# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

from bs4 import BeautifulSoup

import sys
sys.path.append(r'../')

import pandas as pd
import streamlit as st
from streamlit_chat import message
from precommend import search_product_prefix as search
from precommend import openai_recommend as recommend

st.set_page_config(layout="wide")

top_k=5

# @st.cache
# def streamlit_ui():
#   dummy_class = BackendLogic()


# products_list = []
# partner='praktiker'
col1, col2, col3= st.columns(3)


def clear_text_input():
    # clear_chat_data()
    st.session_state['question'] = st.session_state['input']
    st.session_state['input'] = ""


def clear_chat_data():
    chat_handler.clear_messages()
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
        

# Initialize state variables

print('###############')
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'chat_handler' not in st.session_state:
    search_engine=search.Search()
    chat_handler=recommend.Recommend()
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

    chat_handler.append_message({"role": "user", "content": question})
    
    keywords=recommend.get_keywords(question)
    
    search_item=search_engine.get_topk_related_product(keywords,top_k)
    
    search_engine.search_history[0]['keywords']
    search_engine.search_history[0]['products_found']
    
    chat_handler.append_message(
        {"role": "assistant", "content": "Ezeket a  termékeket találtam:"})
    
    
    products_list, meta_list=chat_handler.append_products(search_item,max_prod=3)
    
    chat_handler.append_message(
        {"role": "assistant", "content": "Az ajánlatom: "})
    
    result=chat_handler.get_recommendation()
    
    st.session_state['chat_history'].append((question, result))
    
    #print("Result: ", result)
    #print("Messages object after run: ", len(message_objects))
    
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
