"""
tests/test_api.py - Unit tests for Flask API and FAQ Engine.
"""

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from faq_engine import FAQEngine


def test_faq_engine_initialization():
    engine = FAQEngine("faq_documents")
    assert len(engine.chunks) >= 20, "Should load at least 20 FAQ chunks"
    stats = engine.get_stats()
    assert stats["total_chunks"] >= 20


def test_faq_engine_retrieval():
    engine = FAQEngine("faq_documents")
    res = engine.ask("What are your support hours?")
    assert res["confidence"] > 40
    assert "technical_support.txt" in res["sources"]
    assert "8:00 AM" in res["answer"] or "Monday" in res["answer"]


def test_flask_health_endpoint():
    client = app.test_client()
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json["status"] == "healthy"


def test_flask_documents_endpoint():
    client = app.test_client()
    res = client.get("/api/documents")
    assert res.status_code == 200
    assert len(res.json["documents"]) == 5


def test_flask_chat_endpoint():
    client = app.test_client()
    res = client.post("/api/chat", json={"query": "How do I reset my password?"})
    assert res.status_code == 200
    data = res.json
    assert data["confidence"] > 50
    assert "security_and_privacy.txt" in data["sources"]


if __name__ == "__main__":
    print("Running FAQ Chatbot test suite...")
    test_faq_engine_initialization()
    print("[PASS] Engine initialization passed")
    test_faq_engine_retrieval()
    print("[PASS] Engine retrieval passed")
    test_flask_health_endpoint()
    print("[PASS] Health endpoint passed")
    test_flask_documents_endpoint()
    print("[PASS] Documents endpoint passed")
    test_flask_chat_endpoint()
    print("[PASS] Chat query endpoint passed")
    print("\nAll 5 automated tests PASSED successfully!")
