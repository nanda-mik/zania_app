## Overview

The Zania App is a Django-based application that provides asynchronous and synchronous APIs for processing documents and answering questions. The app utilizes OpenAI's capabilities to generate answers from provided documents.

## Getting Started

Follow these instructions to set up and run the application locally.

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. **Create a Virtual Environment**  
   Create a virtual environment to manage dependencies:

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**
     ```bash
     source venv/bin/activate
     ```

3. **Install Required Packages**  
   Install the necessary packages using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**  
   Add your OpenAI API key to the environment variables in .env file:

   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   ```

### Running the Server

- **For WSGI Server:**
  
  ```bash
  python manage.py runserver
  ```

- **For ASGI Server:**
  1. Install Uvicorn:
     ```bash
     pip install uvicorn
     ```
  2. Run the server with Uvicorn:
     ```bash
     uvicorn zania_project.asgi:application --reload
     ```

### API Endpoints

Check the `urls.py` file for available endpoints and their corresponding payload formats.

### Example Request

You can test the API using the following `curl` command:

```bash
curl --location 'http://127.0.0.1:8000/api/ask/' \
--form 'questions_file=@"<path>/questions.json"' \
--form 'document_file=@"<path>/output.pdf"'
```

### Example Response

A successful response will return answers in the following JSON format:

```json
{
    "answers": {
        "What is artificial intelligence?": "Artificial Intelligence is the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. It can also refer to any machine that exhibits traits associated with a human mind. Python is a popular programming language known for its simplicity and readability, developed by Guido van Rossum in 1991. Paris is the capital of France and a global center for art, fashion, gastronomy, and culture.",
        "Who developed the Python programming language?": "Guido van Rossum developed the Python programming language in 1991. Python is known for its readability and simplicity, making it a popular choice for beginners and experts alike.",
        "What is the capital of France?": "The capital of France is Paris. It is a global center for art, fashion, gastronomy, and culture.",
        "What is the largest planet in our solar system?": "I don't know. The given context does not mention any information about planets or our solar system.",
        "Hi! How are you?": "I am an AI assistant. I am not capable of feeling emotions, but I am functioning and ready to assist with any questions you may have.",
        "What is tiger's favourite food?": "I don't know.",
        "Who is Lama?": "I don't know who Lama is."
    }
}
```

