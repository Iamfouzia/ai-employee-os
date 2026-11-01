# AI Employee OS

An AI-powered employee operating system designed to automate business workflows using modern **Agentic AI, LLMs, NLP, speech processing, APIs, databases, and enterprise integrations**.

The project provides a foundation for building intelligent AI employees capable of interacting with external services, processing information, managing workflows, and supporting business operations.

---

## 🚀 Features

* 🤖 Agentic AI workflows
* 🧠 LLM integration
* 🔗 LangGraph-based agent orchestration
* 💬 OpenAI, Anthropic, and Google Gemini model support
* 🗃️ ChromaDB vector database integration
* ⚡ Redis-based services and state management
* 🌐 FastAPI backend
* 🎙️ Speech-to-text processing with Faster-Whisper
* 👥 Speaker diarization with Pyannote Audio
* 📄 PDF/document processing
* 🗄️ SQL database support through SQLAlchemy
* 🔄 Database migrations with Alembic
* ☁️ AWS integration through Boto3
* 🔎 Elasticsearch integration
* 🔐 Microsoft authentication through MSAL
* 📧 Google API integrations
* 🧪 Automated testing with Pytest

---

## 🏗️ Project Structure

```text
ai-employee-os/
│
├── app/
│   └── Application source code
│
├── tests/
│   └── Test cases
│
├── ai-employee-os-mariam-module/
│   └── Additional project module
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│
└── README.md
```

> The project structure may evolve as additional modules and features are added.

---

# 🛠️ Technology Stack

## Core AI & NLP

* Python
* PyTorch
* Hugging Face Transformers
* Hugging Face Hub

## Agentic AI

* LangGraph
* OpenAI
* Anthropic
* Google Gemini

## Vector & Data Storage

* ChromaDB
* Redis
* SQLAlchemy
* Elasticsearch

## Backend

* FastAPI
* Uvicorn

## Speech & Audio

* Faster-Whisper
* Pyannote Audio
* PyAV

## Database & Migrations

* SQLAlchemy
* Alembic

## Cloud & APIs

* Google APIs
* Microsoft MSAL
* AWS Boto3

## Testing

* Pytest

---

# 📋 Prerequisites

Before installing the project, make sure the following are installed on your system:

* Python
* Git
* pip
* Virtual environment support

Depending on the enabled modules, the project may additionally require:

* Redis
* FFmpeg
* Database server
* API credentials
* Cloud service credentials

---

# 📥 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Ammarawan123/ai-employee-os.git
```

Navigate into the project:

```bash
cd ai-employee-os
```

---

## 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal should display:

```text
(.venv)
```

---

# 📦 Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install all project dependencies:

```bash
pip install -r requirements.txt
```

The current dependency file includes packages for:

* Deep Learning
* NLP
* Agentic AI
* LLM APIs
* Vector databases
* Redis
* FastAPI
* Google APIs
* Audio processing
* Speaker diarization
* Authentication
* Databases
* AWS
* Elasticsearch
* Testing

---

# 🔐 Environment Variables

The project uses environment variables for API keys, authentication credentials, and external services.

Create a `.env` file in the project root:

```text
ai-employee-os/
│
├── .env
├── requirements.txt
├── app/
└── tests/
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

REDIS_URL=redis://localhost:6379

DATABASE_URL=your_database_url

AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

