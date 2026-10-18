# 📚 LitLens — NLP-Based Spoiler-Aware Reading Companion

LitLens is an NLP-powered reading companion designed to help readers understand books without exposing information they have not yet read.

The core idea is simple:

> **Read → Get confused → Ask LitLens → Understand without spoilers → Continue reading.**

---

## 🚧 Project Status

**Overall Status:** 🟡 In Development

| Phase    | Description                        | Status    |
| -------- | ---------------------------------- | --------- |
| Phase 1  | 📖 Book Upload                     | DONE |
| Phase 2  | ⚙️ Book Processing                 | DONE |
| Phase 3  | 🧩 Chunk Storage                   | DONE |
| Phase 4  | 🔎 Question Processing & Retrieval | ⏳ Pending |
| Phase 5  | 🛡️ Spoiler Protection             | ⏳ Pending |
| Phase 6  | 💬 Question Answering              | ⏳ Pending |
| Phase 7  | 👤 Character Intelligence          | ⏳ Pending |
| Phase 8  | 🕸️ Character Relationships        | ⏳ Pending |
| Phase 9  | 📖 Reading Interface               | ⏳ Pending |
| Phase 10 | 📊 Evaluation                      | ⏳ Pending |
| Phase 11 | 🚀 Documentation & Deployment      | ⏳ Pending |

> The architecture and phases may evolve during development as implementation and experimentation reveal better approaches.

---

# 🏗️ Development Pipeline

The initial LitLens pipeline is:

```text
Book Upload
     ↓
Book Processing
     ↓
Chapter Detection
     ↓
Text Preprocessing
     ↓
Chunk Creation
     ↓
Chunk Storage
     ↓
Book / NLP Intelligence
     ↓
User Question
     ↓
Current Reading Position
     ↓
Spoiler / Access Filter
     ↓
Relevant Chunk Retrieval
     ↓
Answer Generation
     ↓
Answer + Sources
```

The system follows the principle:

> **Process once, retrieve many times.**

The book should not be processed from scratch every time the user asks a question.

---

# 📌 Phase 1 — Book Upload

**Status:** ⏳ Pending

The user uploads a supported book file to LitLens.

### Goals

* Accept book files
* Validate uploaded files
* Store the original book
* Create a book record
* Extract basic metadata where possible

### Expected Output

```text
Uploaded Book
      ↓
Book Record
      ↓
Stored Original File
```

### GitHub Issue

`Phase 1: Implement Book Upload`

---

# ⚙️ Phase 2 — Book Processing

**Status:** ⏳ Pending

The uploaded book is processed into structured textual information.

### Goals

* Extract text
* Detect chapters
* Preserve chapter boundaries
* Clean unnecessary text
* Prepare content for NLP processing

### Expected Output

```text
Book
 ↓
Extracted Text
 ↓
Detected Chapters
 ↓
Structured Chapter Data
```

### GitHub Issue

`Phase 2: Implement Book Processing Pipeline`

---

# 🧩 Phase 3 — Chunk Storage

**Status:** ⏳ Pending

Chapters are divided into smaller chunks suitable for retrieval.

Each chunk should retain enough metadata to identify where it came from.

Possible metadata:

```text
book_id
chapter_id
chapter_number
chunk_id
chunk_number
text
position
```

### Expected Structure

```text
Book
 ├── Chapter 1
 │    ├── Chunk 1
 │    ├── Chunk 2
 │    └── Chunk 3
 │
 ├── Chapter 2
 │    ├── Chunk 1
 │    └── Chunk 2
 │
 └── Chapter 3
      ├── Chunk 1
      └── Chunk 2
```

### GitHub Issue

`Phase 3: Implement Chapter Chunking and Storage`

---

# 🔎 Phase 4 — Question Processing & Retrieval

**Status:** ⏳ Pending

When the reader asks a question, LitLens retrieves relevant information from the already processed book.

### Flow

```text
User Question
      ↓
Question Processing
      ↓
Current Reading Position
      ↓
Accessible Chapters
      ↓
Relevant Chunk Retrieval
      ↓
Ranked Results
```

The first retrieval implementation may use:

```text
TF-IDF
   +
Cosine Similarity
```

Later, semantic retrieval can be evaluated using embeddings.

### GitHub Issue

`Phase 4: Implement Question Retrieval`

---

# 🛡️ Phase 5 — Spoiler Protection

**Status:** ⏳ Pending

This is the core differentiating feature of LitLens.

If the reader has reached Chapter 8:

```text
Accessible:
Chapter 1 → Chapter 8

Restricted:
Chapter 9 → Final Chapter
```

The restriction must happen **before relevant context is passed to the answering system**.

### Example

```text
Current Chapter = 8

Question
   ↓
Retrieve only Chapters 1–8
   ↓
Generate answer
```

The system should not retrieve Chapter 15 and simply hide it afterward.

### GitHub Issue

`Phase 5: Implement Spoiler-Aware Retrieval`

---

# 💬 Phase 6 — Question Answering

**Status:** ⏳ Pending

After relevant chunks have been retrieved, LitLens produces an answer based on the permitted context.

### Expected Output

```text
Answer:
John left the house after his argument with Robert.

Sources:
Chapter 7
Chapter 8
```

The answer should remain grounded in the retrieved book content.

