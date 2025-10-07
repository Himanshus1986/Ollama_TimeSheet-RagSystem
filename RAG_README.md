# PDF Query System with Ollama - Setup Guide

A complete local RAG (Retrieval-Augmented Generation) system that allows you to upload PDF files and query them using Ollama's Llama 3.2 1B model with local embeddings. No paid APIs required - everything runs locally.

## 🚀 Features

- **Local AI Processing**: Uses Ollama with Llama 3.2 1B model
- **PDF Upload & Processing**: Supports multiple PDF files
- **Smart Chunking**: Intelligent text splitting for better retrieval
- **Vector Search**: ChromaDB for efficient similarity search
- **Web Interface**: Clean Gradio UI for easy interaction
- **RESTful API**: FastAPI backend with full documentation
- **No External APIs**: Everything runs locally on your machine

## 📋 Prerequisites

### System Requirements
- Python 3.9 or higher
- At least 8GB RAM (16GB recommended)
- 10GB free disk space
- Internet connection (for initial model downloads only)

### Required Software
- **Ollama**: For running local LLM and embedding models
- **Python**: For running the application
- **Docker** (optional): For containerized deployment

## 🛠️ Installation Guide

### Step 1: Install Ollama

#### Windows
1. Download Ollama from [https://ollama.com/download](https://ollama.com/download)
2. Run the installer and follow the setup wizard
3. Open Command Prompt or PowerShell

#### macOS
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download Required Models

After installing Ollama, download the required models:

```bash
# Download Llama 3.2 1B model (main language model)
ollama pull llama3.2:1b

# Download Nomic Embed Text model (for embeddings)
ollama pull nomic-embed-text

# Verify models are installed
ollama list
```

**Expected output:**
```
NAME                   ID           SIZE    MODIFIED
llama3.2:1b           abc123def    1.3GB   2 hours ago
nomic-embed-text      xyz789abc    274MB   2 hours ago
```

### Step 3: Start Ollama Service

```bash
# Start Ollama server (keep this running)
ollama serve
```

The Ollama service will run on `http://localhost:11434`

## 📁 Project Setup

### Method 1: Manual Setup (Recommended)

1. **Download all project files** (they should be in your current directory)

2. **Create project directory:**
```bash
mkdir pdf-query-system
cd pdf-query-system
```

3. **Place all downloaded files** in the project directory:
   - `pdf_query_api.py`
   - `gradio_ui.py` 
   - `requirements.txt`
   - `docker-compose.yml`
   - `Dockerfile`
   - `Dockerfile.gradio`

4. **Create Python virtual environment:**
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

5. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

### Method 2: Docker Setup

1. **Ensure Docker is installed and running**

2. **Place all files in project directory** (same as Method 1)

3. **Start all services:**
```bash
docker-compose up --build
```

This will automatically:
- Start Ollama service
- Build and start the API server
- Build and start the Gradio UI
- Download required models (first run only)

## 🚀 Running the Application

### Manual Deployment (Non-Docker)

1. **Start Ollama service** (in a separate terminal):
```bash
ollama serve
```

2. **Start the FastAPI server** (in another terminal):
```bash
cd pdf-query-system
source venv/bin/activate  # or venv\Scripts\activate on Windows
python pdf_query_api.py
```
The API will be available at: `http://localhost:8000`

3. **Start the Gradio UI** (in a third terminal):
```bash
cd pdf-query-system
source venv/bin/activate  # or venv\Scripts\activate on Windows
python gradio_ui.py
```
The UI will be available at: `http://localhost:7860`

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services will be available at:**
- Gradio UI: `http://localhost:7860`
- API Documentation: `http://localhost:8000/docs`
- Ollama Service: `http://localhost:11434`

## 📖 Usage Instructions

### Using the Web Interface

1. **Open your browser** and go to `http://localhost:7860`

2. **Check API Health**: Click "Check API Health" to ensure everything is connected

3. **Upload PDF Files**:
   - Click on the file upload area
   - Select one or more PDF files
   - Click "Upload and Process PDFs"
   - Wait for processing to complete

4. **Ask Questions**:
   - Type your question in the text box
   - Click "Ask" or press Enter
   - View the AI-generated answer with source references

5. **Clear Data**: Use "Clear All Data" to remove uploaded files and reset the database

### Using the API Directly

The API provides several endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Upload PDFs
curl -X POST "http://localhost:8000/upload_pdfs" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"

# Query documents
curl -X POST "http://localhost:8000/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the documents?"}'
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🔧 Configuration

### Environment Variables

You can customize the application by setting these environment variables:

```bash
# API Configuration
export API_HOST=0.0.0.0
export API_PORT=8000

# Ollama Configuration
export OLLAMA_HOST=http://localhost:11434
export LLM_MODEL=llama3.2:1b
export EMBEDDING_MODEL=nomic-embed-text

# Database Configuration
export CHROMA_PERSIST_DIR=./chroma_db
export UPLOAD_DIR=./uploaded_pdfs
```

### Model Configuration

To use different models, modify the configuration in `pdf_query_api.py`:

```python
# Change these variables
EMBEDDING_MODEL_NAME = "nomic-embed-text"  # or "all-minilm"
LLM_MODEL_NAME = "llama3.2:1b"            # or "llama3.2:3b"
```

Available embedding models:
- `nomic-embed-text` (recommended, 274MB)
- `all-minilm` (alternative, smaller)

## 🐛 Troubleshooting

### Common Issues

**1. "Cannot connect to Ollama" error:**
```bash
# Check if Ollama is running
ollama list

# If not running, start it:
ollama serve
```

**2. "Model not found" error:**
```bash
# Download missing models
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

**3. "Port already in use" error:**
```bash
# Kill processes using the ports
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**4. Memory issues:**
- Ensure you have at least 8GB RAM
- Close other applications to free memory
- Consider using the 1B model instead of larger ones

**5. PDF processing fails:**
- Ensure PDFs are not password-protected
- Check if PDFs contain readable text (not just images)
- Try with smaller PDF files first

### Logs and Debugging

**View application logs:**
```bash
# Manual deployment
tail -f /var/log/pdf-query-system.log

# Docker deployment
docker-compose logs -f pdf-query-api
docker-compose logs -f gradio-ui
```

**Enable debug mode:**
Add this to your environment:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
```

## 📊 Performance Tips

1. **Optimize chunk size**: Adjust `chunk_size` in `pdf_query_api.py` based on your documents
2. **Use SSD storage**: Store ChromaDB on SSD for faster retrieval
3. **Increase RAM**: More RAM allows processing larger documents
4. **Use appropriate models**: Use `llama3.2:1b` for speed, `llama3.2:3b` for better quality

## 🔒 Security Considerations

- The application runs locally and doesn't send data to external services
- PDFs are stored locally in the `uploaded_pdfs` directory
- Vector embeddings are stored locally in ChromaDB
- No user authentication is implemented (suitable for local use only)

## 📝 File Structure

```
pdf-query-system/
├── pdf_query_api.py          # FastAPI backend server
├── gradio_ui.py             # Gradio web interface
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # API server container
├── Dockerfile.gradio       # Gradio UI container
├── README.md              # This file
├── chroma_db/             # Vector database (created automatically)
├── uploaded_pdfs/         # Uploaded PDF files (created automatically)
└── venv/                  # Python virtual environment (created by you)
```

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed correctly
3. Verify Ollama models are downloaded: `ollama list`
4. Check logs for detailed error messages
5. Try restarting all services

## 📄 License

This project is open source and available under the MIT License.

---

**Happy querying! 🚀**