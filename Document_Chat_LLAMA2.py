#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from llama_index import download_loader, VectorStoreIndex
import tempfile

# Function to create query engine from the document
def create_query_engine(document_path, doc_type):
    if doc_type == 'docx':
        DocxReader = download_loader("DocxReader")
        loader = DocxReader()
    elif doc_type == 'pdf':
        PDFMinerReader = download_loader("PDFMinerReader")
        loader = PDFMinerReader()
    else:
        raise ValueError("Unsupported document type")

    documents = loader.load_data(file=Path(document_path))
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine()

# Load .env and set API Key
load_dotenv(find_dotenv())
with st.sidebar:
    api_key = st.text_input('OpenAI API Key:', type='password')
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key

# Streamlit app main body
st.title("Document Chat")

# Document upload
uploaded_file = st.file_uploader("Choose a document", type=['docx', 'pdf'])
if uploaded_file is not None:
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name[-5:]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Process the file
    doc_type = 'docx' if uploaded_file.name.endswith('.docx') else 'pdf'
    query_engine = create_query_engine(tmp_path, doc_type)

    # Query interface
    query = st.text_input("Enter your query here")
    if query:
        response_obj = query_engine.query(query)
        response_text = response_obj.response  # Extracting only the response text
        st.text("Response:")
        st.write(response_text)


# In[ ]:




