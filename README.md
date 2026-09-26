# CustomSDGPT

CustomSDGPT is an open-source agentic AI chatbot built with Python and modern AI frameworks. It supports multiple language models, including Google Gemini and OpenAI models, while using LangGraph and LangChain for agent workflows, tool usage, document-based question answering, web search, conversation memory, and external data retrieval.

The application uses FastAPI for the backend and provides a lightweight web interface where users can select a supported AI model and interact with the assistant.

---

## Key Features

- AI-powered conversations using Google Gemini and OpenAI models
- Model selection directly from the web interface
- LangGraph-based agent workflow and tool execution
- Real-time streaming responses
- Upload and process PDF, DOCX, TXT, MD, PY, and CSV files
- Retrieval-Augmented Generation (RAG) for questions about uploaded documents
- Current web information retrieval through Tavily
- County-level public health data retrieval through CDC PLACES
- Conversation history and memory support
- ChromaDB-based vector storage and retrieval
- SQLite-based application data and LangGraph checkpoint storage
- Simple browser-based chat interface
- Docker support for containerized deployment
- AWS deployment workflow with GitHub Actions, Amazon ECR, and EC2

---

## How It Works

CustomSDGPT brings several components together to create an agentic chatbot:

- **FastAPI** handles the backend server and API requests.
- **Jinja2** renders the web interface.
- **LangGraph** manages the agent workflow, tool execution, and decision flow.
- **LangChain** provides model integrations, message handling, tools, and RAG-related components.
- **Google Gemini** provides supported Gemini language models.
- **OpenAI** provides supported GPT language models.
- **Tavily** allows the agent to retrieve current information from the web.
- **CDC PLACES** provides county-level public health information through a custom tool.
- **ChromaDB** stores embeddings for uploaded documents and supports similarity search.
- **SQLite** stores conversation-related application data and LangGraph checkpoints.
- **Docker** packages the application for consistent deployment.

The basic LangGraph tool workflow is:

```text
User
  ↓
Selected AI Model
  ↓
LangGraph Chatbot Node
  ↓
Does the model need a tool?
   ↙              ↘
 No               Yes
 ↓                 ↓
Answer          ToolNode
                   ↓
                 Tool
                   ↓
              Tool Result
                   ↓
             Chatbot Node
                   ↓
              Final Answer
```

This allows the selected language model to decide whether it can answer a question directly or whether it should use one of the available tools.

---

## Requirements

Before running the project, make sure the following are available:

- Python 3.11
- pip or conda
- Git
- Google API key for Gemini
- OpenAI API key for OpenAI models
- Tavily API key for web search

For cloud deployment, you may also need:

- Docker
- AWS account
- Amazon ECR repository
- Amazon EC2 instance
- GitHub Actions self-hosted runner

---

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/shk0224/CustomSDGPT.git
```

### 2. Open the Project Directory

```bash
cd CustomSDGPT
```

### 3. Create a Conda Environment

```bash
conda create -n customsdgpt python=3.11 -y
```

### 4. Activate the Environment

```bash
conda activate customsdgpt
```

### 5. Install the Required Packages

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file inside the project root directory and add the required API configuration.

```env
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-2.5-flash

OPENAI_API_KEY=your_openai_api_key

TAVILY_API_KEY=your_tavily_api_key

LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=customsdgpt
```

If LangSmith tracing is not required, leave:

```env
LANGSMITH_TRACING=false
```

Never commit your real API keys to the repository.

---

## Running the Application

Start the FastAPI application with:

```bash
python app.py
```

After the server starts, open:

```text
http://127.0.0.1:8080
```

in your browser.

---

## Project Structure

```text
CustomSDGPT/
│
├── app.py                  # FastAPI application and chat endpoints
├── agent.py                # LangGraph agent workflow and model selection
├── database.py             # Conversation and persistence operations
├── rag.py                  # Document processing and RAG functionality
├── tools.py                # Tools available to the AI agent
├── requirements.txt        # Project dependencies
├── Dockerfile              # Docker image configuration
├── .dockerignore           # Files excluded from Docker builds
├── .gitignore              # Files excluded from Git
│
├── templates/
│   └── index.html          # Web interface
│
├── uploads/                # Uploaded user documents
├── data/                   # SQLite databases and application data
└── chroma_db/              # ChromaDB vector storage
```

---

## Available Agent Capabilities

The LangGraph agent can use different capabilities depending on the user's request.

### Normal Conversation

The selected Gemini or OpenAI model can answer normal questions directly without using an external tool.

### Web Search

For current or time-sensitive information, the agent can use Tavily to retrieve information from the web.

### Document Search

Uploaded documents are processed and stored for Retrieval-Augmented Generation (RAG). The agent can retrieve relevant information when the user asks questions about uploaded files.

### Conversation Memory

The application includes tools for saving and recalling useful information associated with conversations.

### Calculator

The agent can use a calculator tool for supported mathematical calculations.

### CDC PLACES Community Health Tool

CustomSDGPT includes a custom public health data tool that retrieves supported county-level health information from CDC PLACES.

For example, the user can ask:

```text
What is the diabetes prevalence in Cherokee County, Georgia?
```

The agent can determine that the CDC PLACES tool is appropriate, call the tool, receive the public health data, and use the result to generate a readable response.

---

## Model Selection

CustomSDGPT supports model selection from the web interface.

The application can route requests to supported models from different providers while keeping the same LangGraph workflow and tools.

The general model flow is:

```text
User selects a model
        ↓
     FastAPI
        ↓
   LangGraph Agent
        ↓
