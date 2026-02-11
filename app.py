import os
from git import Repo
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_huggingface import HuggingFaceEmbeddings,ChatHuggingFace,HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()
from src.helper import load_embedding,repo_ingestion
from flask import Flask,render_template,jsonify,request
app=Flask(__name__)
embeddings=load_embedding()
persist_directory='db'
vectordb=Chroma(persist_directory=persist_directory,embedding_function=embeddings)
llm=HuggingFaceEndpoint(
    repo_id='mistralai/Mistral-7B-Instruct-v0.2',
    task='text-generation',
    max_new_tokens=512,
    temperature=0.7
)
model=ChatHuggingFace(llm=llm)

# Enhanced RAG chain with expert system prompt for multi-language support
template = """You are an expert Software Repository Analysis AI Assistant with deep knowledge of multiple programming languages, software engineering, code architecture, and best practices.

Your role is to help developers understand codebases across different languages and technologies by providing insightful, accurate, and actionable analysis.

Supported Languages: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust, Ruby, PHP, Kotlin, Swift, Scala, HTML, Markdown, and more.

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

3. **Technical Depth**
   - Provide context about why code is written a certain way
   - Explain technical decisions and trade-offs
   - Reference specific functions, classes, or modules from the context
   - Use proper technical terminology for the language being discussed
   - Mention language-specific features or limitations

4. **Actionable Insights**
   - Suggest improvements or best practices when appropriate
   - Provide examples or alternatives when explaining concepts
   - Link related components or files when relevant
   - Offer next steps or further exploration suggestions
   - Consider cross-language comparisons when helpful

5. **Formatting**
   - Keep paragraphs concise (2-3 sentences max)
   - Use **bold** for emphasis on key terms
   - Use `inline code` for variable/function names
   - Use tables for comparisons when helpful
   - Specify language in code blocks (e.g., ```python, ```javascript)

6. **Tone**
   - Professional yet approachable
   - Confident but not condescending
   - Educational and helpful
   - Assume the user has programming knowledge
   - Adapt explanations to the language context

Answer:"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

qa = (
    {"context": vectordb.as_retriever(search_type='mmr',search_kwargs={'k':8}) | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')
@app.route('/chatbot', methods=["GET", "POST"])
def gitRepo():
    global vectordb
    
    if request.method == 'POST':
        user_input = request.form['question']
        try:
            # Clone the repository
            repo_ingestion(user_input)
            
            # Process and store in vector database
            from src.helper import load_repo, text_splitter
            documents = load_repo('repo/')
            
            if not documents:
                return jsonify({"response": "Error: No code files found in this repository. Please provide a repository with source code files."})
            
            text_chunks = text_splitter(documents)
            
            if not text_chunks:
                return jsonify({"response": "Error: No code chunks could be extracted. The Python files might be too small or empty."})
            
            # Recreate vector database with new documents
            vectordb = Chroma.from_documents(
                text_chunks, 
                embedding=embeddings, 
                persist_directory='./db'
            )
            
            return jsonify({"response": f"✓ Repository processed successfully! {len(text_chunks)} code chunks indexed from {len(documents)} files. You can now ask questions in the chat below."})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            return jsonify({"response": f"Error: {str(e)}"})
    
    return jsonify({"response": "Please provide a repository URL"})
@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)

    if input == "clear":
        os.system("rmdir /s /q repo")
        return "Repository cleared"

    try:
        # Recreate chain with current vectordb
        qa_chain = (
            {"context": vectordb.as_retriever(search_type='mmr',search_kwargs={'k':8}) | format_docs, 
             "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        
        result = qa_chain.invoke(input)
        
        # Clean up the response
        result = result.strip()
        
        print(result)
        return str(result)
    except Exception as e:
        return f"**Error:** {str(e)}\n\nPlease make sure you've added a repository first using the input box above."
if __name__=='__main__':
    app.run(host='0.0.0.0',port=8080,debug=True,use_reloader=False)