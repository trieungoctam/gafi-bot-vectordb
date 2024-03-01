from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import json
import pandas as pd
import os, shutil

CHROMA_PATH = "./chroma"
DATA_PATH = "./data/csv"

def get_url() -> list[str]:
    data = json.load(open("./data/web_url.json", "r"))
    return data['url']

def load_documents(urls: list[str]):
    docs = []
    for url in urls:
        loader = WebBaseLoader(url)
        doc = loader.load()
        docs.append(doc)
    return docs

def split_document(docs):
    document_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        separators="\n",
        chunk_size=150,
        chunk_overlap=15
    )
    for doc in docs:
        document_chunk = text_splitter.split_documents(doc)
        document_chunks.extend(document_chunk)
    return document_chunks

def save_vectorstore(document_chunks):
    
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    vector_store = Chroma.from_documents(document_chunks, 
                                        OpenAIEmbeddings(),
                                        persist_directory=CHROMA_PATH)

    vector_store.persist()


def main():
    urls = get_url()
    docs = load_documents(urls)
    document_chunks = split_document(docs)
    save_vectorstore(document_chunks)
    

if __name__ == "__main__":
    main()