Selected Model Provider
   ↙             ↘
Gemini          OpenAI
   \             /
    \           /
     Same Tools
        ↓
   Final Answer
```

This design allows the application to use different language model providers without creating a separate agent workflow for every provider.

---

## Docker Setup

### Build the Docker Image

```bash
docker build -t customsdgpt .
```

### Start the Container

```bash
docker run -d \
  --name customsdgpt \
  --restart always \
  -p 8080:8080 \
  --env-file .env \
  customsdgpt
```

Once the container is running, the application can be accessed at:

```text
http://localhost:8080
```

---

## AWS Deployment

CustomSDGPT can also be deployed to AWS using a CI/CD workflow built around:

- GitHub Actions
- Amazon ECR
- Amazon EC2
- Docker
- GitHub self-hosted runner

The general deployment flow is:

```text
Code pushed to GitHub
        ↓
GitHub Actions
        ↓
Build Docker image
        ↓
Push image to Amazon ECR
        ↓
EC2 pulls latest image
        ↓
New container starts
        ↓
Updated application becomes available
```

---

### 1. Configure IAM Access

Create an IAM user for the deployment workflow.

The following AWS managed policies can be used for a basic setup:

```text
AmazonEC2ContainerRegistryFullAccess
AmazonEC2FullAccess
```

For a production environment, a more restrictive IAM policy following the principle of least privilege is recommended.

---

### 2. Create an Amazon ECR Repository

Create an ECR repository for the Docker image.

An ECR image URI may look similar to:

```text
315865595366.dkr.ecr.us-east-1.amazonaws.com/customsdgpt
```

For the GitHub secret, store only the repository name:

```text
ECR_REPO=customsdgpt
```

The complete ECR URI should not be used as the value of `ECR_REPO`.

---

### 3. Prepare an EC2 Instance

Launch an Ubuntu EC2 instance that will host the application.

To make the application reachable on port `8080`, configure the required EC2 security group rule.

Example:

```text
Type: Custom TCP
Port: 8080
Source: 0.0.0.0/0
```

For a production deployment, access rules should be restricted appropriately.

---

### 4. Install Docker on EC2

Connect to the EC2 instance and update the system:

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
```

Install Docker:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Add the Ubuntu user to the Docker group:

```bash
sudo usermod -aG docker ubuntu
newgrp docker
```

Verify the installation:

```bash
docker --version
```

---

### 5. Set Up the GitHub Self-Hosted Runner

From the GitHub repository, navigate to:

```text
Settings → Actions → Runners → New self-hosted runner
```

Choose Linux and follow the setup instructions provided by GitHub.

The runner can be started with:

```bash
./run.sh
```

For a longer-running deployment environment, the runner can also be configured as a service:

```bash
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## GitHub Secrets

Store sensitive deployment configuration in GitHub Actions Secrets rather than directly in the source code.

Required values may include:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
ECR_REPO

GOOGLE_API_KEY
GEMINI_MODEL
OPENAI_API_KEY
TAVILY_API_KEY
LANGSMITH_TRACING
LANGSMITH_ENDPOINT
LANGSMITH_API_KEY
LANGSMITH_PROJECT
```

These can be configured from:

```text
GitHub Repository
→ Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Example configuration:

```text
AWS_DEFAULT_REGION=us-east-1
ECR_REPO=customsdgpt
GEMINI_MODEL=gemini-2.5-flash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=customsdgpt
```

Never store actual API keys directly in the source code or README file.

---

## GitHub Actions CI/CD

The GitHub Actions workflow can be stored at:

```text
.github/workflows/cicd.yaml
```

The workflow is responsible for automating the deployment process. A typical run performs the following tasks:

1. Builds the latest Docker image.
2. Pushes the image to Amazon ECR.
3. Makes the latest image available to the EC2 environment.
4. Stops or replaces the previous application container.
5. Starts the updated CustomSDGPT container.

---

## Using CustomSDGPT

After starting the application locally or deploying it to a server, you can:

1. Select a supported Gemini or OpenAI model.
2. Start a normal conversation with the AI assistant.
3. Upload supported documents.
4. Ask questions based on uploaded content using RAG.
5. Request current information using web search.
6. Retrieve supported county-level public health information from CDC PLACES.
7. Perform calculations and other supported tool-based tasks.
8. Continue conversations using stored chat history and memory.

---

## Example Prompts

### Normal Conversation

```text
Explain LangGraph in simple terms.
```

### Ask About an Uploaded Document

```text
Summarize the uploaded PDF.
```

### Search for Current Information

```text
Search the web for the latest AI agent news.
```

### Use Document Context

```text
Based on my uploaded document, what are the key points?
```

### Use the Calculator

```text
Calculate 125 * 48 / 6.
```

### Use the CDC PLACES Tool

```text
What is the diabetes prevalence in Cherokee County, Georgia?
```

Another example:

```text
What is the diabetes prevalence in Forsyth County, Georgia?
```

---

## Security and Deployment Notes

- Never commit the `.env` file or API keys to GitHub.
- Store deployment credentials using GitHub Secrets.
- Keep local application data, uploaded files, and vector databases out of the public repository when appropriate.
- Avoid using `reload=True` when running Uvicorn in production.
- Make sure the required application port is correctly configured.
- Use restrictive security group and IAM permissions for production deployments.
- Rotate any credential or API key that may have been accidentally exposed.

---

## Contributing

Contributions and improvements are welcome.


---

## License

CustomSDGPT is an open-source project. Refer to the repository's license file for the applicable usage and distribution terms.