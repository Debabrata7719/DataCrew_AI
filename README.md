# DataCrew AI - AI Email Assistant 📧

A modern, conversational AI-powered email assistant built with FastAPI, LangChain, and Groq LLM. Features a beautiful chat-style interface for sending emails through natural language with automatic email signatures, employee database management, and document generation.

## 🌟 Features

- **Conversational AI Interface**: Chat-style UI similar to ChatGPT
- **Natural Language Email Sending**: Just describe what you want to send
- **Employee Database**: Store and manage employee data in MongoDB
- **Employee Lookup**: Search employees by name or job role
- **Document Generation**: Create Word, PDF, Excel, and text files
- **File Attachments**: Upload files to attach to emails
- **Conversation Memory**: Remembers last 50 messages per session
- **Automatic Email Signature**: Adds "Best regards, [Your Name]" automatically
- **LangChain Agent**: Intelligent tool-calling with parameter extraction
- **Groq LLM**: Fast, powerful language model
- **MCP Support**: Uses Model Context Protocol (MCP) for tools
- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Processing**: Instant AI responses with typing indicators

## 🏗️ Project Structure

```
AI_EMAIL_WRITER/
├── src/                    # Source code directory
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management
│   ├── Data_Insert.py      # Sample data insertion script
│   ├── employee_service.py # Employee business logic
│   ├── api/                # FastAPI application
│   │   ├── main.py         # API entry point
│   │   ├── session_state.py # Session management
│   │   └── endpoints/     # API endpoints
│   │       ├── chat.py     # Chat endpoint
│   │       ├── files.py    # File upload endpoints
│   │       └── memory.py   # Memory stats endpoint
│   ├── llm/                # LangChain agent
│   │   └── agent.py        # LLM agent with tools
│   ├── data/               # Database layer
│   │   ├── mongodb.py      # MongoDB connection
│   │   ├── repository.py   # CRUD operations
│   │   └── data_manager.py # Data management
│   ├── services/           # Business logic
│   │   ├── employee_service.py # Employee service
│   │   └── document_service.py  # Document generation
│   ├── memory/             # Conversation memory
│   │   └── manager.py      # Memory management
│   ├── mcp/                # Model Context Protocol
│   │   ├── server.py       # MCP server
│   │   └── tools/          # MCP tools
│   │       ├── email.py     # Email tools
│   │       ├── employee.py  # Employee tools
│   │       └── document.py  # Document tools
├── frontend/               # Web interface
│   ├── index.html          # Chat UI
│   ├── style.css           # Modern styling
│   └── script.js           # Frontend logic
├── uploads/                # Uploaded files
├── generated_docs/         # Generated documents
├── .env                    # Environment variables (gitignored)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── start.bat               # Quick start script (Windows)
└── README.md               # This file
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create/update `.env` file with your credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password
SENDER_NAME=Your Name
```

**Getting Gmail App Password:**
1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"

### 3. Run MongoDB

Ensure MongoDB is running locally on `localhost:27017`

### 4. Run the Application

**Option 1: Using start.bat (Windows)**
```bash
start.bat
```

**Option 2: Manual start**
```bash
cd src
python -m src.api.main
```

The server will start on `http://127.0.0.1:8000`

## 📡 API Endpoints

### `POST /chat`
Main chat endpoint for conversational email sending and all AI operations.

**Request:**
```json
{
  "message": "Send an email to john@example.com about tomorrow's meeting"
}
```

**Response:**
```json
{
  "response": "Email sent successfully to john@example.com!"
}
```

### `POST /upload-file`
Upload files to attach to emails.

**Parameters:**
- `file`: File to upload
- `session_id`: Optional session identifier

### `DELETE /chat/history/{session_id}`
Clear conversation history for a session.

### `GET /memory/stats/{session_id}`
Get session statistics and context summary.

### `GET /health`
Health check endpoint to verify API and configuration status.

### `GET /docs`
Interactive API documentation (Swagger UI)

## 🎨 Frontend Access

Once the server is running, access the web interface at:

**http://127.0.0.1:8000/app/**

## 💡 Usage Examples

### Via Web Interface:
1. Open `http://127.0.0.1:8000/app/`
2. Type natural language commands like:
   - "Send an email to boss@company.com about sick leave tomorrow"
   - "Email team@startup.com with project update"
   - "Write to hr@company.com requesting vacation"
   - "Add employee John Doe as data scientist email john@test.com phone 123456"
   - "Create a word document with title Report containing Introduction and Conclusion"
   - "Who are the data scientists in our team?"

### Employee Management Examples:
- "store name Sayandip Roy as data scientist email sayandip@gmail.com phone 92374626373"
- "add Rahul Saha (backend developer) with email rahul@gmail.com and phone 8394847563"
- "list all employees who are data scientists"
- "get emails of all software engineers"

### Document Creation Examples:
- "create a word document named Report with title Project Update"
- "generate pdf invoice for January 2024"
- "make an excel sheet with employee data"

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.x
- **AI/ML**: LangChain, Groq LLM
- **Database**: MongoDB (local)
- **Protocol**: MCP (Model Context Protocol)
- **Email**: SMTP (Gmail)
- **Documents**: python-docx, reportlab, openpyxl
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Styling**: Modern gradient design with Inter font

## 🔧 Configuration

### Supported LLM Models
Currently using `openai/gpt-oss-120b` via Groq. You can change this in `src/llm/agent.py`:

```python
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="openai/gpt-oss-120b",
    temperature=0
)
```

### MongoDB Settings
Default connection: `mongodb://localhost:27017/`
Database: `Employee's`
Collection: `Employee_data`

### CORS Settings
For production, update CORS origins in `src/api/main.py`:

```python
allow_origins=["https://yourdomain.com"]
```

## 📝 Notes

- The AI extracts recipient, subject, and message from natural language
- Employee data is stored in MongoDB with duplicate prevention
- Multi-word job titles (e.g., "data scientist") are properly parsed
- Documents are saved in `generated_docs/` directory
- Uploaded files are stored in `uploads/` directory
- Conversation memory persists for 50 messages per session

## 🐛 Troubleshooting

**Email not sending?**
- Verify Gmail app password is correct
- Check 2FA is enabled on Google account

**MongoDB connection errors?**
- Ensure MongoDB is running locally
- Check database name matches "Employee's"

**API errors?**
- Verify Groq API key is valid
- Check all dependencies are installed
- Review console logs for detailed errors

**Employee not being added correctly?**
- Ensure proper format: "name X as job_type email X phone X"
- Multi-word job titles should work automatically

**Built with FastAPI, LangChain, Groq, MongoDB, and MCP (Model Context Protocol)**

