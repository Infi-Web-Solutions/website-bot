
# Website Bot

A Django-based web application that serves as a web scraper and chatbot platform. This project allows users to create a personalized bot, upload documents (like PDFs), and scrape URLs to create a knowledge base. The bot, powered by LangChain and LangGraph, can then answer user questions based on this stored information.

---

## Features

- **User Authentication**: Secure signup and login functionality.  
- **Personalized Bots**: Each user can create a single bot.  
- **Knowledge Base Creation**:
  - **PDF Upload**: Upload PDF files, which are chunked and stored in a vector database.
  - **URL Scraping**: Scrape a given URL to extract content and add it to the knowledge base.  
- **RAG Chatbot**: A Retrieval-Augmented Generation (RAG) chatbot uses the stored knowledge to provide context-aware answers to user queries.  
- **Stateful Conversation**: The chatbot maintains a conversation history to provide more coherent and relevant responses.  
- **PostgreSQL with PGVector**: The project uses a PostgreSQL database with the pgvector extension for efficient vector embeddings and similarity searches.

---

## Technology Stack

- **Backend**: Django  
- **Frontend**: HTML, CSS  
- **Database**: PostgreSQL with pgvector  
- **AI/ML**:
  - **LangChain**: For document loading, text splitting, and interaction with the vector store.
  - **LangGraph**: To define and manage the stateful RAG workflow.
  - **OpenAI API**: For embeddings and the Language Model (LLM).  
- **Web Scraping**: `scrapy`, `requests`, `BeautifulSoup`, `trafilatura`  
- **Environment Management**: `python-dotenv`

---

## Prerequisites

Before running this project, you need to have the following installed:

- Python 3.8+  
- PostgreSQL with the pgvector extension enabled.

---

## Setup and Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/Infi-Web-Solutions/website-bot.git
    cd scrapperchatbot
    ```

2. **Set up a virtual environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    > **Note**: A `requirements.txt` file is not included in the provided code, but you will need to create one with all the necessary libraries like `Django`, `psycopg2-binary`, `langchain`, `langgraph`, `openai`, `beautifulsoup4`, `requests`, etc.

4. **Configure environment variables**:  
   Create a `.env` file in the project’s root directory and add the following:

    ```dotenv
    # OpenAI API Key
    OPENAI_API_KEY="your_openai_api_key_here"

    # PostgreSQL Connection String
    # Format: postgresql+psycopg://user:password@host:port/database
    COLLECTION_STRING="postgresql+psycopg://your_user:your_password@localhost:5432/your_database"
    ```

5. **Database setup**:

    Ensure your PostgreSQL database is running and has the pgvector extension enabled.

    Run migrations to create the necessary database tables:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Start the Django development server**:

    ```bash
    python manage.py runserver
    ```

---

## Workflow

### RAG System (`views.py`)

The core of the chatbot is a RAG (Retrieval-Augmented Generation) system powered by LangGraph.

- **Graph State**: A `GraphState` dictionary tracks the flow of information, including:
  - User’s question  
  - Retrieved documents  
  - Chat history  
  - Collection name  

- **`retrieve` Node**:  
  Performs a similarity search on the PostgreSQL vector store using the user’s question. It retrieves the most relevant document chunks based on their vector embeddings.

- **`generate` Node**:  
  The retrieved documents are passed to this node, which serves as the context for the LLM. It uses a predefined system prompt (`rag_prompt`) along with the user’s question and chat history to generate a final, coherent response.

- **Workflow**: The `StateGraph` defines a simple, linear flow:
  1. The process starts at the `retrieve` node.  
  2. The output of the `retrieve` node is passed to the `generate` node.  
  3. The output of the `generate` node marks the **END** of the process.

This architecture ensures that the LLM's response is grounded in the information from the knowledge base, preventing hallucinations and providing accurate, context-specific answers.

---

## URLs

Below are the main endpoints available in the application for navigation:

- **Home/Dashboard**:  
  http://127.0.0.1:8000/webscrapper/

- **Login**:  
  http://127.0.0.1:8000/webscrapper/login/

- **Signup**:  
http://127.0.0.1:8000/webscrapper/signup/


- **Chatbot Interface**:  
  http://127.0.0.1:8000/webscrapper/chatbot/
