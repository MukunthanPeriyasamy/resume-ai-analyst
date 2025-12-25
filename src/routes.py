import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from .document_loader import load_documents, reload_documents, vector_store
from .llm import analyze_all_resumes

# Create API router
router = APIRouter()

# Configuration
TEMP_DOCS_DIR = "src/temp_docs"
FAISS_INDEX_DIR = "faiss_index"


class AnalysisResponse(BaseModel):
    analysis: str
    resumes_processed: int


@router.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the ATS Resume Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "/upload": "Upload resumes for analysis (POST)",
            "/analyze": "Analyze uploaded resumes (POST)",
            "/reload": "Force reload resumes (POST)",
            "/clear": "Clear vector store and temp files (DELETE)"
        }
    }


@router.post("/upload")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload resume files (PDF/DOCX) for analysis.
    Files are saved temporarily and then vectorized with semantic chunking.
    After successful vectorization, temporary files are automatically removed.
    """
    # Create temp_docs directory if it doesn't exist
    if not os.path.exists(TEMP_DOCS_DIR):
        os.makedirs(TEMP_DOCS_DIR)

    # Save uploaded files
    saved_files = []
    for file in files:
        # Validate file type
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx') or file.filename.endswith('.txt')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Only PDF, DOCX, and TXT files are supported."
            )
        
        file_location = os.path.join(TEMP_DOCS_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        saved_files.append(file.filename)
    
    # Trigger document loading and vectorization with semantic chunking
    try:
        vector_store_result = load_documents(TEMP_DOCS_DIR)
        num_vectors = vector_store_result.index.ntotal
        
        # Checkpoint: Remove temporary documents after successful vectorization
        cleanup_temp_docs()
        
        return {
            "message": "Resumes uploaded and vectorized successfully",
            "files": saved_files,
            "vectors_created": num_vectors,
            "note": "Temporary files removed after vectorization"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resumes: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_resumes():
    """
    Analyze all uploaded resumes using ATS criteria.
    
    Returns comprehensive analysis including:
    - Overall ATS score
    - Format analysis
    - Content evaluation
    - Consistency & relationship check (skills vs projects)
    - Strengths and weaknesses
    - Red flags (mismatched skills, keyword stuffing)
    - Recommendations
    """
    # Check if vector store exists
    if not os.path.exists(FAISS_INDEX_DIR):
        raise HTTPException(
            status_code=400,
            detail="No resumes found. Please upload resumes using /upload endpoint first."
        )
    
    try:
        # Perform analysis
        analysis_result = analyze_all_resumes()
        
        # Count number of resumes processed
        num_resumes = vector_store.index.ntotal
        
        return {
            "analysis": analysis_result,
            "resumes_processed": num_resumes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/reload")
def reload_resumes():
    """
    Force reload resumes from temp_docs directory.
    Useful when you want to re-process documents with updated settings.
    """
    if not os.path.exists(TEMP_DOCS_DIR):
        raise HTTPException(
            status_code=400,
            detail=f"Directory not found: {TEMP_DOCS_DIR}"
        )
    
    try:
        vector_store_result = reload_documents(TEMP_DOCS_DIR)
        num_vectors = vector_store_result.index.ntotal
        
        # Checkpoint: Remove temporary documents after successful vectorization
        cleanup_temp_docs()
        
        return {
            "message": "Resumes reloaded successfully",
            "vectors_created": num_vectors,
            "note": "Temporary files removed after vectorization"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reload failed: {str(e)}"
        )


@router.delete("/clear")
def clear_vector_store():
    """
    Clear the vector store and temporary documents.
    Use this to start fresh with new resumes.
    """
    try:
        # Remove vector store
        if os.path.exists(FAISS_INDEX_DIR):
            shutil.rmtree(FAISS_INDEX_DIR)
        
        # Remove temp docs
        cleanup_temp_docs()
        
        return {
            "message": "Vector store and temporary documents cleared successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Clear failed: {str(e)}"
        )


def cleanup_temp_docs():
    """
    Checkpoint function: Remove temporary documents after vectorization.
    This keeps the system clean and saves disk space.
    Only vectors are stored permanently, not the original files.
    """
    if os.path.exists(TEMP_DOCS_DIR):
        try:
            # Remove all files in temp_docs
            for file in os.listdir(TEMP_DOCS_DIR):
                file_path = os.path.join(TEMP_DOCS_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            print(f"Warning: Failed to cleanup temp docs: {e}")
