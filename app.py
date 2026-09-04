"""
app.py - Web server and REST API for AI Chatbot for FAQs.

Provides a web interface and HTTP endpoints for interacting with the
FAQ retrieval engine.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from faq_engine import FAQEngine

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "faq_documents")
ALLOWED_EXTENSIONS = {".txt", ".md", ".json"}

# Ensure document folder exists
os.makedirs(DOCS_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")
CORS(app)

# Load FAQ retrieval engine
engine = FAQEngine(DOCS_DIR)
print(f"Loaded {len(engine.chunks)} FAQ chunks from {DOCS_DIR}")


@app.route("/")
def index():
    """Serve the chatbot web application."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "FAQ Chatbot RAG Service",
        "total_chunks": len(engine.chunks)
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Query endpoint.
    Expects JSON: { "query": "What are your support hours?" }
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Empty question provided."}), 400

    result = engine.ask(query)
    return jsonify(result)


@app.route("/api/documents", methods=["GET"])
def list_documents():
    """Returns a list of loaded documents and chunk counts."""
    stats = engine.get_stats()
    return jsonify(stats)


@app.route("/api/documents/upload", methods=["POST"])
def upload_document():
    """
    Upload a new .txt or .md FAQ document to expand the knowledge base.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Invalid file."}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(DOCS_DIR, filename)
    file.save(save_path)

    # Read content and add to active index
    with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    new_chunks = engine.add_document(content, filename)

    return jsonify({
        "message": f"Successfully indexed '{filename}'!",
        "new_chunks": new_chunks,
        "total_chunks": len(engine.chunks)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nStarting FAQ Chatbot Server on http://localhost:{port}")
    print("Press Ctrl+C to stop.\n")
    app.run(host="0.0.0.0", port=port, debug=True)
