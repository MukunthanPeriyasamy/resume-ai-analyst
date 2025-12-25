# 🚀 ResumeAI: AI-Powered ATS Resume Analyzer

ResumeAI is a standard GEN AI application designed to help job seekers optimize their resumes for Applicant Tracking Systems (ATS). It uses **Semantic Chunking** to preserve the context of resume sections and **LLM-powered reasoning** to provide deep-dive analysis.

## ✨ Key Features

- **🔍 Intelligent ATS Analysis**: Evaluates formatting, readability, keyword density, and action verbs.
- **🧠 Semantic Chunking**: Unlike standard splitters, it understands resume structure (Experience, Education, Skills) to keep related info together.
- **⚠️ Consistency Checking**: Flags mismatches between listed skills and demonstrated projects/experience.
- **📄 Multi-Format Support**: Supports `.pdf`, `.docx` files.
- **⚡ Fast Persistence**: Uses **FAISS** for vector storage with disk persistence for near-instant reloading.
- **🤖 Powered by OpenAI**: Leverages `openai/gpt-oss-20b` for high-speed, high-quality analysis.

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **AI/LLM**: OpenAI (GPT-3.5), LangChain
- **Vector DB**: FAISS
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Document Loading**: PyPDF, Docx2txt, SemanticChunker

## 🚀 Getting Started

### 1. Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory and add your OpenAI API key:

```env
GROQ_API_KEY=your_api_key_here
```

### 3. Usage

#### CLI Mode (Deep Analysis)
Run the analysis directly via console:

```bash
python src/llm.py
```

#### API Mode
Start the FastAPI server:

```bash
python -m uvicorn main:app --reload
```

## 📡 API Endpoints

- `GET /`: Connectivity status.
- `POST /upload`: Upload resumes (binary files).
- `POST /analyze`: Run the AI analysis on all uploaded documents.
- `DELETE /clear`: Wipe the vector store and temp files.

## 📁 Project Structure

```text
rag_application/
├── main.py              # FastAPI entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── document_loader.py # Semantic chunking & FAISS logic
│   ├── llm.py           # Analysis logic and CLI entry
│   ├── prompts.py       # Detailed recruiter system prompts
│   ├── routes.py        # API endpoint definitions
│   └── temp_docs/       # Temporary file storage
├── faiss_index/         # Persisted vector database
└── .env                 # API Keys (gitignored)
```
