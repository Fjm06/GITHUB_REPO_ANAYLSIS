import os
from git import Repo
from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings,ChatHuggingFace,HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
load_dotenv()
def repo_ingestion(repo_url):
    os.makedirs('repo',exist_ok=True)
    repo_path = "repo/"
    Repo.clone_from(repo_url,to_path=repo_path)

def load_repo(repo_path):
    loader=GenericLoader.from_filesystem(repo_path,
                                         glob='**/*.py',
                                         suffixes='.py',
                                         parser=LanguageParser(language=Language.PYTHON,parser_threshold=500)
                                         )
    documents=loader.load()
    return documents
def text_splitter(documents):
    documents_splitter=RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON,chunk_size=2000,chunk_overlap=200)
    texts=documents_splitter.split_documents(documents)
    return texts

def load_embedding():
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings
