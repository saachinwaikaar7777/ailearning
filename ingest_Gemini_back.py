import os
import sys

# Fix Windows console encoding for Unicode output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from pypdf import PdfReader
import chromadb
from chromadb.config import Settings

# 1. Import the new Google GenAI SDK
from google import genai

dotenv = load_dotenv()

# 2. Initialize the new Client
# Note: The new SDK defaults to looking for "GEMINI_API_KEY", 
# but since you are using "GOOGLE_API_KEY" in your .env, we pass it explicitly.
# Try both casings to handle .env files with mixed-case keys.
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("Google_API_Key") or os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("[ERROR] No API key found. Set GOOGLE_API_KEY in your .env file.")
client = genai.Client(api_key=api_key)

# ----------------------------
# Config
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Prefer an explicit env var, otherwise default to a "data" folder.
requested_data_dir = os.getenv("DATA_DIR", "data")

# Resolve paths relative to this script's directory so invocation cwd doesn't matter.
candidate = os.path.join(BASE_DIR, requested_data_dir)
if os.path.isdir(candidate):
    DATA_DIR = candidate
elif os.path.isdir(os.path.join(BASE_DIR, "DATA_DIR")):
    # Fall back to a project folder literally named "DATA_DIR"
    DATA_DIR = os.path.join(BASE_DIR, "DATA_DIR")
else:
    # Keep the candidate path (may not exist) so we have a predictable absolute path.
    DATA_DIR = candidate
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "docs"
CHUNK_SIZE_CHARS = 1200                
CHUNK_OVERLAP_CHARS = 200

@dataclass
class Chunk:
    text: str
    metadata: Dict[str, Any]  


def read_pdfs(data_dir: str) -> List[Tuple[str, int, str]]:
    """
    Returns list of tuples: (filename, page_number (1-based), page_text)
    """
    pages = []
    for fn in os.listdir(data_dir):
        if not fn.lower().endswith(".pdf"):
            continue
        path = os.path.join(data_dir, fn)
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = " ".join(text.split())  # normalize whitespace
            if text.strip():
                pages.append((fn, i + 1, text))
    return pages


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Simple sliding window chunking by characters.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(text):
            break
    return chunks


def make_chunks(pages: List[Tuple[str, int, str]]) -> List[Chunk]:
    all_chunks: List[Chunk] = []
    for fn, page_num, page_text in pages:
        for idx, ch in enumerate(chunk_text(page_text, CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS)):
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


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Calls Google Gemini embeddings one-at-a-time using the new SDK.
    embed_content with a list of strings may merge them into one embedding,
    so we call it per text to guarantee one embedding per input.
    """
    all_embeddings = []
    for text in texts:
        response = client.models.embed_content(
            model="models/gemini-embedding-2",
            contents=text
        )
        # Single-text call returns a single embedding
        all_embeddings.append(response.embeddings[0].values)
    return all_embeddings


def main():
    # Automatically create the 'data' folder if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"[WARNING] Created missing folder: '{DATA_DIR}'")
        print(f"[ACTION] Please paste your PDF files into: {os.path.abspath(DATA_DIR)}")
        return  # Stop here so the user can add files

    print("Reading PDFs...")
    pages = read_pdfs(DATA_DIR)
    if not pages:
        raise SystemExit("No PDF text found. Add PDFs to ./data and try again.")

    print(f"Loaded {len(pages)} pages. Chunking...")
    chunks = make_chunks(pages)
    print(f"Created {len(chunks)} chunks.")

    # Setup Chroma persistent client
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}   
    )

    # Prepare for embedding & upsert
    BATCH = 64
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i+BATCH]
        texts = [c.text for c in batch]
        ids = [str(uuid.uuid4()) for _ in batch]
        metas = [c.metadata for c in batch]
        
        # Call the updated embed_texts function
        embeddings = embed_texts(texts)

        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metas,
            embeddings=embeddings
        )
        print(f"Upserted {i + len(batch)}/{len(chunks)} chunks...")

    print("\n[SUCCESS] Ingestion complete.")
    print(f"Chroma DB stored at: {CHROMA_DIR}")
    print(f"Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    main()