ELASTICSEARCH_URL=your_elasticsearch_url
```

> **Never commit real API keys, passwords, tokens, or credentials to GitHub.**

Make sure `.env` is included in `.gitignore`.

---

# 🤖 Supported AI Models

The project includes integrations for multiple AI providers.

### OpenAI

```text
OPENAI_API_KEY
```

### Anthropic

```text
ANTHROPIC_API_KEY
```

### Google Gemini

```text
GOOGLE_API_KEY
```

The exact model used depends on the corresponding application module and configuration.

---

# ⚡ Redis

Some application functionality may depend on Redis.

Make sure Redis is available before starting components that require it.

Example local Redis URL:

```text
redis://localhost:6379
```

Verify that Redis is running before starting the relevant services.

---

# 🌐 Running the Application

The project uses **FastAPI** and **Uvicorn** for its web backend.

The exact application entry point should be verified from the `app/` directory before running the server.

A typical FastAPI command is:

```bash
uvicorn app.main:app --reload
```

If the project's actual entry point differs, use the module and application object defined in the corresponding source file.

Once running, the API can normally be accessed through:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Running Tests

The project uses Pytest.

Run:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

Run tests from a specific directory:

```bash
pytest tests/
```

---

# 🗄️ Database Migrations

The project includes **Alembic** for database migrations.

Before running migrations, make sure the required database configuration is available.

Typical Alembic commands include:

```bash
alembic upgrade head
```

To create a migration:

```bash
alembic revision --autogenerate -m "description"
```

> The exact migration workflow should follow the project's database configuration and Alembic setup.

---

# 🎙️ Speech Processing

The project includes:

* Faster-Whisper
* Pyannote Audio
* PyAV

These components can be used for speech recognition, audio processing, and speaker diarization.

Some speech-processing functionality may require additional system dependencies such as **FFmpeg** and model authentication/configuration.

---

# 🧠 Vector Database

The project uses **ChromaDB** for vector storage and retrieval.

Vector database functionality may be used by AI agents for:

* Document retrieval
* Semantic search
* Context retrieval
* Knowledge-base operations
* RAG-style workflows

---

# 🔎 Elasticsearch

Elasticsearch support is included for search and indexing functionality.

The Elasticsearch service must be running and correctly configured before modules depending on it are used.

---

# ☁️ AWS Integration

AWS functionality is supported through:

```text
boto3
```

AWS credentials should be configured securely through environment variables or an appropriate AWS credential provider.

Never hard-code AWS credentials in source code.

---

# 🔐 Microsoft Authentication

The project includes Microsoft Authentication Library:

```text
msal
```

Microsoft application credentials and tenant configuration may be required for modules using Microsoft services.

---

# 🔗 Google APIs

The project includes:

```text
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib
```

Google Cloud/API credentials may be required depending on the functionality being used.

---

# 📊 Dependency Overview

The project currently declares the following major dependencies:

| Category        | Packages                        |
| --------------- | ------------------------------- |
| Deep Learning   | PyTorch, Transformers           |
| NLP             | Transformers, Hugging Face Hub  |
| Agentic AI      | LangGraph                       |
| LLM APIs        | OpenAI, Anthropic, Google GenAI |
| Vector Database | ChromaDB                        |
| Cache/State     | Redis                           |
| Backend         | FastAPI, Uvicorn                |
| Speech          | Faster-Whisper, Pyannote Audio  |
| Audio           | PyAV                            |
| Database        | SQLAlchemy, Alembic             |
| Documents       | PyPDF                           |
| Cloud           | Boto3                           |
| Search          | Elasticsearch                   |
| Authentication  | MSAL, Google Auth               |
| Testing         | Pytest                          |

---

# ⚠️ Important Setup Notes

Because this project integrates multiple AI providers, databases, cloud services, authentication systems, and audio-processing libraries, **not every dependency is necessarily required for every module**.

Before deploying or running a specific module:

1. Check its imports.
2. Check its required environment variables.
3. Check whether it requires an external service.
4. Verify the corresponding service is running.
5. Run the relevant tests.

This helps avoid missing dependencies and configuration errors.

---

# 🐛 Troubleshooting

## Dependency Installation Errors

Try upgrading pip:

```bash
python -m pip install --upgrade pip
```

Then reinstall:

```bash
pip install -r requirements.txt
```

---

## Check Installed Packages

```bash
pip list
```

Check a specific package:

```bash
pip show package-name
```

---

## Check Python Version

```bash
python --version
```

---

## Check FastAPI Installation

```bash
pip show fastapi
```

---

## Check PyTorch Installation

```bash
python -c "import torch; print(torch.__version__)"
```

---

## Check Transformers Installation

```bash
python -c "import transformers; print(transformers.__version__)"
```

---

# 🔒 Security

Do not commit:

* API keys
* Passwords
* Access tokens
* OAuth credentials
* AWS credentials
* `.env` files
* Private certificates
* Service account JSON files

Use environment variables and secure secret management instead.

---

# 🤝 Contributing

Contributions are welcome.

Recommended workflow:

```bash
git checkout -b feature/your-feature
```

Make your changes, test them, and commit:

```bash
git add .
git commit -m "Add your feature"
```

Push your branch:

```bash
git push origin feature/your-feature
```

Then create a Pull Request on GitHub.

---

# 📄 License

Check the repository for the project's applicable license.

If no license is currently specified, usage and redistribution should be discussed with the repository owner before treating the project as open-source software.

---

# 👨‍💻 Project

**AI Employee OS**

GitHub Repository:

https://github.com/Ammarawan123/ai-employee-os

---

## 👩‍💻 Contributors

This project is developed collaboratively by its contributors.

Contributions include:

* AI/ML development
* Agentic AI workflows
* Backend development
* API integrations
* Database systems
* Automation
* Testing
* Documentation

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
