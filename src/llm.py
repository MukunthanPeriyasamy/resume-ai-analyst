from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import time
import os 
import sys

# Add current directory to path if running directly to support local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompts import system_prompt
from document_loader import load_documents, vector_store

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(model_name='openai/gpt-oss-20b', api_key=groq_api_key)

def analyze_resume(resume_text):
    """
    Analyze resume using ATS criteria.
    
    Args:
        resume_text: The resume content to analyze
        
    Returns:
        Analysis response from LLM
    """
    # Create prompt with system instructions
    prompt = ChatPromptTemplate.from_template(system_prompt + "\n\nRESUME TO ANALYZE:\n{resume}\n\nYOUR ANALYSIS:")
    
    # Create chain
    chain = prompt | llm
    
    # Generate analysis
    response = chain.invoke({"resume": resume_text})
    
    return response.content


def analyze_all_resumes():
    """
    Load all resumes from vector store and analyze them.
    
    Returns:
        Analysis of all resumes
    """
    global vector_store
    
    # Load documents if not already loaded
    if vector_store.index.ntotal == 0:
        vector_store = load_documents()
    
    # Get all documents from vector store
    all_docs = vector_store.similarity_search("", k=vector_store.index.ntotal)
    
    # Combine all resume content
    resume_content = '\n\n---\n\n'.join([doc.page_content for doc in all_docs])
    
    # Analyze
    analysis = analyze_resume(resume_content)
    
    return analysis


if __name__ == "__main__":
    import textwrap
    
    print("\n" + "="*60)
    print("🚀  ATS RESUME ANALYZER - AI POWERED INSIGHTS")
    print("="*60)
    
    start_time = time.time()
    result = analyze_all_resumes()
    end_time = time.time()
    
    # Format the result for better readability
    wrapped_result = textwrap.fill(result, width=80)
    
    print("\n📝 ANALYSIS REPORT:")
    print("-" * 20)
    print(result) # Keep raw formatting if LLM already returns markdown/structure
    print("-" * 20)
    
    print(f"\n✅ Analysis Complete!")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print("="*60 + "\n")
