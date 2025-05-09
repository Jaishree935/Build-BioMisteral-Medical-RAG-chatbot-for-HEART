# -*- coding: utf-8 -*-
"""Medical_chatbot_for_Heart.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13mEhvYbHRQDTClsZPBd2nDOyUeLjyEPU

# **Build BioMistral Medical RAG Chatbot using BioMistral Open Source LLM**

In the notebook we will build a Medical Chatbot with BioMistral LLM and Heart Health pdf file
BioMistral Medical RAG Chatbot, designed to answer heart health-related questions using an AI model specifically trained on medical information.

# Load the Google Drive
"""

from google.colab import drive
drive.mount('/content/drive')

"""#  Installation"""

!pip install langchain sentence-transformers chromadb llama-cpp-python langchain_community pypdf

"""# Importing Libraries"""

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA, LLMChain

"""# Import the document"""

loader=PyPDFDirectoryLoader("/content/drive/MyDrive/BioMistral/Data")
docs=loader.load()

len(docs) #number of pages -each page consider as a document

docs[5]

"""# Chunking"""

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

len(chunks)

chunks[50]

"""# Embedding Creation"""

import os
os.environ['HUGGINGFACEHUB_API_TOKEN']="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"

embeddings= SentenceTransformerEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")

"""# Vector Store Creation"""

vectorstore= Chroma.from_documents(chunks, embeddings)

query="Who is at risk of heart disease?"
search_results= vectorstore.similarity_search(query)

search_results

retriever = vectorstore.as_retriever(search_kwargs={'k':5})

retriever.get_relevant_documents(query)

"""# LLM Model loading"""

llm= LlamaCpp(
    model_path="/content/drive/MyDrive/BioMistral/BioMistral-7B.Q4_K_M.gguf",
    temperature=0.2,
    max_tokens=2048,
    top_p=1
)

"""# Use LLM and retriver and query , to generate final response"""

template= """
<|context|>
You are an Medical Assistant that follows the instructions and generate the accurate response based on the query and the context provided
Please be truthful and  give direct answers.
</s>
<|user|>
{query}
</s>
<|assistant|>
"""

from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(template)

rag_chain=(
    {"context": retriever, "query": RunnablePassthrough()}
    |prompt
    |llm
    |StrOutputParser()
)

response=rag_chain.invoke(query)

response

import sys
while True:
  user_input=input(f"Input query: ")
  if user_input == 'exit':
    print("Exciting....")
    sys.exit()
  if user_input=="":
    continue
  result=rag_chain.invoke(user_input)
  print("Answer:", result)
 
