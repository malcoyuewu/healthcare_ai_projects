# Snowflake Agentic RAG System

A complete implementation of an agentic RAG (Retrieval Augmented Generation) system using Snowflake Cortex AI services and AutoGen multi-agent framework. This system combines unstructured document search with structured data analysis in a single, intelligent healthcare assistant.

## 🏥 Healthcare Focus

This system is specifically designed for healthcare applications, featuring:
- **Medical document search** using Cortex Search
- **Clinical data analysis** using Cortex Analyst  
- **Multi-agent orchestration** with specialized medical AI assistants
- **Evidence-based responses** with proper medical disclaimers

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and navigate to the project
cd snowflake_agentic_rag
Set up venv

# Install dependencies
pip install -r requirements.txt

# Setup configuration
python run.py setup
```

### 2. Configure Credentials
Edit the `.env` file with your credentials:
```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password

# LLM API Keys (at least one required)
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### 3. Run the System

**Streamlit Web App (Recommended):**
```bash
python run.py streamlit
```

**Interactive Demo:**
```bash
python run.py demo
```

**FastAPI Backend:**
```bash
python run.py api
```

## 🏗️ Architecture Overview

The system uses Snowflake's native AI capabilities to create an agentic framework that can:
- **Search unstructured data** using Cortex Search (hybrid vector + keyword search)
- **Query structured data** using Cortex Analyst (natural language to SQL)
- **Orchestrate responses** intelligently based on user intent

### Key Components

1. **Streamlit Frontend**: Modern, interactive web interface for healthcare professionals
2. **AutoGen Multi-Agent System**: Specialized medical AI assistants with domain expertise
3. **Snowflake Cortex Search**: Hybrid vector + keyword search for medical documents
4. **Snowflake Cortex Analyst**: Natural language to SQL for structured data analysis
5. **FastAPI Backend**: RESTful API for integration and programmatic access

## 🤖 Available Agents

### Clinical Research Assistant
- Specializes in medical guidelines and evidence-based medicine
- Searches medical literature and documentation
- Provides evidence-graded recommendations
- Includes appropriate medical disclaimers

### Medical Data Analyst  
- Focuses on healthcare analytics and statistics
- Analyzes patient outcomes and trends
- Provides statistical context and methodology
- Generates clinical performance metrics

## 📊 Database Schema Design

```
KNOWLEDGE_DB
├── RAW_STAGING          # Landing zone for original files
│   ├── @DOC_STAGE       # Internal stage for documents
│   └── DOCUMENT_DIRECTORY # File tracking table
├── SILVER_PROCESSED     # Cleaned, AI-ready data
│   ├── DOC_CHUNKS       # Chunked document text
│   ├── SALES_METRICS    # Sample structured data
│   └── PRODUCT_CATALOG  # Product information
└── AI_SERVICES          # Cortex services and models
    ├── DOCUMENT_SEARCH_SERVICE
    └── STRUCTURED_DATA_ANALYST
```

## 🛠️ Setup Instructions

### 1. Database Setup
```sql
-- Run the database setup script
@01_database_setup.sql
```

### 2. Create Cortex Search Service
```sql
-- Set up the search service for unstructured data
@02_cortex_search_service.sql
```

### 3. Configure Semantic Model
```sql
-- Upload the semantic model YAML
PUT file://03_semantic_model.yaml @KNOWLEDGE_DB.AI_SERVICES.SEMANTIC_MODEL_STAGE;

-- Create the Cortex Analyst service
@04_cortex_agent_setup.sql
```

### 4. Set Up Data Pipeline
```sql
-- Configure automated document processing
@05_data_ingestion_pipeline.sql
```

## 🎨 Streamlit Interface Features

### Multi-Page Application
- **🏠 Home Dashboard**: System overview, quick actions, and agent selection
- **🤖 AI Assistant**: Interactive chat with specialized medical agents
- **🔍 Direct Search**: Direct access to document search and data analysis tools
- **📊 Analytics**: Real-time system metrics, usage statistics, and performance monitoring

### Healthcare-Focused Design
- **Medical Disclaimers**: Appropriate warnings for clinical information
- **Evidence-Based Responses**: Citations and evidence grading
- **Specialized Agents**: Clinical research assistant and medical data analyst
- **Interactive Examples**: Pre-built medical queries for different specialties

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Live system status and performance metrics
- **Export Capabilities**: Download chat history and analytics data
- **Session Management**: Persistent chat history and user preferences

## 💻 Usage Examples

### Streamlit Web Interface
```bash
# Start the Streamlit application
python run.py streamlit

# Navigate to http://localhost:8501
# Use the interactive interface to:
# - Chat with AI medical assistants
# - Search medical documents directly
# - Analyze healthcare data
# - View system analytics and metrics
```

