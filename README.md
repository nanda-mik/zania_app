# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Add env variables
OPENAI_API_KEY=<>

# Run server
For WSGI server, use this command:
python manage.py runserver

for asgi server, install uvicorn and use this command
pip install uvicorn
uvicorn zania_project.asgi:application --reload

# Api endpoints
Check urls.py for endpoints and payload

# Example curl
curl --location 'http://127.0.0.1:8000/api/ask/' \
--form 'questions_file=@"<path>/questions.json"' \
--form 'document_file=@"<path>/output.pdf"'

Example response:
```JSON
{
    "answers": {
        "What is artificial intelligence?": " Artificial Intelligence is the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. It can also refer to any machine that exhibits traits associated with a human mind. Python is a popular programming language known for its simplicity and readability, developed by Guido van Rossum in 1991. Paris is the capital of France and a global center for art, fashion, gastronomy, and culture.",
        "Who developed the Python programming language?": " Guido van Rossum developed the Python programming language in 1991. Python is known for its readability and simplicity, making it a popular choice for beginners and experts alike.",
        "What is the capital of France?": " The capital of France is Paris. It is a global center for art, fashion, gastronomy, and culture.",
        "What is the largest planet in our solar system?": " I don't know. The given context does not mention any information about planets or our solar system.",
        "Hi! How are you?": " I am an AI assistant. I am not capable of feeling emotions, but I am functioning and ready to assist with any questions you may have.",
        "What is tiger's favourite food?": " I don't know.",
        "Who is Lama?": " I don't know who Lama is."
    }
}
```
