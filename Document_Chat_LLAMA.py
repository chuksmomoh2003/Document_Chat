#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from pathlib import Path
from llama_index import download_loader, VectorStoreIndex
import os
import tempfile
import shutil
from dotenv import load_dotenv, find_dotenv
import difflib

# Function to process documents and create a query engine based on the notebooks
def load_and_index_document(uploaded_file):
    try:
        # Create a temporary file to save the uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as temp_file:
            # Write the content of the uploaded file to the temporary file
            shutil.copyfileobj(uploaded_file, temp_file)
            temp_file_path = temp_file.name

        if uploaded_file.type == "application/pdf":
            loader = download_loader("PDFMinerReader")()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            loader = download_loader("DocxReader")()
        else:
            st.error("Unsupported file type: " + uploaded_file.type)
            return None

        documents = loader.load_data(file=Path(temp_file_path))
        index = VectorStoreIndex.from_documents(documents)
        return index.as_query_engine()

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

# Function to check if two strings are similar
def is_similar(str1, str2, threshold=0.8):
    similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
    return similarity > threshold

# Function to get unique answers for the queries
def get_answer(query, query_engines):
    responses = []
    for qe in query_engines:
        response = str(qe.query(query))
        if not any(is_similar(response, existing_response) for existing_response in responses):
            responses.append(response)
    return "\n\n".join(responses)

# Initialize session state keys
if 'query_engines' not in st.session_state:
    st.session_state['query_engines'] = []
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Streamlit UI
st.image('docusearch.png')
st.title("Document Chat")

# Load .env and set API Key
load_dotenv(find_dotenv())
with st.sidebar:
    api_key = st.text_input('OpenAI API Key:', type='password')
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

# File Uploader
uploaded_files = st.file_uploader("Upload Documents", accept_multiple_files=True, type=['pdf', 'docx'])
for uploaded_file in uploaded_files:
    if uploaded_file is not None:
        # Load and index the document
        qe = load_and_index_document(uploaded_file)
        if qe:
            st.session_state['query_engines'].append(qe)
            st.success(f"Loaded and indexed {uploaded_file.name}")

# Chat Interface
user_query = st.text_input("Ask a question about the documents:")
if user_query:
    answer = get_answer(user_query, st.session_state['query_engines'])
    # Append the query and answer to the chat history
    st.session_state['chat_history'].append((user_query, answer))

# Display Chat History
for i, (q, a) in enumerate(reversed(st.session_state['chat_history'])):
    st.text_area(f"Q{i+1}: {q}", value=a, height=100, disabled=False)


# In[ ]:





# In[ ]:




