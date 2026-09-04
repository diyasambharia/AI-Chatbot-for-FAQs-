# System Architecture & Technical Design

This document explains the internal architecture, mathematical principles, and retrieval pipeline of the **AI Chatbot for FAQs**.

---

## 🏗️ Architectural Overview

The application implements a lightweight, deterministic **Retrieval-Augmented Generation (RAG)** architecture designed to deliver accurate, grounded answers from knowledge base documents with zero hallucinations and zero external API fees.

```
+------------------+       +-------------------+       +-----------------------+
|  FAQ Documents   | ----> |  Smart Chunking   | ----> |  TF-IDF Vector Store  |
|  (.txt, .md)     |       |  (Q&A Extractor)  |       |  (Unit Normalized)    |
+------------------+       +-------------------+       +-----------------------+
                                                                   |
                                                                   v
+------------------+       +-------------------+       +-----------------------+
|  Answer + Source | <---- | Confidence & Rank | <---- |   Cosine Similarity   |
|  + Citations     |       | (Title Match Boost)       | (User Query vs Chunks)|
+------------------+       +-------------------+       +-----------------------+
                                                                   ^
                                                                   |
                                                       +-----------------------+
                                                       |   User Question       |
                                                       +-----------------------+
```

---

## ⚙️ Core Pipeline Components

### 1. Document Ingestion & Chunking
- **Input**: Raw text (`.txt`), markdown (`.md`), or JSON files containing FAQ knowledge.
- **Chunking Strategy**: Rather than arbitrary fixed-length sliding windows (which split questions across sentences), the parser uses regex pattern matching targeting semantic question-answer boundaries (`## Q: ... A: ...`).
- **Metadata Tagging**: Each chunk retains its origin filename (`source`), unique identifier (`chunk_id`), extracted question, and answer body.

### 2. Text Normalization & Tokenization
- Lowercase normalization.
- Punctuation removal and alphanumeric token extraction (`\b[a-z0-9_]{2,}\b`).
- **Stop-Word Filtering**: Common grammatical filler words (`the`, `is`, `at`, `which`, `on`, etc.) are removed to concentrate weight on high-value semantic terms (e.g., `pricing`, `password`, `support`, `sla`).

### 3. Vector Space Model (TF-IDF)
Each chunk $d$ is converted into a vector in a shared vocabulary space:

$$\text{TF}(t, d) = \text{Count of term } t \text{ in document } d$$

$$\text{IDF}(t, D) = \ln\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1.0$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

Vectors are subsequently **L2-normalized** into unit vectors:

$$\mathbf{v}_d = \frac{\mathbf{x}_d}{\|\mathbf{x}_d\|_2}$$

### 4. Query Vectorization & Cosine Similarity
When a user submits a query $q$:
1. The query undergoes the identical tokenization and IDF weighting.
2. The dot product between the normalized query vector $\mathbf{v}_q$ and chunk vector $\mathbf{v}_d$ directly yields the **Cosine Similarity**:

$$\text{Similarity}(q, d) = \mathbf{v}_q \cdot \mathbf{v}_d = \sum_{t \in q \cap d} v_q(t) \cdot v_d(t)$$

3. **Title Match Boost**: If tokens in the query directly match tokens in the chunk's question title, a boost factor (up to $+0.20$) is added to favor direct Q&A intent.

### 5. Dynamic Confidence Scoring
The similarity score is scaled to an intuitive percentage (0% to 99%):
- **High Confidence ($\ge 75\%$)**: Strong semantic match. The answer is directly returned with source document citation.
- **Medium Confidence ($50\% - 74\%$)**: Relevant information found; primary answer provided along with related question chips.
- **Low Confidence ($< 50\%$)**: Graceful fallback explaining that the specific topic wasn't found, suggesting the closest related topics to prevent hallucination.

---

## 🌐 Dual-Mode Deployment Architecture

| Capability | Client-Side (GitHub Pages) | Server-Side (Flask / Python) |
| :--- | :--- | :--- |
| **Hosting** | Free on GitHub Pages (Static) | Local machine, Docker, or Cloud VM |
| **Engine** | Pure JavaScript RAG Engine (`ClientFAQEngine`) | Pure Python Engine (`faq_engine.py`) |
| **External Dependencies** | None (Runs directly in browser) | `flask`, `flask-cors` |
| **Latency** | $< 5\text{ ms}$ (zero network round-trip) | $< 15\text{ ms}$ |
| **Document Uploads** | Browser memory / `localStorage` | Server disk filesystem (`faq_documents/`) |
| **Privacy** | 100% Client-side (queries stay on device) | Controlled server environment |

---

## 📈 Comparison: Sparse vs. Dense Embeddings

| Metric | This System (TF-IDF + Cosine) | Dense Neural Embeddings (OpenAI / HuggingFace) |
| :--- | :--- | :--- |
| **API Cost** | **\$0.00 (Zero)** | Pay-per-token API fees |
| **Inference Speed** | **$\approx 1\text{ ms}$** | $200 - 800\text{ ms}$ (network + GPU) |
| **Offline Capability** | **Yes (100% offline)** | Requires active internet & API keys |
| **Exact Keyword Matching** | **Superior** (Product names, codes, pricing) | Sometimes blurs specific numerical values |
| **Deployment Complexity** | **Zero setup (Open in any browser)** | Requires vector databases (Chroma/Pinecone) |
