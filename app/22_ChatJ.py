# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

from bs4 import BeautifulSoup

import sys
sys.path.append(r'../')

import pandas as pd
import streamlit as st
# from streamlit_chat import message
from precommend import search_product_prefix as search
from precommend import openai_recommend as recommend

st.set_page_config(layout="wide")
st.title("ChatJ")


top_k=5

# @st.cache
# def streamlit_ui():
#   dummy_class = BackendLogic()


# products_list = []
# partner='praktiker'
col1, col2 = st.columns(2)


def clear_chat_data():
    chat_handler.store=st.session_state.store
    print(st.session_state.store)
    chat_handler.clear_messages()
    st.session_state.messages = []

        
# styl = """
# <style>
#     .stTextInput {
#         position: fixed;
#         bottom: 2rem;
#         background-color: white;
#         right:700  
#         left:500;
#         border-radius: 36px; 
#         z-index:4;
#     }
#     .stButton{
#         position: fixed;
#         bottom: 2rem;
#         left:500; 
#         right:500;
#         z-index:4;
#     }

#     @media screen and (max-width: 1000px) {
#         .stTextInput {
#             left:2%; 
#             width: 100%;
#             bottom: 2.1rem;  
#             z-index:2; 
#         }                        
#         .stButton {            
#             left:2%;  
#             width: 100%;       
#             bottom:0rem;
#             z-index:3; 
#         }          
#     } 

# </style>

# """

# Initialize state variables

print('###############')
if 'language' not in st.session_state:
    st.session_state.language='Hungarian'
if 'store' not in st.session_state:
    st.session_state.store='Praktiker'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'meta_list' not in st.session_state:
    st.session_state.meta_list = []
if 'chat_handler' not in st.session_state:
    search_engine=search.Search()
    chat_handler=recommend.Recommend()



# Sidebars
with st.sidebar:
    bt_lang_selector = st.radio(
        "Choose a language",
        ("Hungarian", "English"),
        on_change=clear_chat_data,
        key='language'
    )
    bt_prod_selector = st.radio(
        "Choose a store",
        ("Praktiker", "Rossmann"),
        on_change=clear_chat_data,
        key='store'
    )
    
    clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        

# Chat input
if prompt := st.chat_input("How can I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    chat_handler.append_message({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # message_placeholder = st.empty()
        
        keywords=recommend.get_keywords(prompt)
        
        if len(keywords):
            search_item=search_engine.get_topk_related_product(keywords,top_k,st.session_state.store)
            
            chat_handler.append_message({"role": "assistant", "content": "Ezeket a  termékeket találtam:"})
                      
            products_list, meta_list=chat_handler.append_products(search_item,max_prod=top_k)
            st.session_state.meta_list=meta_list
            
            chat_handler.append_message({"role": "assistant", "content": "Az ajánlatom: "})
            
            response=chat_handler.get_recommendation(st.session_state.language)
            st.session_state.messages.append({"role": "assistant", "content": response})
            chat_handler.append_message({"role": "assistant", "content": response})
            
           
        else:
            st.session_state.meta_list=[]
            st.session_state.messages.append({"role": "assistant", "content": "Nem találtam ilyen terméket, próbáljuk újra"})
            chat_handler.append_message(
                {"role": "assistant", "content": "Nem találtam ilyen terméket, próbáljuk újra"})

    with st.sidebar:            
        if len(search_engine.search_history):
            st.json(search_engine.search_history[-1]['keywords'])
            st.json(search_engine.search_history[-1]['products_found'])

    st.experimental_rerun()
        
with col1:
    df_meta=pd.DataFrame(st.session_state.meta_list)
    st.dataframe(df_meta)
with col2:    
    for i, row in df_meta.iterrows():
        st.image(
            row['image_url'],
            width=100, # Manually Adjust the width of the image as per requirement
     )
                
# # with col1:
# # df_meta=pd.DataFrame(st.session_state.meta_list)
#     # st.dataframe(df_meta)
# # with col2:    
# for meta in st.session_state.meta_list:
#     with col1:
#         st.image(
#             meta['image_url'],
#             width=100, # Manually Adjust the width of the image as per requirement
#             )
#     with col2:
#         st.json(meta)
        
        
            

            
            
         
