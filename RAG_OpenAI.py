#This code builds a Retrieval-Augmented Generation (RAG) system using LangChain.
#Put your knowledge into a smart searchable library (vector DB),then ask questions, and an LLM answers using that knowledge, not just its memory.
import os
from dotenv import load_dotenv
from openai import OpenAI
from langchain_community.vectorstores import FAISS #vector database for similarity search
from langchain_community.embeddings.openai import OpenAIEmbeddings#converts text to vectors(numbers)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.docstore.document import Document #standard wrapper for text data, Adds structure + metadata
#from langchain_community.chains import create_retrieval_chain#combines retrieval(vector search) + LLM(ChatGPT), This is RAG Pipeline
from langchain_community.chat_models import ChatOpenAI #CHATGPT-like model
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.chains import RetrievalQA
load_dotenv()
client = OpenAI()

kb = [
    "Agentic AI agents use memory, tools, and goals to act.",
    "LangChain and CrewAI are popular frameworks for building AI agents.",
    #"Retrieval-Augmented Generation (RAG) improves accuracy by fetching external knowledge."
]
questions = [
    "What are the key components of Agentic AI?",
    "Name one framework for AI agents.",
    #"How does RAG improve answers?"
] 
# Build vector DB
docs = [Document(page_content=x) for x in kb]#convert raw text into documents, takes each text and wrap in document object
embeddings = OpenAIEmbeddings()#create Embedding or Text->Numbers, this object knows how to take text , send it to OpenAI and get a vector list of nos.
db = FAISS.from_documents(docs, embeddings)#each document text is converted to embedding vector, FAISS stores them efficiently for similarity search
 
retriever = db.as_retriever()#converts question to embedding, find most similar documents, like which paragraph best answers this question
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    retriever=retriever
)
 #THis creates full pipeline, user question-> retriever find relevant docs-> docs + question -> chatGPT generates answers
for q in questions:
    print("\nQ:", q)
    print("A:", qa.run(q))