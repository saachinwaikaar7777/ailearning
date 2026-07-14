import os
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "docs"
EMBED_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "models/gemini-2.5-flash" #model for generating answers, this is a powerful model that can understand and use the retrieved context to answer questions, you can experiment with different models to see how it affects the quality of the answers, but make sure to choose a model that is capable of understanding and using the retrieved context effectively
TOP_K = 5#number of top relevant documents to retrieve for each query, this controls how many sources the model can use to answer the question, more can provide more context but also more noise, 5 is a common choice for RAG applications

def embed_query(query: str) -> List[float]:#embed a single query string using OpenAI embeddings, return embedding vector, convert text to numerical vector
    resp = genai.embed_content(model=EMBED_MODEL, content=query)#call OpenAI embeddings endpoint with specified model and input query, get response with embedding vector for the query, this will convert the input uery text into a numerical vector representation that captures its semantic meaning, this embedding vector can then be used to perform similarity search in the vector database (ChromaDB) to find relevant documents based on their embeddings
    return resp["embedding"]#return embedding vector, type: List[float], numerical representation of the input text

def retrieve(collection, query: str, k: int = TOP_K) -> List[Dict[str, Any]]:# retrieve top-k relevant documents from ChromaDB collection for the given query
    #inputs : vector db collection, query string, number of top results to retrieve, default is TOP_K, 5
    q_emb = embed_query(query)#embed the query string to get its embedding vector
    results = collection.query(#query the collection using the query embedding, perform cosine similarity search to find nearest neighbors, return top-k results with documents, metadata, and distances
        query_embeddings=[q_emb],#list of query embeddings, here we have only one query, so we wrap the single query embedding in a list, this is because the ChromaDB query method expects a list of query embeddings, even if we are only querying with one embedding
        n_results=k,#number of top results to retrieve, this controls how many sources the model can use to answer the question, more can provide more context but also more noise, 5 is a common choice for RAG applications
        include=["documents", "metadatas", "distances"]#cosine similarity seach, find nearest vectors, return documents, metadata, distances
        #include is a list of what to include in the results, we want the retrieved document texts, their associated metadata (like source file, page number, etc.), and their distances to the query embedding (which indicates how relevant they are to the query
    )

    docs = results["documents"][0]#list of retrieved document texts, chroma returns results per query, here we have only one query, so take first element index 0
    metas = results["metadatas"][0]
    dists = results["distances"][0]

#combine documents, metadata, distances into list of dicts,
# creates a list of hits with text, metadata, and distance for each retrieved document, appends to hits list, returns hits, type: List[Dict[str, Any]] ,
#  each dict has keys: text, meta, distance
    hits = []
    for doc, meta, dist in zip(docs, metas, dists):#iterate over retrieved documents, metadata, and distances together using zip, for each retrieved document, get its text, metadata, and distance to the query embedding
        #zip combines the three lists (docs, metas, dists) into tuples of (doc, meta, dist) for each retrieved document, this allows us to iterate over them together in a single loop, for each retrieved document, we can access its text, metadata, and distance in the same iteration of the loop
        hits.append({#append a dict with text, metadata, and distance for each retrieved document to the hits list, this will give us a list of hits where each hit contains the text of the retrieved document, its associated metadata (like source file, page number, etc.), and its distance to the query embedding (which indicates how relevant it is to the query)
            "text": doc,
            "meta": meta,
            "distance": dist
        })
    return hits

