import os
from git import Repo
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_huggingface import HuggingFaceEmbeddings,ChatHuggingFace,HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
def repo_ingestion(repo_url):
    import shutil
    repo_path = "repo/"
    # Remove existing repo directory if it exists
    if os.path.exists(repo_path):
        def handle_remove_readonly(func, path, exc):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(repo_path, onerror=handle_remove_readonly)
    os.makedirs('repo',exist_ok=True)
    Repo.clone_from(repo_url,to_path=repo_path)

def load_repo(repo_path):
    """Load all code files from repository - supports multiple languages"""
    all_documents = []
    
    # Define language mappings
    language_map = {
        '.py': Language.PYTHON,
        '.js': Language.JS,
        '.ts': Language.JS,
        '.jsx': Language.JS,
        '.tsx': Language.JS,
        '.java': Language.JAVA,
        '.cpp': Language.CPP,
        '.c': Language.C,
        '.cs': Language.CSHARP,
        '.go': Language.GO,
        '.rb': Language.RUBY,
        '.php': Language.PHP,
        '.rs': Language.RUST,
        '.kt': Language.KOTLIN,
        '.swift': Language.SWIFT,
        '.scala': Language.SCALA,
        '.html': Language.HTML,
        '.md': Language.MARKDOWN,
    }
    
    # Load files by language
    for ext, lang in language_map.items():
        try:
            loader = GenericLoader.from_filesystem(
                repo_path,
                glob=f'**/*{ext}',
                suffixes=[ext],
                parser=LanguageParser(language=lang, parser_threshold=0)
            )
            docs = loader.load()
            all_documents.extend(docs)
        except Exception as e:
            pass
    
    return all_documents

def text_splitter(documents):
    """Split documents intelligently based on content type"""
    all_chunks = []
    
    for doc in documents:
        try:
            source = doc.metadata.get('source', '')
            ext = os.path.splitext(source)[1].lower()
            
            # Choose appropriate splitter
            if ext in ['.py']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.JS, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.java']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.JAVA, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.cpp', '.c', '.h', '.hpp']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.CPP, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.go']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.GO, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.rs']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.RUST, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.md', '.markdown']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.MARKDOWN, chunk_size=2000, chunk_overlap=200
                )
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=2000, chunk_overlap=200
                )
            
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)
        except:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200
            )
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)
    
    return all_chunks

def load_embedding():
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings
