# AI Resume Chat Application

A production-ready AI-powered resume chat application built with RAG (Retrieval Augmented Generation) that allows users to upload resumes and chat with an AI assistant about the resume content.

## 🏗️ Architecture Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend]
        Auth[JWT Auth]
        RateLimit[Rate Limiting]
    end
    
    subgraph "Service Layer"
        ResumeSvc[Resume Service]
        ChatSvc[Chat Service]
        AuthSvc[Auth Service]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        Redis[(Redis Cache)]
        Chroma[(ChromaDB)]
    end
    
    subgraph "AI Layer"
        Ollama[Ollama LLM]
        Embeddings[Embedding Model]
    end
    
    UI --> API
    API --> Auth
    API --> RateLimit
    API --> ResumeSvc
    API --> ChatSvc
    API --> AuthSvc
    ResumeSvc --> PG
    ChatSvc --> Chroma
    ChatSvc --> Ollama
    ChatSvc --> Redis
    AuthSvc --> PG
    Ollama --> Embeddings
```

### Component Diagram

```mermaid
graph TB
    subgraph "Frontend Components"
        Login[Login Page]
        Register[Register Page]
        Dashboard[Dashboard]
        Chat[Chat Interface]
        Upload[Resume Upload]
    end
    
    subgraph "Backend Components"
        Router[API Router]
        Middleware[Auth Middleware]
        ResumeParser[Resume Parser]
        RAGPipeline[RAG Pipeline]
        VectorStore[Vector Store]
        LLMService[LLM Service]
    end
    
    subgraph "Data Components"
        UserDB[User Table]
        ResumeDB[Resume Table]
        ChunkDB[Chunk Table]
        ChatDB[Chat History]
    end
    
    Login --> Router
    Register --> Router
    Dashboard --> Router
    Chat --> Router
    Upload --> Router
    Router --> Middleware
    Router --> ResumeParser
    Router --> RAGPipeline
    ResumeParser --> UserDB
    ResumeParser --> ResumeDB
    ResumeParser --> ChunkDB
    RAGPipeline --> VectorStore
    RAGPipeline --> LLMService
    RAGPipeline --> ChatDB
```

### RAG Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant API
    participant VectorStore
    participant LLM
    participant DB
    
    User->>UI: Upload Resume
    UI->>API: POST /api/resume/upload
    API->>API: Parse Resume (PDF/DOCX)
    API->>API: Chunk Text
    API->>VectorStore: Generate Embeddings
    API->>VectorStore: Store in ChromaDB
    API->>DB: Save Metadata
    API-->>UI: Resume ID
    
    User->>UI: Ask Question
    UI->>API: POST /api/resume/chat
    API->>VectorStore: Semantic Search
    VectorStore-->>API: Relevant Chunks
    API->>LLM: Build Prompt + Context
    LLM-->>API: Generated Answer
    API->>DB: Save Chat History
    API-->>UI: AI Response
```

### Database ER Diagram

```mermaid
erDiagram
    USERS ||--o{ RESUMES : "uploads"
    USERS ||--o{ CHAT_HISTORY : "chats"
    RESUMES ||--o{ RESUME_CHUNKS : "contains"
    RESUMES ||--o{ CHAT_HISTORY : "references"
    
    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    RESUMES {
        int id PK
        int user_id FK
        string filename
        string file_path
        string file_type
        int file_size
        text parsed_text
        json parsed_data
        string processing_status
        text error_message
        timestamp created_at
        timestamp updated_at
    }
    
    RESUME_CHUNKS {
        int id PK
        int resume_id FK
        int chunk_index
        text chunk_text
        json metadata
        timestamp created_at
    }
    
    CHAT_HISTORY {
        int id PK
        int resume_id FK
        int user_id FK
        text question
        text answer
        json context_chunks
        timestamp created_at
    }
```

## 📁 Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── api/                 # API endpoint definitions
│   ├── routes/              # Route handlers
│   │   ├── auth.py         # Authentication routes
│   │   └── resume.py       # Resume & chat routes
│   ├── services/            # Business logic
│   │   ├── auth_service.py # Authentication service
│   │   ├── resume_service.py # Resume operations
│   │   └── chat_service.py # Chat with RAG
│   ├── repositories/        # Data access layer
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py         # User model
│   │   └── resume.py       # Resume models
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py         # User schemas
│   │   └── resume.py       # Resume schemas
│   ├── rag/                 # RAG pipeline
│   │   ├── embeddings.py   # Embedding service
│   │   ├── vectorstore.py   # ChromaDB wrapper
│   │   ├── llm.py          # LLM service
│   │   └── rag_pipeline.py # RAG orchestration
│   ├── parsers/             # Resume parsers
│   │   ├── pdf_parser.py   # PDF parsing
│   │   └── docx_parser.py  # DOCX parsing
│   ├── middleware/          # Custom middleware
│   │   ├── auth.py         # JWT authentication
│   │   └── rate_limit.py   # Rate limiting
│   ├── core/                # Core configurations
│   │   ├── config.py       # App settings
│   │   ├── database.py     # DB connection
│   │   ├── security.py     # Security utilities
│   │   └── redis_client.py # Redis wrapper
│   ├── utils/               # Utility functions
│   └── main.py             # Application entry point
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
└── .env.example            # Environment template
```

### Frontend Structure (React)

```
frontend-react/
├── src/
│   ├── components/          # Reusable components
│   │   └── ui/             # UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       └── Modal.tsx
│   ├── pages/              # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   └── Chat.tsx
│   ├── services/           # API services
│   │   ├── api.ts          # Axios instance
│   │   ├── auth.ts         # Auth API
│   │   └── resume.ts       # Resume API
│   ├── store/              # State management
│   │   └── authStore.ts    # Zustand store
│   ├── hooks/              # Custom hooks
│   ├── types/              # TypeScript types
│   │   └── index.ts
│   ├── layouts/            # Layout components
│   ├── utils/              # Utilities
│   │   └── cn.ts           # Class name utility
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Vite config
├── tailwind.config.js      # Tailwind config
└── Dockerfile             # Docker image
```

## 🔌 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Resume Endpoints

#### Upload Resume
```http
POST /api/resume/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <resume.pdf or resume.docx>
```

**Response (201):**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "file_type": "application/pdf",
  "file_size": 1048576,
  "processing_status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get All Resumes
```http
GET /api/resume/
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "filename": "resume.pdf",
    "file_type": "application/pdf",
    "file_size": 1048576,
    "processing_status": "completed",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Get Resume Details
```http
GET /api/resume/{id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "file_type": "application/pdf",
  "file_size": 1048576,
  "parsed_text": "Full resume text...",
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "skills": ["Python", "JavaScript", "React"],
    "experience": ["Senior Developer at Tech Corp"],
    "projects": ["E-commerce Platform"],
    "certifications": ["AWS Certified"]
  },
  "processing_status": "completed",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Delete Resume
```http
DELETE /api/resume/{id}
Authorization: Bearer <token>
```

**Response (204):** No content

### Chat Endpoints

#### Chat with Resume
```http
POST /api/resume/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_id": 1,
  "question": "What skills does this candidate have?"
}
```

**Response (200):**
```json
{
  "answer": "Based on the resume, the candidate has the following skills: Python, JavaScript, React, Node.js, PostgreSQL, and AWS.",
  "context_chunks": [
    {
      "text": "Skills: Python, JavaScript, React, Node.js...",
      "metadata": {
        "resume_id": 1,
        "chunk_index": 5
      }
    }
  ]
}
```

#### Get Chat History
```http
GET /api/resume/{id}/chat-history
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "history": [
    {
      "id": 1,
      "question": "What skills does this candidate have?",
      "answer": "Based on the resume...",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 🚀 Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Ollama (for local AI models)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd newProject
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Pull Ollama models**
```bash
docker-compose exec ollama ollama pull nomic-embed-text
docker-compose exec ollama ollama pull llama3
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Start PostgreSQL and Redis**
```bash
docker-compose up postgres redis -d
```

5. **Run migrations**
```bash
python -c "from app.core.database import init_db; init_db()"
```

6. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend-react
npm install
```

2. **Configure environment**
```bash
cp .env.example .env
```

3. **Start development server**
```bash
npm run dev
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password storage
- **Rate Limiting**: 30 requests per minute per IP
- **CORS Protection**: Configured allowed origins
- **File Validation**: Type and size validation for uploads
- **Input Sanitization**: Pydantic validation for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## 🤖 AI Configuration

### Ollama Models

The application uses two Ollama models:

1. **Embedding Model**: `nomic-embed-text`
   - Used for generating text embeddings
   - 768-dimensional vectors

2. **LLM Model**: `llama3` (can be changed to mistral or qwen)
   - Used for generating responses
   - Configurable temperature for creativity control

### RAG Pipeline

1. **Chunking Strategy**
   - Chunk size: 500 characters
   - Overlap: 50 characters
   - Preserves context between chunks

2. **Retrieval Strategy**
   - Top-K results: 3 chunks
   - Semantic similarity search
   - Filtered by resume_id

3. **Prompt Engineering**
   - System prompt enforces resume-only answers
   - Clear instructions to avoid hallucination
   - Context-aware responses

## 📊 Performance Optimization

- **Redis Caching**: Chat responses cached for 1 hour
- **Connection Pooling**: PostgreSQL connection pool (10 connections)
- **Async Processing**: Resume processing in background
- **Vector Indexing**: ChromaDB automatic indexing
- **Batch Operations**: Efficient embedding generation

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend-react
npm test
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_chat
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis
- **AI**: LangChain + Ollama + ChromaDB
- **Authentication**: JWT + Passlib
- **Rate Limiting**: SlowAPI

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router
- **Icons**: Lucide React

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please follow the standard pull request workflow.
