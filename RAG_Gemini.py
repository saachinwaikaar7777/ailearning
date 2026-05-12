import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS #vector database for similarity search
from langchain_community.docstore.document import Document #standard wrapper for text data, Adds structure + metadata
from langchain_classic.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
load_dotenv()
kb = [
"Agentic AI agents use memory, tools, and goals to act.",
"LangChain and CrewAI are popular frameworks for building AI agents.",
"Retrieval-Augmented Generation (RAG) improves accuracy by fetching external knowledge."
]

questions = [
"What are the key components of Agentic AI?",
"Name one framework for AI agents.",
"How does RAG improve answers?"
]

# Build vector DB
docs = [Document(page_content=x) for x in kb]#convert raw text into documents, takes each text and wrap in document object
#embeddings = OpenAIEmbeddings()#create Embedding or Text->Numbers, this object knows how to take text , send it to OpenAI and get a vector list of nos.
# Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
model="models/gemini-embedding-001"
)
#embeddings = OpenAIEmbeddings(model="text-embedding-3-small")#create Embedding or Text->Numbers, this object knows how to take text , send it to OpenAI and get a vector list of nos.
db = FAISS.from_documents(docs, embeddings)#each document text is converted to embedding vector, FAISS stores them efficiently for similarity search
retriever = db.as_retriever(search_kwargs={"k": 2})#converts question to embedding, find most similar documents, like which paragraph best answers this question
#search_kwargs={"k": 2} means we want to retrieve the top 2 most relevant documents for each question, instead of just 1. This can provide more context to the LLM when generating answers.
qa = RetrievalQA.from_chain_type(
#llm=ChatOpenAI(model="gpt-4o-mini"),
llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite"),
retriever=retriever,
chain_type="stuff"
)
#THis creates full pipeline, user question-> retriever find relevant docs-> docs + question -> chatGPT generates answers
for q in questions:
    print("\nQ:", q)
    response = qa.invoke({"query": q})
    print("A:", response["result"])