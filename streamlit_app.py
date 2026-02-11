import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from git import Repo
from github import Github
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import shutil
import time

load_dotenv()

# Page config
st.set_page_config(
    page_title="GitHub Repo AI Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'projects' not in st.session_state:
    st.session_state.projects = {}
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'model' not in st.session_state:
    st.session_state.model = None

# Load persistent projects
PROJECTS_FILE = "projects.json"

def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_projects():
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(st.session_state.projects, f, indent=2)

# Initialize
if not st.session_state.projects:
    st.session_state.projects = load_projects()

@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

@st.cache_resource
def load_llm():
    llm = HuggingFaceEndpoint(
        repo_id='mistralai/Mistral-7B-Instruct-v0.2',
        task='text-generation',
        max_new_tokens=512,
        temperature=0.7
    )
    return ChatHuggingFace(llm=llm)

def handle_remove_readonly(func, path, exc):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url, project_name):
    repo_path = f"repos/{project_name}"
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=handle_remove_readonly)
    os.makedirs(repo_path, exist_ok=True)
    Repo.clone_from(repo_url, to_path=repo_path)
    return repo_path

def get_repo_metadata(repo_url, github_token=None):
    """Fetch repo metadata using GitHub API"""
    try:
        if github_token:
            g = Github(github_token)
        else:
            g = Github()
        
        # Extract owner/repo from URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo_name = parts[-2], parts[-1].replace('.git', '')
        
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Get latest commit
        latest_commit = repo.get_commits()[0]
        
        metadata = {
            'name': repo.name,
            'description': repo.description,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'language': repo.language,
            'last_commit': repo.pushed_at.isoformat(),
            'open_issues': repo.open_issues_count,
            'branches': [b.name for b in repo.get_branches()[:10]],
            'latest_commit': {
                'sha': latest_commit.sha[:7],
                'message': latest_commit.commit.message,
                'author': latest_commit.commit.author.name,
                'date': latest_commit.commit.author.date.isoformat(),
                'url': latest_commit.html_url
            }
        }
        return metadata
    except Exception as e:
        return {'error': str(e)}

def load_repo_files(repo_path):
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
            # Skip if language not supported or no files found
            pass
    
    # Also load common text files (README, config files, etc.)
    text_extensions = ['.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml']
    for ext in text_extensions:
        try:
            from langchain_community.document_loaders import TextLoader
            import glob
            
            pattern = os.path.join(repo_path, f'**/*{ext}')
            for file_path in glob.glob(pattern, recursive=True):
                try:
                    loader = TextLoader(file_path, encoding='utf-8')
                    docs = loader.load()
                    all_documents.extend(docs)
                except:
                    pass
        except:
            pass
    
    return all_documents

def split_documents(documents):
    """Split documents intelligently based on content type"""
    all_chunks = []
    
    # Group documents by language/type
    for doc in documents:
        try:
            # Detect language from file extension
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
            elif ext in ['.rb']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.RUBY, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.md', '.markdown']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.MARKDOWN, chunk_size=2000, chunk_overlap=200
                )
            elif ext in ['.html', '.htm']:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language.HTML, chunk_size=2000, chunk_overlap=200
                )
            else:
                # Generic text splitter for other files
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=2000, chunk_overlap=200
                )
            
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)
        except Exception as e:
            # Fallback to generic splitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000, chunk_overlap=200
            )
            chunks = splitter.split_documents([doc])
            all_chunks.extend(chunks)
    
    return all_chunks

