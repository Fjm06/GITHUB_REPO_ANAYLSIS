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
from src.helper import load_embedding,repo_ingestion
from flask import Flask,render_template,jsonify,request
app=Flask(__name__)
embeddings=load_embedding()
persist_directory='db'
vectordb=Chroma(persist_directory=persist_directory,embedding_function=embeddings)
llm=HuggingFaceEndpoint(
    repo_id='mistralai/Mistral-7B-Instruct-v0.3',
    task='text-generation'
)
model=ChatHuggingFace(llm=llm)
memory=ConversationSummaryMemory(llm=model,memory_key='chat_history',return_messages=True)
qa=ConversationalRetrievalChain.from_llm(model,retriever=vectordb.as_retriever(search_type='mmr',search_kwargs={'k':8}),memory=memory)
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')
@app.route('/chatbot', methods=["GET", "POST"])
def gitRepo():

    if request.method == 'POST':
        user_input = request.form['question']
        repo_ingestion(user_input)
        os.system("python store_index.py")

    return jsonify({"response": str(user_input) })
@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)

    if input == "clear":
        os.system("rm -rf repo")

    result = qa.invoke({"question": input})


    print(result['answer'])
    return str(result["answer"])
if __name__=='__main__':
    app.run(host='0.0.0.0',port=8080,debug=True,use_reloader=False)