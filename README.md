# vibelinkmodel

# JacobRyanMedia Chatbot Project

This project showcases the use of Retrieval-Augmented Generation (RAG) to build a sophisticated chatbot. The chatbot leverages OpenAI embeddings and Chroma for document storage and retrieval, providing an enhanced question-answering experience. This project is containerized using Docker Compose for easy deployment.

## Features

- **RAG Implementation**: Combines document retrieval with powerful language models to answer questions based on the provided documents.
- **Document Indexing**: Uses Chroma for efficient document storage and retrieval.
- **Embeddings**: Utilizes OpenAI embeddings for high-quality semantic search.
- **Dockerized Deployment**: Simplifies deployment using Docker Compose.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/JacobRyanMedia.git
   cd JacobRyanMedia

Set up environment variables:
Create a .env file in the root directory and add your OpenAI API key:

    API_KEY=your_openai_api_key
Build and run the Docker containers:

    docker-compose up --build
# Access the application:
The application should now be running on http://localhost:8000/chatbot.