### GitHub Issue

`Phase 6: Implement Question Answering`

---

# 👤 Phase 7 — Character Intelligence

**Status:** ⏳ Pending

LitLens analyzes characters and other entities within the book.

Potential NLP techniques:

* Named Entity Recognition
* Entity normalization
* Mention counting
* First appearance detection
* Chapter-wise character tracking

Example:

```text
Mr. Darcy
Darcy
Mr Darcy
```

may need to be normalized as the same character.

### GitHub Issue

`Phase 7: Implement Character Extraction and Entity Analysis`

---

# 🕸️ Phase 8 — Character Relationships

**Status:** ⏳ Pending

LitLens can identify potential relationships between characters.

Initial approach:

```text
Character A
     ↕
Co-occurrence
     ↕
Character B
```

More advanced approaches may later attempt relationship classification.

Example:

```text
Harry ─── FRIEND ─── Ron
```

### GitHub Issue

`Phase 8: Implement Character Relationship Analysis`

---

# 📖 Phase 9 — Reading Interface

**Status:** ⏳ Pending

Create the reader interface and connect reading progress with the NLP system.

The system should know the reader's current position.

For example:

```text
Book: Example Book
Current Chapter: 8
Current Page: 142
```

This information controls what content is available to retrieval.

### GitHub Issue

`Phase 9: Implement Reader and Reading Progress`

---

# 📊 Phase 10 — Evaluation

**Status:** ⏳ Pending

Evaluate LitLens rather than only demonstrating that it works.

Potential evaluation areas:

### Retrieval

* Precision
* Recall
* Top-K retrieval accuracy

### Question Answering

* Answer correctness
* Context relevance
* Grounding

### Spoiler Protection

Test questions whose answers occur:

```text
Before current chapter
At current chapter
After current chapter
```

The system should demonstrate that future information is not used.

### Traditional vs Semantic Retrieval

Potential experiment:

```text
TF-IDF
   vs
Sentence Embeddings
```

### GitHub Issue

`Phase 10: Evaluate LitLens NLP Pipeline`

---

# 🚀 Phase 11 — Documentation & Deployment

**Status:** ⏳ Pending

Final project preparation.

### Goals

* Complete README
* Add architecture diagram
* Document NLP pipeline
* Document database design
* Add screenshots
* Add installation instructions
* Add usage instructions
* Document experiments
* Document limitations
* Deploy the application if feasible

### GitHub Issue

`Phase 11: Final Documentation and Deployment`

---

# 🧠 NLP Techniques

The project is designed to progressively explore NLP techniques.

### Traditional NLP

* Tokenization
* Sentence segmentation
* Stopword handling
* Stemming
* Lemmatization
* N-grams
* POS tagging

### Information Extraction

* Named Entity Recognition
* Entity normalization
* Coreference resolution
* Character extraction
* Relationship extraction

### Information Retrieval

* Bag of Words
* TF-IDF
* Cosine similarity
* Ranking

### Modern NLP

* Word embeddings
* Sentence embeddings
* Semantic similarity
* Retrieval-Augmented Generation concepts
* Question Answering

LLMs are considered an **optional later component**, not the foundation of LitLens.

---

# 🧱 Initial Technology Direction

| Component       | Technology              |
| --------------- | ----------------------- |
| Backend         | Python + Flask          |
| Frontend        | HTML + CSS + JavaScript |
| Templates       | Jinja                   |
| Database        | SQLite initially        |
| NLP             | NLTK / spaCy            |
| ML / Retrieval  | scikit-learn            |
| Data Processing | NumPy / pandas          |
| Semantic Search | sentence-transformers   |
| Vector Search   | FAISS                   |
| LLM             | Optional                |

The technology stack may change if experimentation reveals a better technical approach.

---

# 🎯 Core Product Principle

LitLens is not intended to be a generic chatbot.

Its purpose is to provide **context-aware assistance while preserving the reader's experience**.

```text
                    LITLENS

                    📖 Read
                      ↓
                  🤔 Confused?
                      ↓
                  💬 Ask
                      ↓
             🔎 Find relevant context
                      ↓
             🛡️ Apply spoiler filter
                      ↓
                 💡 Answer
                      ↓
               📚 Continue reading
```

---

# 📈 Development Philosophy

LitLens will be developed incrementally.

The project aims to understand the underlying NLP concepts rather than simply connecting an LLM API.

The intended progression is:

```text
Traditional NLP
      ↓
Information Extraction
      ↓
Traditional Information Retrieval
      ↓
Semantic NLP
      ↓
Spoiler-Aware Retrieval
      ↓
Question Answering
      ↓
Optional LLM Integration
```

Each major development phase will be tracked using a GitHub Issue.

---

# 🗂️ GitHub Development Tracking

Each phase will have its own GitHub Issue.

Example:

```text
Phase 1
└── Issue #1 — Book Upload

Phase 2
└── Issue #2 — Book Processing

Phase 3
└── Issue #3 — Chunk Storage

Phase 4
└── Issue #4 — Question Retrieval

...
```

The README status will be updated as development progresses:

```text
⏳ Pending
🔵 In Progress
✅ Done
⚠️ Blocked
```

The architecture will be finalized before implementation begins, and individual issues will be created when each phase is started.
