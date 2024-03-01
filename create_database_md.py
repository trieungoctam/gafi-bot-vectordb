import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma"
DATA_PATH = "data/markdown"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    return documents

def split_text(documents : list[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=64,
    )
    chunks = splitter.split_documents(documents)
    print(f"Document {len(documents)} split into {len(chunks)} chunks")
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database
    reload_db = False
    if os.path.exists(CHROMA_PATH) and reload_db:
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from documents
    db = Chroma.from_documents(chunks, 
                            OpenAIEmbeddings(),
                            persist_directory=CHROMA_PATH
                            )
    db.persist()
    print(f"Database created at {CHROMA_PATH}")
    
def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def main():
    generate_data_store()

if __name__ == "__main__":
    main()
