# 🤖 GitHub Repository Analysis AI Agent

An intelligent AI-powered tool that analyzes GitHub repositories and enables conversational queries about codebases across multiple programming languages.

## ✨ Features

- 📁 **Multi-Repository Support** - Manage and analyze multiple repositories simultaneously
- 🔄 **Auto-Updates** - Detect new commits and automatically re-index
- 💾 **Persistent Sessions** - Projects and chat history saved across sessions
- 💬 **Conversational AI** - Natural language queries powered by Mistral-7B
- 🌲 **Pinecone Vector Database** - Cloud-based vector search for scalability
- 🌍 **Multi-Language Support** - Python, JavaScript, Java, C/C++, Go, Rust, Ruby, PHP, and more
- 📊 **Rich Metadata** - GitHub stats, branches, issues, and commit history

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- HuggingFace API Token
- Pinecone API Key (free tier available)
- GitHub Token (optional, for private repos)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Fjm06/GITHUB_REPO_ANAYLSIS.git
cd GITHUB_REPO_ANAYLSIS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your credentials:
```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
PINECONE_API_KEY=your_pinecone_api_key
GITHUB_TOKEN=your_github_token_optional
```

4. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## 🎯 Usage

1. **Add Repository**: Enter GitHub URL and project name in the sidebar
2. **Select Project**: Click on a project to start chatting
3. **Ask Questions**: Query the codebase naturally
4. **Update**: Use 🔄 button to check for new commits
5. **Delete**: Use 🗑️ button to remove projects

## 📝 Example Questions

- "What does this repository do?"
- "Explain the main functions and their purpose"
- "How is the code structured?"
- "What are the key dependencies?"
- "Show me the authentication flow"
- "What design patterns are used?"

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM**: Mistral-7B-Instruct-v0.2 (via HuggingFace)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: Pinecone
- **Framework**: LangChain
- **Git Integration**: GitPython, PyGithub

## 📦 Project Structure

```
├── streamlit_app.py          # Main Streamlit application
├── app.py                     # Flask alternative (legacy)
├── src/
│   └── helper.py             # Helper functions
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in repo)
└── README.md                 # This file
```

## 🌐 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud dashboard:
   - `HUGGINGFACEHUB_API_TOKEN`
   - `PINECONE_API_KEY`
   - `GITHUB_TOKEN` (optional)
5. Deploy!

## 🔑 Getting API Keys

### HuggingFace Token
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token
3. Copy and add to `.env`

### Pinecone API Key
1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Go to API Keys section
3. Copy your API key
4. Run `python setup_pinecone.py` to create index

### GitHub Token (Optional)
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select `repo` scope
4. Copy and add to `.env`

## 📊 Supported Languages

- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- C/C++ (.c, .cpp, .h, .hpp)
- Go (.go)
- Rust (.rs)
- Ruby (.rb)
- PHP (.php)
- Kotlin (.kt)
- Swift (.swift)
- Scala (.scala)
- HTML (.html)
- Markdown (.md)
- And more...

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ by [Fjm06](https://github.com/Fjm06)

## 🙏 Acknowledgments

- LangChain for the RAG framework
- HuggingFace for LLM and embeddings
- Pinecone for vector database
- Streamlit for the amazing UI framework
