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
The application should now be running on http://localhost:8000.

# Usage
Document Loading and Indexing
The chatbot relies on pre-loaded documents for answering questions. Documents are split into chunks and embedded for efficient retrieval.
Sending Requests to the API
Once the application is running, you can send requests to the API to interact with the chatbot.

Example: Querying the Chatbot
You can use curl or any API client (like Postman) to send a POST request to the /api/excerpt/transcript endpoint with your prompt.

    curl -X POST http://localhost:8000/api/excerpt/transcript -d "user_file=vocabularies.txt" -d "user_id=dfgh-gfjfjk-hjdkk-jdjjgg" -d "username=Akin"

Example: Expected Response
The API will respond with a JSON object containing the answer.

    {
      "result": "The capital of France is Paris."
    }
API Endpoints
POST /api/excerpt/transcript: Sends a query to the chatbot and returns the answer.

Request Body: JSON object containing the prompt.

    curl -X POST http://localhost:8000/api/excerpt/transcript -d "user_file=vocabularies.txt" -d "user_id=dfgh-gfjfjk-hjdkk-jdjjgg" -d "username=Akin"
Response: JSON object containing the result.

    {
        "username": "Akin",
        "file_id": "fgh-gfjfjk-hjdkk-jdjjgg",
        "text":"The capital of France is Paris."
    }
POST /api/excerpt/chatdata: Sends a query to the chatbot and returns the answer.

Request Body: JSON object containing the prompt.

    curl -X POST http://localhost:8000/api/excerpt/chatdata -d "user_id=dfgh-gfjfjk-hjdkk-jdjjgg" -d "username=Akin"
Response: JSON object containing the result.

    {
        "username": "Akin",
        "file_id": "fgh-gfjfjk-hjdkk-jdjjgg"
    }

POST /api/excerpt/bot: Sends a query to the chatbot and returns the answer.

Request Body: JSON object containing the prompt.

    curl -X POST http://localhost:8000/api/excerpt/bot -d "user_id=dfgh-gfjfjk-hjdkk-jdjjgg" -d "username=Akin" -d "text=how are youy"
Response: JSON object containing the result.

    {
        "text": "I'm a language model AI, so I don't have feelings, but I'm here and ready to help you with any questions you have. How can I assist you today?",
        "file_id": "fgh-gfjfjk-hjdkk-jdjjgg"
    }

Deployment
The project uses Docker Compose for easy deployment. Ensure that the docker-compose.yml is correctly set up and run:
        
    docker-compose up --build


