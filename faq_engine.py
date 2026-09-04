"""
faq_engine.py - Core retrieval-augmented FAQ search engine.

Loads text and markdown FAQ documents, splits them into question-answer
chunks, builds a TF-IDF vector index, and finds the closest matching answer
for any incoming user query using cosine similarity.
"""

import os
import re
import math
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple


class FAQChunk:
    """Represents a single Q&A pair or text segment in the knowledge base."""

    def __init__(self, question: str, answer: str, source: str, chunk_id: int):
        self.question = question.strip()
        self.answer = answer.strip()
        self.source = source
        self.chunk_id = chunk_id
        # Full text combined for semantic search
        self.full_text = f"{self.question} {self.answer}"
        self.tokens = self._tokenize(self.full_text)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Convert text to lowercase tokens, stripping punctuation and short noise."""
        words = re.findall(r"\b[a-z0-9_]{2,}\b", text.lower())
        # Common English stop words to ignore for better relevance matching
        stop_words = {
            "the", "is", "at", "which", "on", "a", "an", "and", "or", "in", "to",
            "for", "of", "with", "as", "by", "from", "it", "this", "that", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "can", "could", "should", "would", "will", "i", "you",
            "we", "they", "my", "your", "our", "their", "me", "him", "her", "us"
        }
        return [w for w in words if w not in stop_words]


class FAQEngine:
    """
    Search and retrieval engine for FAQ collections.
    Computes TF-IDF vector representations and cosine similarity.
    """

    def __init__(self, documents_dir: Optional[str] = None):
        self.documents_dir = documents_dir
        self.chunks: List[FAQChunk] = []
        self.idf: Dict[str, float] = {}
        self.vocab: Dict[str, int] = {}
        self.chunk_vectors: List[Dict[str, float]] = []

        if documents_dir and os.path.exists(documents_dir):
            self.load_directory(documents_dir)

    def load_directory(self, folder_path: str) -> int:
        """Loads and indexes all .txt and .md files in the given directory."""
        self.chunks = []
        chunk_counter = 0

        for file_name in sorted(os.listdir(folder_path)):
            if file_name.endswith((".txt", ".md")):
                full_path = os.path.join(folder_path, file_name)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                parsed_chunks = self._parse_faq_text(content, source_name=file_name, start_id=chunk_counter)
                self.chunks.extend(parsed_chunks)
                chunk_counter += len(parsed_chunks)

        self._build_index()
        return len(self.chunks)

    def add_document(self, content: str, source_name: str) -> int:
        """Dynamically add and re-index a new document."""
        new_chunks = self._parse_faq_text(content, source_name=source_name, start_id=len(self.chunks))
        self.chunks.extend(new_chunks)
        self._build_index()
        return len(new_chunks)

    def _parse_faq_text(self, text: str, source_name: str, start_id: int) -> List[FAQChunk]:
        """
        Splits text by '## Q:' or 'Q:' patterns into question-answer pairs.
        Falls back to double-newline paragraphs if Q&A markers are absent.
        """
        chunks = []
        pattern = r"(?:^|\n)##?\s*Q:\s*(.*?)\n(?:##?\s*A:\s*|A:\s*)(.*?)(?=(?:\n##?\s*Q:|\Z))"
        matches = list(re.finditer(pattern, text, re.DOTALL | re.IGNORECASE))

        if matches:
            for i, match in enumerate(matches):
                q = match.group(1).strip()
                a = match.group(2).strip()
                if q and a:
                    chunks.append(FAQChunk(question=q, answer=a, source=source_name, chunk_id=start_id + i))
        else:
            # Fallback: Split by double newlines into paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
            for i, p in enumerate(paragraphs):
                first_line = p.split("\n")[0].strip("# ")
                body = "\n".join(p.split("\n")[1:]).strip() or p
                chunks.append(FAQChunk(question=first_line, answer=body, source=source_name, chunk_id=start_id + i))

        return chunks

    def _build_index(self):
        """Builds word frequencies, IDF weights, and unit TF-IDF vectors for all chunks."""
        total_docs = len(self.chunks)
        if total_docs == 0:
            return

        # 1. Document Frequency (DF)
        doc_freq = Counter()
        for chunk in self.chunks:
            unique_words = set(chunk.tokens)
            for word in unique_words:
                doc_freq[word] += 1

        # 2. Inverse Document Frequency (IDF) with smoothing
        self.idf = {
            word: math.log((1.0 + total_docs) / (1.0 + count)) + 1.0
            for word, count in doc_freq.items()
        }

        # 3. Compute TF-IDF unit vectors for each chunk
        self.chunk_vectors = []
        for chunk in self.chunks:
            tf = Counter(chunk.tokens)
            vector = {}
            squared_sum = 0.0

            for word, count in tf.items():
                tfidf_val = count * self.idf.get(word, 1.0)
                vector[word] = tfidf_val
                squared_sum += tfidf_val ** 2

            norm = math.sqrt(squared_sum) or 1.0
            unit_vector = {w: v / norm for w, v in vector.items()}
            self.chunk_vectors.append(unit_vector)

    def _vectorize_query(self, query: str) -> Dict[str, float]:
        """Convert a user question into a normalized TF-IDF vector."""
        tokens = FAQChunk._tokenize(query)
        tf = Counter(tokens)
        vector = {}
        squared_sum = 0.0

        for word, count in tf.items():
            if word in self.idf:
                tfidf_val = count * self.idf[word]
                vector[word] = tfidf_val
                squared_sum += tfidf_val ** 2

        norm = math.sqrt(squared_sum) or 1.0
        return {w: v / norm for w, v in vector.items()}

    def ask(self, query: str, top_k: int = 3, threshold: float = 0.15) -> Dict[str, Any]:
        """
        Retrieves the best matching answer for the user query.
        Returns answer text, matched question, confidence score (0-100%), and sources.
        """
        if not query.strip():
            return {
                "answer": "Please ask a question so I can help you.",
                "confidence": 0,
                "sources": [],
                "matched_question": "",
                "related_questions": []
            }

        if not self.chunks:
            return {
                "answer": "The knowledge base is currently empty. Please load or upload FAQ documents first.",
                "confidence": 0,
                "sources": [],
                "matched_question": "",
                "related_questions": []
            }

        q_vec = self._vectorize_query(query)
        scored_chunks: List[Tuple[float, FAQChunk]] = []

        # Cosine similarity dot product between unit vectors
        for i, doc_vec in enumerate(self.chunk_vectors):
            dot_product = sum(weight * doc_vec.get(word, 0.0) for word, weight in q_vec.items())
            
            # Boost score if words match directly in the question title
            query_tokens = set(FAQChunk._tokenize(query))
            question_tokens = set(FAQChunk._tokenize(self.chunks[i].question))
            overlap = len(query_tokens.intersection(question_tokens))
            if overlap > 0:
                dot_product += 0.15 * min(overlap / max(len(query_tokens), 1), 1.0)

            scored_chunks.append((dot_product, self.chunks[i]))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_score, best_chunk = scored_chunks[0]

        # Calculate a realistic confidence percentage (0 to 100)
        confidence = min(int(round(top_score * 100)), 99)

        if top_score < threshold or confidence < 20:
            # Low confidence fallback with related suggestions
            related = [
                c.question for s, c in scored_chunks[:3] if s > 0.05
            ]
            return {
                "answer": (
                    "I couldn't find a direct answer to that question in the knowledge base. "
                    "Try rephrasing your question or see if one of the related topics below helps."
                ),
                "confidence": max(confidence, 15),
                "sources": [best_chunk.source] if related else [],
                "matched_question": "",
                "related_questions": related
            }

        # High / Medium confidence match
        sources = list(dict.fromkeys([c.source for s, c in scored_chunks[:top_k] if s > threshold]))
        related = [c.question for s, c in scored_chunks[1:4] if s > 0.10 and c.question != best_chunk.question]

        return {
            "answer": best_chunk.answer,
            "confidence": confidence,
            "sources": sources,
            "matched_question": best_chunk.question,
            "related_questions": related
        }

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on loaded documents and chunks."""
        doc_counts = Counter(c.source for c in self.chunks)
        return {
            "total_chunks": len(self.chunks),
            "documents": [
                {"name": doc, "chunks": count} for doc, count in doc_counts.items()
            ]
        }
