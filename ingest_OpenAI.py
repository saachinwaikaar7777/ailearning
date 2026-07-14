import os
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings

from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------
# Config
# ----------------------------
DATA_DIR = "data"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "docs"
EMBED_MODEL = "text-embedding-3-small"   # good default; fast/cheap
CHUNK_SIZE_CHARS = 1200                 # simple chunking by chars
CHUNK_OVERLAP_CHARS = 200

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any]  # metadata associated with the chunk, e.g. source file, page number, chunk index, etc., for traceability. RAG must show sources of info.


def read_pdfs(data_dir: str) -> List[Tuple[str, int, str]]:#find all pdfs in data dir and extract text, uses pdfreader, param data_dir: directory containing pdf files
    #extract text from pdf files page by page, normalize whitespace, return list of tuples with filename, page number and page text
    #reader.pages is 0-based, so add 1 to page number, return 1-based page number, skip empty pages, return list of tuples, each tuple is (filename, page_number (1-based), page_text)
    """
    Returns list of tuples: (filename, page_number (1-based), page_text)
    """
    pages = []
    for fn in os.listdir(data_dir):
        if not fn.lower().endswith(".pdf"):
            continue
        path = os.path.join(data_dir, fn)
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):#enumerate pages in pdf, i is 0-based page index, page is page object 
            text = page.extract_text() or ""#extract text from page, if no text, use empty string
            text = " ".join(text.split())  # normalize whitespace
            if text.strip():
                pages.append((fn, i + 1, text))#reader.pages is 0-based, so add 1 to page number, return 1-based page number, skip empty pages, return list of tuples, each tuple is (filename, page_number (1-based), page_text)
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:#chunk text into overlapping chunks of given size and overlap
    """
    Simple sliding window chunking by characters.
    (You can later upgrade to token-based chunking.)
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size#calculate end index for chunk, this will give us the index of the last character in the chunk, we will slice the text from start to end to get the chunk of text for this iteration
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)#add chunk to list of chunks if it's not empty, we will return this list of chunks at the end of the function, each chunk is a substring of the original text with a maximum length of chunk_size characters, and with an overlap of overlap characters between consecutive chunks
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(text):
            break
    return chunks


def make_chunks(pages: List[Tuple[str, int, str]]) -> List[Chunk]:#create chunks from pages, each chunk has text and metadata, filename, page number, chunk index
#result is list of Chunk objects, atomic units with text and metadata ready for embedding and storage

    all_chunks: List[Chunk] = []
    for fn, page_num, page_text in pages:
        for idx, ch in enumerate(chunk_text(page_text, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS)):#chunk page text into overlapping chunks, idx is chunk index, ch is chunk text
            #create Chunk object for each chunk of text, with metadata for traceability, source file, page number, chunk index, etc., for RAG to show sources of info
            all_chunks.append(
                Chunk(
                    text=ch,
                    metadata={
                        "source_file": fn,
                        "page": page_num,
                        "chunk_index": idx,
                    },
                )
            )
    return all_chunks


def embed_texts(texts: List[str]) -> List[List[float]]:#embed list of texts using OpenAI embeddings, return list of embeddings
    """
    Calls OpenAI embeddings in batches.
    """
    # OpenAI embeddings endpoint accepts list input
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)#call OpenAI embeddings endpoint with model and input texts
    return [d.embedding for d in resp.data]#extract embeddings from response, return list of embeddings


def main():#main ingestion function, orchestrates reading, chunking, embedding, and storing in ChromaDB
    print("Reading PDFs...")
    pages = read_pdfs(DATA_DIR)
    if not pages:
        raise SystemExit("No PDF text found. Add PDFs to ./data and try again.")

    print(f"Loaded {len(pages)} pages. Chunking...")
    chunks = make_chunks(pages)
    print(f"Created {len(chunks)} chunks.")

    # Setup Chroma persistent client
    chroma_client = chromadb.PersistentClient(#initialize ChromaDB persistent client, vectors stored on disk, 
        path=CHROMA_DIR,#path to store ChromaDB data
        settings=Settings(anonymized_telemetry=False)#disable telemetry, telemetry is data collected about usage of the library, set to False to disable, respect privacy   
    )
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,#name of the collection to store documents, Knowledge base namespace 
        metadata={"hnsw:space": "cosine"}  # cosine similarity
        #metadata is optional dictionary to store additional info about the collection, here we specify hnsw:space as cosine to use cosine similarity for nearest neighbor search, other options include "l2" for Euclidean distance, "ip" for inner product, etc.
        #hnsw is the algorithm used for nearest neighbor search, it stands for Hierarchical Navigable Small World, it's a popular algorithm for efficient similarity search in high-dimensional spaces, it organizes the vectors in a graph structure that allows for fast retrieval of nearest neighbors, by specifying hnsw:space as cosine, we are telling ChromaDB to use cosine similarity as the distance metric when performing nearest neighbor search on the vectors in this collection.
        # By default, ChromaDB uses cosine similarity for vector search, but you can specify other distance metrics if needed.   
    )

    # Optional: reset collection on each ingest
    # Uncomment if you want a clean rebuild each time.
    # chroma_client.delete_collection(COLLECTION_NAME)
    # collection = chroma_client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    # Prepare for embedding & upsert
    BATCH = 64#process in batches of 64 chunks to avoid overloading API
    for i in range(0, len(chunks), BATCH):#process chunks in batches
        batch = chunks[i:i+BATCH]#get batch of chunks to process, slice list of chunks from i to i+BATCH, this will give us a batch of chunks to process in this iteration of the loop
        texts = [c.text for c in batch]#get texts from chunks
        ids = [str(uuid.uuid4()) for _ in batch]#generate unique ids for each chunk
        #for each chunk in the batch, generate a unique id using uuid4, this will give us a list of unique ids for each chunk in the batch, we need these ids to store the chunks in ChromaDB, they will be used as the primary key for each document in the collection, and also to retrieve the documents later when we perform similarity search or other operations on the collection
        metas = [c.metadata for c in batch]#get metadata for each chunk
#metadata is important for traceability and for RAG to show sources of info, we will store the source file, page number, and chunk index in the metadata for each chunk, this way we can easily trace back the source of any information retrieved from the collection later on when we perform similarity search or other operations on the collection
        embeddings = embed_texts(texts)#embed texts in batch using OpenAI embeddings, this will give us a list of embeddings for each chunk in the batch, we will store these embeddings in ChromaDB along with the texts and metadata, so that we can perform similarity search later on when we want to retrieve relevant chunks based on a query

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metas,
            embeddings=embeddings
        )#upsert batch into ChromaDB collection using the add method, this will add the documents to the collection with the specified ids, texts, metadata, and embeddings, if a document with the same id already exists in the collection, it will be updated with the new information (upsert), otherwise it will be added as a new document
        print(f"Upserted {i + len(batch)}/{len(chunks)} chunks...")

    print("\n✅ Ingestion complete.")
    print(f"Chroma DB stored at: {CHROMA_DIR}")
    print(f"Collection: {COLLECTION_NAME}")

#every python file has a built-in variable called __name__, when the file is run directly, __name__ is set to "__main__", 
# so this condition checks if the file is being run directly, and if so, it calls the main() function to start the ingestion process, 
# otherwise, if the file is imported as a module, the main() function is not called automatically.
if __name__ == "__main__":# run main ingestion function
    main()