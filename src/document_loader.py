from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
import os


# Configuration
FAISS_INDEX_PATH = "faiss_index"  # Directory to save/load vectors

# Initialize embeddings (used for both semantic chunking and vector store)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# Semantic Chunker - intelligently splits based on meaning and context
# This preserves resume sections (Work Experience, Education, Skills) intact
semantic_chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # Uses percentile-based breakpoints
    breakpoint_threshold_amount=95  # Higher = fewer, larger chunks (preserves more context)
)

# Initialize empty vector store
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world this")))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


def save_vector_store():
    """
    Save the vector store to disk for persistence.
    This allows fast loading on subsequent app starts.
    """
    try:
        vector_store.save_local(FAISS_INDEX_PATH)
    except Exception as e:
        print(f"⚠️  Failed to save vector store: {e}")


def load_vector_store_from_disk():
    """
    Load vector store from disk if it exists.
    
    Returns:
        FAISS vector store if found on disk, None otherwise
    """
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            loaded_store = FAISS.load_local(
                FAISS_INDEX_PATH, 
                embeddings,
                allow_dangerous_deserialization=True  # Required for loading pickle files
            )
            return loaded_store
        except Exception as e:
            print(f"⚠️  Failed to load from disk: {e}")
            return None
    return None


def load_documents(path='temp_docs'):
    """
    Load documents with semantic chunking and disk persistence optimization.
    
    Semantic chunking preserves:
    - Resume sections (Work Experience, Education, Skills)
    - Complete job descriptions and achievements
    - Contextual relationships within the resume
    
    Flow:
    1. Try to load from disk (fast - 2 seconds)
    2. If not on disk, load and vectorize documents with semantic chunking (slow - 30 seconds)
    3. Save to disk for next time
    
    Args:
        path: Path to documents directory
        
    Returns:
        FAISS vector store
    """
    global vector_store
    
    # Step 1: Try loading from disk first
    saved_store = load_vector_store_from_disk()
    if saved_store is not None:
        vector_store = saved_store
        return vector_store
    
    # Step 2: Load and vectorize documents with semantic chunking (first time only)
    documents = []
    if not os.path.exists(path):
        raise Exception(f'Path does not exist: {path}')
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            continue
        documents.extend(loader.load())
    
    if not documents:
        raise Exception('No documents found in directory')
    
    # Semantic chunking - intelligently splits based on meaning
    # This preserves resume structure and relationships
    semantic_chunks = semantic_chunker.split_documents(documents)
    
    # Add semantically chunked documents to vector store
    vector_store.add_documents(semantic_chunks)
        
    # Step 3: Save to disk for next time
    save_vector_store()
    
    return vector_store


def reload_documents(path='temp_docs'):
    """
    Force reload documents from scratch, ignoring saved vectors.
    Useful when documents have been updated.
    
    Args:
        path: Path to documents directory
        
    Returns:
        FAISS vector store
    """
    global vector_store
    
    # Reset vector store
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world this")))
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    
    # Load and save with semantic chunking
    vector_store = load_documents(path)
    return vector_store
