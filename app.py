from langchain_community.llms import HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_pinecone import PineconeVectorStore
import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import fitz
import io


load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
index_name = "pdfreader"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)

def loadPdf(file):
    loader  =  PyPDFLoader(file)
    data = loader.load()
    # pdf_document = fitz.open(file)

    # text = ""
    # for page_number in range(pdf_document.page_count):
    #     page = pdf_document.load_page(page_number)
    #     text += page.get_text()
    # print(text)
     
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text_chunks = text_splitter.split_documents(data)
    
    vectorstore_from_docs = PineconeVectorStore.from_documents(
        text_chunks,
        index_name=index_name,
        embedding=embeddings
    )


# vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)

def askQuestion(query):
    repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

    llm = HuggingFaceEndpoint(
        repo_id=repo_id, max_length=128, temperature=1, token=HUGGINGFACEHUB_API_TOKEN
    )
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
    result = qa.invoke(query)
    return result


# print(askQuestion("What is the guarantee of the scheme?"))


app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/ask')
@cross_origin(supports_credentials=True)
def ask():
    query = request.args.get('query')
    print(query)
    result = askQuestion(query)
    return jsonify(result)

@app.route('/load' , methods=['POST'])
@cross_origin(supports_credentials=True)
def load():
    print("loading pdf")
    try:
        file = request.files['file']
        fileName = file.filename
        print(fileName)
        file_path = os.path.join("uploads", fileName)
        file.save(file_path)

        try:
            loadPdf(file_path)
            return jsonify({"status": "success"})
        except Exception as e:
            print(e)
            return jsonify({"status": "failed"})
    
    except Exception as e:
        print(e)
        return jsonify({"status": "failed"})
if __name__ == '__main__':
    app.run(debug=True)