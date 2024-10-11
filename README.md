# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
.\venv\Scripts\activate

# Activate the virtual environment (macOS/Linux)
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Run server
python manage.py runserver

# Api endpoints
Check urls.py for endpoints and payload
