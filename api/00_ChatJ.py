# https://blog.streamlit.io/ai-talks-chatgpt-assistant-via-streamlit/

import sys
sys.path.append(r'../')

import streamlit as st
from streamlit_chat import message
from precommend import gpt
from tools import translator


products_list = []

data_df =gpt.get_dataset()

def clear_text_input():
    # clear_chat_data()
    st.session_state['question'] = st.session_state['input']
    st.session_state['input'] = ""
    message_objects = st.session_state['messages']
    products_list = []

def clear_chat_data():
    message_objects = []
    message_objects.append({"role": "system", "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
    st.session_state['messages'] = []

# Initialize chat history
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'messages' not in st.session_state:
    message_objects = []
    message_objects.append({"role": "system",
                            "content": "Egy chatbot vagy, aki egy barkácsáruház termékeivel kacsolatban válaszolsz kérdésekre és ajánlásokat adsz."})
    st.session_state['messages'] = message_objects
else:
    message_objects = st.session_state['messages']

# Chat 
st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

if st.session_state['question']:
    question = st.session_state['question']
    print("Object before run: ", message_objects)
    message_objects.append({"role": "user", "content": question})
    trans_q = translator.translate_ms(question)
    customer_embed = gpt.get_customer_question_embeddings(trans_q)
    top3_df = gpt.get_topk_related_product(data_df, 3, customer_embed)
    for index, row in top3_df.iterrows():
        brand_dict = {'role': "assistant", "content": f"{row['combined']}"}
        products_list.append(brand_dict)
    message_objects.append({"role": "assistant", "content": f"Ezt a 3 terméket találtam:"})
    message_objects.extend(products_list)
    message_objects.append(
        {"role": "assistant", "content": "Ezek közül a következőt ajánlom: "})

    result = gpt.get_recommendation(message_objects)
    message_objects.append({"role": "assistant", "content": result})
    st.session_state['chat_history'].append((question, result))
    st.session_state['messages'] = message_objects
    print("Result: ", result)
    print("Messages object: ", message_objects)



if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        message(st.session_state['chat_history'][i][1], key=str(i))
        # st.markdown(f'\n\nSources: {st.session_state["source_documents"][i]}')
        message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')