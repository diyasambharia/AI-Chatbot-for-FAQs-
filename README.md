FAQ Chatbot with RAG (Retrieval-Augmented Generation)
A sophisticated chatbot that provides accurate, context-aware responses to frequently asked questions using Retrieval-Augmented Generation with LangChain, OpenAI GPT, and document embeddings.
🚀 Features

Intelligent FAQ Responses: Context-aware answers based on your knowledge base
Document Embedding: Automatically processes and embeds FAQ documents
Semantic Search: Finds relevant information using vector similarity
Real-time Chat Interface: Clean, responsive web interface
Multi-format Support: Supports PDF, TXT, and Markdown files
Conversation Memory: Maintains context across multiple questions
Admin Dashboard: Upload and manage FAQ documents
Response Confidence: Shows confidence scores for answers

📋 Prerequisites

Python 3.8+
OpenAI API key
Node.js 16+ (for frontend)
Git

🛠️ Installation
1. Clone the Repository
bashgit clone https://github.com/yourusername/faq-chatbot-rag.git
cd faq-chatbot-rag
2. Backend Setup
bash# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
3. Frontend Setup
bashcd frontend
npm install
npm run build
cd ..
4. Initialize Database
bashpython init_db.py
🔧 Configuration
Create a .env file in the root directory:
envOPENAI_API_KEY=your_openai_api_key_here
VECTOR_DB_PATH=./data/vectordb
UPLOAD_FOLDER=./data/uploads
MAX_TOKENS=1000
TEMPERATURE=0.7
CHUNK_SIZE=500
CHUNK_OVERLAP=50
🚀 Usage
Starting the Application
bash# Start the backend server
python app.py

# The application will be available at http://localhost:5000
Using the Chatbot

Upload FAQ Documents:

Go to the admin panel at /admin
Upload your FAQ documents (PDF, TXT, or MD files)
Documents are automatically processed and embedded


Ask Questions:

Visit the main chat interface
Type your questions in natural language
Receive accurate, context-aware responses


Manage Knowledge Base:

View uploaded documents
Delete outdated information
Monitor chatbot performance



📁 Project Structure
faq-chatbot-rag/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── init_db.py            # Database initialization
├── README.md             # This file
├── data/
│   ├── uploads/          # Uploaded FAQ documents
│   └── vectordb/         # Vector database storage
├── src/
│   ├── __init__.py
│   ├── chatbot.py        # Main chatbot logic
│   ├── document_processor.py  # Document processing
│   ├── embedding_manager.py   # Embedding management
│   └── utils.py          # Utility functions
├── templates/
│   ├── index.html        # Main chat interface
│   ├── admin.html        # Admin dashboard
│   └── base.html         # Base template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── main.js       # Frontend JavaScript
└── tests/
    ├── test_chatbot.py   # Unit tests
    └── test_documents.py # Document processing tests
🔍 API Endpoints
Chat API

POST /api/chat - Send a question and receive an answer
GET /api/chat/history - Get conversation history
DELETE /api/chat/clear - Clear conversation history

Document Management

POST /api/documents/upload - Upload FAQ documents
GET /api/documents - List all documents
DELETE /api/documents/<id> - Delete a document
POST /api/documents/process - Reprocess documents

Health Check

GET /api/health - Check API health status

📊 Performance Metrics
The chatbot tracks several performance metrics:

Response Time: Average time to generate answers
Relevance Score: Semantic similarity of retrieved documents
Confidence Score: Model confidence in generated responses
User Satisfaction: Based on user feedback

🧪 Testing
Run the test suite:
bash# Run all tests
pytest

# Run specific test categories
pytest tests/test_chatbot.py -v
pytest tests/test_documents.py -v

# Run with coverage
pytest --cov=src tests/
📈 Monitoring and Logging
The application includes comprehensive logging:

Request Logs: All API requests and responses
Error Logs: Detailed error information
Performance Logs: Response times and resource usage
User Interaction Logs: Questions asked and satisfaction ratings

Logs are stored in the logs/ directory and can be configured in logging.conf.
🔒 Security Features

Input Validation: Sanitizes all user inputs
Rate Limiting: Prevents abuse of the API
File Upload Security: Validates file types and sizes
API Key Protection: Secure handling of sensitive credentials

🚀 Deployment
Docker Deployment
bash# Build Docker image
docker build -t faq-chatbot .

# Run container
docker run -p 5000:5000 --env-file .env faq-chatbot
Cloud Deployment
The application can be deployed on:

Heroku: Use the included Procfile
AWS: Deploy using Elastic Beanstalk
Google Cloud: Use App Engine or Cloud Run
Azure: Deploy with App Service

📚 FAQ Document Format
For best results, structure your FAQ documents as follows:
markdown# Frequently Asked Questions

## Category 1: General Questions

### Q: What is this service?
A: This service provides...

### Q: How do I get started?
A: To get started, you need to...

## Category 2: Technical Questions

### Q: What are the system requirements?
A: The system requires...
