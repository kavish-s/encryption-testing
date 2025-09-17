# Encryption Testing Web App

This project is a Flask web application for comparing standard AES encryption and chunked AES encryption (with HMAC) on uploaded files. It provides a modern Bootstrap UI, logs all comparisons, and visualizes performance with tables and graphs.

## Features
- Upload files and compare AES vs Chunked AES encryption
- View time and size comparisons in a table
- Visualize encryption times with a graph
- Persistent logging of all comparisons

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Visit `http://localhost:5000` in your browser.

## Project Structure
- `app.py` - Flask application
- `helpers/` - Encryption and logging helpers
- `templates/` - HTML templates
- `uploads/` - Temporary file storage
- `data/` - Keys and comparison logs

## License
MIT