def create_vectorstore(text_chunks, project_name, embeddings):
    """Create Chroma vectorstore for project"""
    try:
        persist_dir = f"db/{project_name}"
        vectorstore = Chroma.from_documents(
            documents=text_chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        return vectorstore
    except Exception as e:
        st.error(f"Error creating vectorstore: {e}")
        return None

def load_vectorstore(project_name, embeddings):
    """Load Chroma vectorstore for specific project"""
    try:
        persist_dir = f"db/{project_name}"
        if os.path.exists(persist_dir):
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            return vectorstore
        return None
    except Exception as e:
        st.error(f"Error loading vectorstore: {e}")
        return None

def get_last_commit_hash(repo_path):
    """Get last commit hash and info from local repo"""
    try:
        repo = Repo(repo_path)
        commit = repo.head.commit
        return {
            'sha': commit.hexsha[:7],
            'message': commit.message.strip(),
            'author': commit.author.name,
            'date': commit.committed_datetime.isoformat()
        }
    except:
        return None

def check_for_updates(project_name):
    """Check if repo has new commits"""
    project = st.session_state.projects.get(project_name)
    if not project:
        return False
    
    repo_path = f"repos/{project_name}"
    if not os.path.exists(repo_path):
        return False
    
    try:
        repo = Repo(repo_path)
        repo.remotes.origin.fetch()
        
        local_commit = repo.head.commit.hexsha
        remote_commit = repo.remotes.origin.refs[repo.active_branch.name].commit.hexsha
        
        return local_commit != remote_commit
    except:
        return False

def update_repo(project_name):
    """Pull latest changes and re-index"""
    repo_path = f"repos/{project_name}"
    try:
        repo = Repo(repo_path)
        repo.remotes.origin.pull()
        
        # Re-index
        documents = load_repo_files(repo_path)
        if documents:
            text_chunks = split_documents(documents)
            embeddings = load_embedding_model()
            create_vectorstore(text_chunks, project_name, embeddings)
            
            # Update metadata
            st.session_state.projects[project_name]['last_updated'] = datetime.now().isoformat()
            st.session_state.projects[project_name]['last_commit'] = get_last_commit_hash(repo_path)
            save_projects()
            return True
    except Exception as e:
        st.error(f"Update failed: {e}")
    return False

# Sidebar
with st.sidebar:
    st.title("🤖 GitHub Repo AI Agent")
    
    # Vector DB status
    try:
        db_size = sum(f.stat().st_size for f in Path('db').rglob('*') if f.is_file()) if os.path.exists('db') else 0
        db_size_mb = db_size / (1024 * 1024)
        st.success(f"💾 Vector DB Ready")
        st.caption(f"Storage: {db_size_mb:.2f} MB")
    except:
        st.info("💾 Vector DB: Ready")
    
    st.markdown("---")
    st.subheader("Add New Repository")
    
    with st.form("add_repo"):
        repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/user/repo")
        project_name = st.text_input("Project Name", placeholder="my-project")
        github_token = st.text_input("GitHub Token (optional)", type="password", 
                                     help="For private repos and API access")
        submit = st.form_submit_button("Add Repository")
        
        if submit and repo_url and project_name:
            with st.spinner(f"Cloning and indexing {project_name}..."):
                try:
                    # Clone repo
                    repo_path = clone_repo(repo_url, project_name)
                    
                    # Get metadata
                    metadata = get_repo_metadata(repo_url, github_token if github_token else None)
                    
                    # Load and process files
                    documents = load_repo_files(repo_path)
                    
                    if not documents:
                        st.error("No code files found in repository. Please check the repository URL.")
                    else:
                        text_chunks = split_documents(documents)
                        
                        # Create embeddings and vectorstore
                        embeddings = load_embedding_model()
                        create_vectorstore(text_chunks, project_name, embeddings)
                        
                        # Save project
                        st.session_state.projects[project_name] = {
                            'url': repo_url,
                            'added': datetime.now().isoformat(),
                            'last_updated': datetime.now().isoformat(),
                            'last_commit': get_last_commit_hash(repo_path),
                            'chunks': len(text_chunks),
                            'files': len(documents),
                            'metadata': metadata
                        }
                        save_projects()
                        
                        st.success(f"✓ {project_name} added successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    
    st.markdown("---")
    st.subheader("Your Projects")
    
    if st.session_state.projects:
        for proj_name in st.session_state.projects.keys():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                if st.button(f"📁 {proj_name}", key=f"select_{proj_name}", use_container_width=True):
                    st.session_state.current_project = proj_name
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("🔄", key=f"update_{proj_name}", help="Check for updates"):
                    if check_for_updates(proj_name):
                        with st.spinner("Updating..."):
                            if update_repo(proj_name):
                                st.success("Updated!")
                                st.rerun()
                    else:
                        st.info("Up to date")
            
            with col3:
                if st.button("🗑️", key=f"delete_{proj_name}", help="Delete project"):
                    # Delete files
                    repo_path = f"repos/{proj_name}"
                    db_path = f"db/{proj_name}"
                    
                    if os.path.exists(repo_path):
                        shutil.rmtree(repo_path, onerror=handle_remove_readonly)
                    if os.path.exists(db_path):
                        shutil.rmtree(db_path, onerror=handle_remove_readonly)
                    
                    del st.session_state.projects[proj_name]
                    save_projects()
                    
                    if st.session_state.current_project == proj_name:
                        st.session_state.current_project = None
                    st.rerun()
    else:
        st.info("No projects yet. Add one above!")

# Main area
if st.session_state.current_project:
    project = st.session_state.projects[st.session_state.current_project]
    
    st.title(f"💬 Chat with {st.session_state.current_project}")
    
    # Project info
    with st.expander("📊 Project Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Files Indexed", project.get('files', 0))
            st.metric("Code Chunks", project.get('chunks', 0))
        
        with col2:
            metadata = project.get('metadata', {})
            if 'language' in metadata:
                st.metric("Language", metadata['language'])
            if 'stars' in metadata:
                st.metric("Stars", metadata['stars'])
        
        with col3:
            if 'last_updated' in project:
                st.metric("Last Updated", project['last_updated'][:10])
            if 'open_issues' in metadata:
                st.metric("Open Issues", metadata['open_issues'])
        
        # Latest Commit Info
        if 'latest_commit' in metadata:
            st.markdown("---")
            st.markdown("### 🔄 Latest Commit")
            commit = metadata['latest_commit']
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Message:** {commit.get('message', 'N/A')}")
                st.markdown(f"**Author:** {commit.get('author', 'N/A')}")
            with col2:
                st.markdown(f"**SHA:** `{commit.get('sha', 'N/A')}`")
                st.markdown(f"**Date:** {commit.get('date', 'N/A')[:10]}")
            
            if 'url' in commit:
                st.markdown(f"[View Commit on GitHub]({commit['url']})")
        
        if 'branches' in metadata:
            st.markdown("---")
            st.write("**Branches:**", ", ".join(metadata['branches'][:5]))
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
    
    # Chat input
    if prompt := st.chat_input("Ask anything about this repository..."):
        # Add user message
        st.session_state.chat_history.append({'role': 'user', 'content': prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Load models
                    embeddings = load_embedding_model()
                    model = load_llm()
                    
                    # Load vectorstore
                    vectordb = load_vectorstore(st.session_state.current_project, embeddings)
                    
                    if vectordb:
                        # Get project metadata for context
                        project_meta = st.session_state.projects.get(st.session_state.current_project, {})
                        metadata = project_meta.get('metadata', {})
                        latest_commit = metadata.get('latest_commit', {})
                        
                        # Add commit context to prompt if available
                        commit_context = ""
                        if latest_commit:
                            commit_context = f"""

Repository Commit Information:
- Latest Commit SHA: {latest_commit.get('sha', 'N/A')}
- Commit Message: {latest_commit.get('message', 'N/A')}
- Author: {latest_commit.get('author', 'N/A')}
- Date: {latest_commit.get('date', 'N/A')}
- Repository: {project_meta.get('url', 'N/A')}
"""
                        
                        # Create QA chain
                        template = """You are an expert Software Repository Analysis AI Assistant with deep knowledge of multiple programming languages, software engineering, code architecture, and best practices.

Your role is to help developers understand codebases across different languages and technologies by providing insightful, accurate, and actionable analysis.

Supported Languages: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Kotlin, Swift, Scala, HTML, Markdown, and more.
""" + commit_context + """

Context from Repository:
{context}

User Question: {question}

Response Guidelines:
1. **Structure & Clarity**
   - Start with a brief, direct answer
   - Use ### for main sections
   - Use bullet points (-) for lists
   - Use numbered lists (1., 2., 3.) for sequential steps or priorities
   - Use code blocks with ``` for code examples (always specify language)

2. **Code Analysis**
   - Explain the purpose and functionality clearly
   - Identify patterns, architectures, and design principles
   - Point out dependencies and relationships between components
   - Highlight potential issues, bugs, or improvements when relevant
   - Consider language-specific idioms and best practices
   - Reference commit history or recent changes when relevant

3. **Commit & History Awareness**
   - When asked about "latest commit", "last push", or "recent changes", use the Repository Commit Information provided above
   - Provide specific commit details (SHA, message, author, date) when relevant
   - Don't say you can't access commit information - it's provided in the context
   - Reference the commit message to understand recent changes

4. **Technical Depth**
   - Provide context about why code is written a certain way
   - Explain technical decisions and trade-offs
   - Reference specific functions, classes, or modules from the context
   - Use proper technical terminology for the language being discussed
   - Mention language-specific features or limitations

5. **Actionable Insights**
   - Suggest improvements or best practices when appropriate
   - Provide examples or alternatives when explaining concepts
   - Link related components or files when relevant
   - Offer next steps or further exploration suggestions
   - Consider cross-language comparisons when helpful

6. **Formatting**
   - Keep paragraphs concise (2-3 sentences max)
   - Use **bold** for emphasis on key terms
   - Use `inline code` for variable/function names
   - Use tables for comparisons when helpful
   - Specify language in code blocks (e.g., ```python, ```javascript)

7. **Tone**
   - Professional yet approachable
   - Confident but not condescending
   - Educational and helpful
   - Assume the user has programming knowledge
   - Adapt explanations to the language context

Answer:"""
                        
                        prompt_template = ChatPromptTemplate.from_template(template)
                        
                        def format_docs(docs):
                            return "\n\n".join(doc.page_content for doc in docs)
                        
                        qa_chain = (
                            {"context": vectordb.as_retriever(search_type='mmr', search_kwargs={'k': 8}) | format_docs,
                             "question": RunnablePassthrough()}
                            | prompt_template
                            | model
                            | StrOutputParser()
                        )
                        
                        response = qa_chain.invoke(prompt)
                        st.markdown(response)
                        
                        # Add to history
                        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    else:
                        st.error("Vector database not found. Please re-index the project.")
                
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({'role': 'assistant', 'content': error_msg})

else:
    st.title("🤖 GitHub Repo AI Agent")
    st.markdown("""
    ### Welcome! 👋
    
    This AI agent helps you understand and query GitHub repositories intelligently.
    
    **Features:**
    - 📁 **Multiple Projects** - Manage multiple repositories
    - 🔄 **Auto-Updates** - Check for new commits and re-index
    - 💾 **Persistent Sessions** - Your projects are saved
    - 💬 **Conversational** - Ask questions naturally
    - 📊 **Rich Context** - Analyzes code, structure, and metadata
    - 🚀 **Fast Vector Search** - Powered by ChromaDB
    - 🔄 **Commit Tracking** - Shows latest commit information
    
    **Get Started:**
    1. Add a repository using the sidebar
    2. Select a project to start chatting
    3. Ask questions about the code!
    
    **Example Questions:**
    - "What does this repository do?"
    - "Explain the main functions"
    - "How is the code structured?"
    - "What are the key dependencies?"
    - "What was the latest commit about?"
    - "When was this code last pushed?"
    - "Who made the most recent changes?"
    """)