### Command Line Demo
```bash
# Start interactive demo
python run.py demo

# Example queries:
# "What are the current guidelines for diabetes screening?"
# "What is our patient satisfaction rate?"
# "Show me HbA1c trends over the past year"
```

### API Usage
```python
import requests

# Query the clinical assistant
response = requests.post("http://localhost:8000/query", json={
    "question": "What are the side effects of metformin?",
    "agent_type": "clinical"
})

print(response.json()["answer"])
```

## 🔧 Configuration

### Environment Variables
```env
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=KNOWLEDGE_DB
SNOWFLAKE_SCHEMA=AI_SERVICES

# LLM API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Multi-LLM Support
The system supports multiple LLM providers:
- **OpenAI GPT-4** - Primary recommendation engine
- **Google Gemini** - Alternative high-quality responses  
- **DeepSeek** - Cost-effective option
- **Ollama** - Local deployment option

## 📁 Project Structure

```
snowflake_agentic_rag/
├── streamlit_app.py                    # Main Streamlit application (Home)
├── streamlit_healthcare_system.py      # Streamlit-optimized healthcare system
├── pages/
│   ├── 1_🤖_AI_Assistant.py           # AI chat interface
│   ├── 2_🔍_Direct_Search.py          # Direct search tools
│   └── 3_📊_Analytics.py              # System analytics
├── .streamlit/
│   ├── config.toml                     # Streamlit configuration
│   └── secrets.toml.template           # Streamlit secrets template
├── 01_database_setup.sql               # Database schema creation
├── 02_cortex_search_service.sql        # Cortex Search setup
├── 03_semantic_model.yaml              # Semantic model for Cortex Analyst
├── 04_cortex_agent_setup.sql           # Agent and tools setup
├── 05_data_ingestion_pipeline.sql      # Data processing pipeline
├── config_cortex_search.py             # Snowflake connector
├── autogen_configs.py                  # AutoGen agent configuration
├── api.py                              # FastAPI web service (optional)
├── demo.py                             # Interactive demo
├── run.py                              # Main launcher script
├── verify_setup.py                     # Setup verification
├── requirements.txt                    # Python dependencies
├── .env.template                       # Environment template
└── README.md                           # This file
```

## 🧪 Testing

### Test API Endpoints
```bash
python run.py test
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are diabetes symptoms?", "agent_type": "clinical"}'
```

## 🔍 Key Features

### Intelligent Intent Detection
The system automatically determines whether to use:
- **Structured data queries** for numerical/analytical questions
- **Document search** for procedural/policy questions
- **Both tools** for complex queries requiring multiple data sources

### Automatic Document Processing
- **Chunking**: Documents are automatically split into searchable chunks
- **Classification**: AI-powered categorization of content
- **Metadata extraction**: Automatic tagging and department assignment

### Security & Access Control
- **Security levels** on document chunks
- **Department-based filtering** for search results
- **Role-based access** through Snowflake's native security

### Medical Safety Features
- **Evidence grading** in clinical responses
- **Source citations** for all recommendations
- **Medical disclaimers** on clinical advice
- **Structured data validation** for analytics

## 🚨 Important Notes

### Medical Disclaimer
This system is designed for informational and research purposes only. All medical recommendations should be verified with qualified healthcare professionals. The AI assistants provide evidence-based information but do not replace clinical judgment.

### Security Considerations
- Store API keys securely in environment variables
- Use appropriate Snowflake roles and permissions
- Implement proper access controls for production deployment
- Regularly update dependencies for security patches

## 🛠️ Troubleshooting

### Common Issues

**Connection Errors:**
- Verify Snowflake credentials in `.env`
- Check network connectivity to Snowflake
- Ensure warehouse is running

**Import Errors:**
- Install all requirements: `pip install -r requirements.txt`
- Check Python version compatibility (3.9+)

**API Errors:**
- Verify at least one LLM API key is configured
- Check API service status with `/health` endpoint
- Review logs for detailed error messages

### Performance Optimization
- Use appropriate warehouse sizes for different workloads
- Monitor and adjust TARGET_LAG for search services
- Optimize chunk sizes based on your content type

## 🔄 Next Steps

1. **Custom Embeddings**: Implement domain-specific embedding models
2. **Advanced Agents**: Add more specialized tools for specific use cases
3. **Enhanced UI**: Build a comprehensive web application
4. **Analytics Dashboard**: Add usage tracking and performance metrics
5. **Integration**: Connect with existing healthcare systems
6. **Compliance**: Add HIPAA and other healthcare compliance features

## 📚 Documentation

- [Snowflake Cortex AI Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [AutoGen Framework Documentation](https://microsoft.github.io/autogen/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