def build_context(hits: List[Dict[str, Any]]) -> Tuple[str, str]:#tuple of context block and citations block
    """
    Builds:
    - context_block: fed to the llm model
    - citations_block: printed for user
    """
    context_parts = []#build context block with source info and text for each retrieved hit, this will be fed to the LLM model as context for answering the question, it contains the retrieved documents with source information, this way the model can use this information to answer the question and also cite the sources in its answer
    citations_parts = []#build citations block with source info for each retrieved hit, this will be printed for the user to show the sources of the retrieved information, it contains a list of sources with their corresponding numbers, this way the user can see where the information is coming from and also understand the references in the model's answer when it cites sources like [1], [2], etc.
    for idx, h in enumerate(hits, start=1):#iterate over retrieved hits with index starting from 1, for each hit, get its text, metadata, and distance, build context part with source info and text for the hit, append to context_parts list, also build citation part with source info for the hit, append to citations_parts list, this will give us two separate blocks: one for context to feed to the model, and one for citations to show to the user
        src = h["meta"].get("source_file", "unknown")#get source file from metadata, if not available, use "unknown", this will give us the source file name for the retrieved document, which is important for traceability and for RAG to show sources of info, we will include this source information in both the context block (fed to the model) and the citations block (printed for the user), this way we can provide transparency about where the information is coming from and also allow the model to cite sources in its answer
        page = h["meta"].get("page", "?")#get page number from metadata, if not available, use "?", this will give us the page number for the retrieved document, which is important for traceability and for RAG to show sources of info, we will include this page information in both the context block (fed to the model) and the citations block (printed for the user), this way we can provide transparency about where the information is coming from and also allow the model to cite sources in its answer
        context_parts.append(f"[Source {idx}: {src}, p.{page}]\n{h['text']}\n")#context part with source info and text, gives traceability to the model, 
        # enable citations like [1], [2]
        citations_parts.append(f"[{idx}] {src} (page {page})")

    return "\n".join(context_parts), "\n".join(citations_parts)#join context parts with newlines to create the final context block, join citation parts with newlines to create the final citations block, return both blocks as a tuple, this will give us a context block that contains the retrieved documents with source information for the model to use when answering the question, and a citations block that contains a list of sources with their corresponding numbers for the user to see where the information is coming from and understand the references in the model's answer when it cites sources like [1], [2], etc.

def answer_question(question: str, context_block: str) -> str:#answer the user's question using the provided context block, this will call the OpenAI chat completions endpoint with a system prompt that instructs the model to use only the provided sources to answer the question, and a user prompt that includes the question and the context block, the model will generate an answer based on the information in the context block and will cite sources using the source numbers, this function returns the generated answer from the model
    system = (
        "You are a helpful AI assistant. Answer using ONLY the provided sources. "
        "If the sources do not contain the answer, say you don't have enough information. "
        "Be concise, and when you make a claim, reference the source numbers like [1], [2]."
    )

    user = (
        f"QUESTION:\n{question}\n\n"
        f"SOURCES:\n{context_block}\n\n"
        "INSTRUCTIONS:\n"
        "- Use only the sources.\n"
        "- Cite sources with [#].\n"#instruct the model to cite sources using the source numbers in square brackets, this will allow the model to reference the retrieved documents in its answer, for example if the model uses information from the first retrieved document, it should cite it as [1], if it uses information from the second retrieved document, it should cite it as [2], and so on, this way we can maintain traceability of the information used in the answer and also provide transparency to the user about where the information is coming from  
        "- If missing, say what is missing.\n"
    )

    model = genai.GenerativeModel(CHAT_MODEL)
    resp = model.generate_content(
         [
             #{"role": "system", "parts": [system]},
             {"role": "user", "parts": [user]}
         ],
         generation_config={"temperature": 0.2}
     )
        
    return resp.text.strip()

def main():
    chroma_client = chromadb.PersistentClient(#initialize ChromaDB persistent client, vectors stored on disk,
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    collection = chroma_client.get_collection(COLLECTION_NAME)#get the collection from ChromaDB, this collection should have been created and populated during the ingestion process, if the collection does not exist, this will raise an error, so make sure to run the ingest.py script first to create and populate the collection before running this chat.py script

    print("✅ Chat with Your Docs (RAG) — type 'exit' to quit.\n")

    while True:
        q = input("You: ").strip()#interactive loop to chat with the document collection, prompt user for input question, strip whitespace
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        hits = retrieve(collection, q, TOP_K)#retrieve top-k relevant documents for the query from ChromaDB collection
        context_block, citations = build_context(hits)#build context block and citations block from retrieved hits
#context block is the text that will be fed to the LLM model as context for answering the question, it contains the retrieved documents with source information, citations block is a separate block that will be printed for the user to show the sources of the retrieved information, it contains a list of sources with their corresponding numbers, this way the user can see where the information is coming from and also understand the references in the model's answer when it cites sources like [1], [2], etc. 
#citations block is important for transparency and traceability, it allows the user to see the sources of the information retrieved from the collection, and also helps the user understand the references in the model's answer when it cites sources like [1], [2], etc.
        print("\n--- Retrieved Sources ---")
        print(citations)

        ans = answer_question(q, context_block)
        print("\nAssistant:")
        print(ans)
        print("\n" + "-"*60 + "\n")#*60 is just a visual separator for readability between interactions

if __name__ == "__main__":
    main()