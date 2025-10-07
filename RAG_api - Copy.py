import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel
import shutil

import ollama
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

app = FastAPI(title="PDF Query API with Ollama", version="1.0.0")

# Configuration
EMBEDDING_MODEL_NAME = "nomic-embed-text"  # Ollama embedding model
LLM_MODEL_NAME = "gemma:2b"  # Local Llama model via Ollama
CHROMA_PERSIST_DIR = './chroma_db'
UPLOAD_DIR = './uploaded_pdfs'

# Ensure directories exist
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize embedding model
embedding = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)

# Global variable for vectorstore
vectorstore = None

# Data models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

def process_pdfs(pdf_filepaths: List[str]):
    """Process PDF files and create vector embeddings"""
    global vectorstore
    all_docs = []
    
    for pdf_file in pdf_filepaths:
        try:
            loader = PyPDFLoader(pdf_file)
            documents = loader.load()
            all_docs.extend(documents)
            print(f"Loaded {len(documents)} pages from {pdf_file}")
        except Exception as e:
            print(f"Error loading {pdf_file}: {str(e)}")
            continue

    if not all_docs:
        raise HTTPException(status_code=400, detail="No documents could be processed")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    docs_chunks = text_splitter.split_documents(all_docs)
    print(f"Created {len(docs_chunks)} document chunks")

    # Create or update vectorstore
    try:
        if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
            # Load existing vectorstore and add new documents
            vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embedding)
            vectorstore.add_documents(docs_chunks)
        else:
            # Create new vectorstore
            vectorstore = Chroma.from_documents(
                docs_chunks, 
                embedding, 
                persist_directory=CHROMA_PERSIST_DIR
            )
        vectorstore.persist()
        print("Vector database updated successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating vector database: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "PDF Query API with Ollama is running!", "status": "healthy"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test Ollama connection
        ollama.list()
        return {"status": "healthy", "ollama": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/upload_pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """Upload and process PDF files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_paths = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_paths.append(file_path)
            print(f"Uploaded: {file.filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving {file.filename}: {str(e)}")

    # Process the uploaded PDFs
    try:
        process_pdfs(uploaded_paths)
        return {
            "message": f"Successfully processed {len(uploaded_paths)} PDF files",
            "files": [os.path.basename(path) for path in uploaded_paths]
        }
    except Exception as e:
        # Clean up uploaded files if processing fails
        for path in uploaded_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Error processing PDFs: {str(e)}")

@app.post("/query", response_model=QueryResponse)
def query_pdf(request: QueryRequest):
    """Query the processed PDF documents"""
    global vectorstore
    
    if vectorstore is None:
        raise HTTPException(status_code=400, detail="No documents loaded. Please upload PDFs first.")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Retrieve relevant chunks using vectorstore
        retriever = vectorstore.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 3}
        )
        relevant_docs = retriever.get_relevant_documents(request.question)
        
        if not relevant_docs:
            return QueryResponse(
                answer="I couldn't find relevant information in the uploaded documents to answer your question.",
                sources=[]
            )

        # Prepare context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        sources = [f"Page {doc.metadata.get('page', 'Unknown')} from {os.path.basename(doc.metadata.get('source', 'Unknown'))}" 
                  for doc in relevant_docs]

        # Format prompt for the LLM
        prompt = f"""Based on the following context from the uploaded documents, please answer the question clearly and concisely.

Context:
{context}

Question: {request.question}

Answer: Please provide a comprehensive answer based only on the information provided in the context above. If the context doesn't contain enough information to answer the question, please say so."""

        # Get completion from Ollama chat model locally
        response = ollama.chat(
            model=LLM_MODEL_NAME, 
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response['message']['content']
        
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.delete("/clear_database")
def clear_database():
    """Clear the vector database and uploaded files"""
    global vectorstore
    
    try:
        # Clear vectorstore
        if vectorstore:
            vectorstore = None
        
        # Remove database directory
        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Clear uploaded files
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
            os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        return {"message": "Database and uploaded files cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)