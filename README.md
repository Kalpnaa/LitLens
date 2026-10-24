# 📚 LitLens — NLP-Based Spoiler-Aware Reading Companion

LitLens is an NLP-powered reading companion designed to help readers understand books without exposing information they have not yet read.

The core idea is simple:

> **Read → Get confused → Ask LitLens → Understand without spoilers → Continue reading.**

---

## 🚧 Project Status

**Overall Status:** 🟡 In Development

| Phase | Description | Status |
|---|---|---|
| Phase 1 | 📖 Book Upload | ✅ Done |
| Phase 2 | ⚙️ Book Processing | ✅ Done |
| Phase 3 | 🧩 Chunk Creation and Storage | ✅ Done |
| Phase 4 | 🔎 Question Processing and Retrieval | ✅ Done |
| Phase 5 | 🛡️ Spoiler-Aware Retrieval | ✅ Done |
| Phase 6 | 💬 Question Answering and Local LLM Integration | ✅ Done |
| Phase 7 | 👤 Character Intelligence | ✅ Done |
| Phase 8 | 🕸️ Character Relationship Analysis | ⏳ Pending |
| Phase 9 | 📖 Reading Interface and Progress Tracking | ⏳ Pending |
| Phase 10 | 📊 Evaluation | ⏳ Pending |
| Phase 11 | 🚀 Documentation and Deployment | ⏳ Pending |

> The architecture and phases may evolve as implementation and experimentation reveal better approaches.

---

## 🏗️ Development Pipeline

The current LitLens pipeline is:

```text
Book Upload
     ↓
Book Processing
     ↓
Text Extraction
     ↓
Chapter Detection
     ↓
Text Chunking
     ↓
Chunk Storage in SQLite
     ↓
User Question
     ↓
Current Reading Position
     ↓
Spoiler-Aware Chapter Filtering
     ↓
TF-IDF Retrieval + Cosine Similarity
     ↓
Relevant Book Context
     ↓
Local LLM Answer Generation
     ↓
Answer + Source Passages
```

LitLens follows the principle:

> **Process once, retrieve many times.**

Uploaded books are processed and stored so that subsequent questions can use the saved chapters and chunks without processing the entire book again.

---

## 📌 Phase 1 — Book Upload

**Status: ✅ Done**

Implemented book uploading through the Flask application.

### Features

- Accepts PDF and TXT files.
- Validates file extensions and uploaded filenames.
- Generates unique stored filenames.
- Saves uploaded books to the application's upload directory.
- Registers book metadata in SQLite.
- Handles invalid uploads and file/database errors.

### Flow

```text
User Uploads Book
        ↓
Validate File
        ↓
Generate Unique Filename
        ↓
Save Original File
        ↓
Create SQLite Book Record
```

**GitHub Issue:** Book Upload

---

## ⚙️ Phase 2 — Book Processing

**Status: ✅ Done**

Implemented the book-processing pipeline to convert uploaded files into structured textual content.

### Features

- Extracts text using the text extraction module.
- Detects chapters or sections.
- Preserves chapter numbers, titles, and heading types.
- Prepares chapter content for chunking.
- Updates processing status in the database.
- Handles missing files and unreadable content.

### Flow

```text
Uploaded Book
     ↓
Text Extraction
     ↓
Chapter Detection
     ↓
Structured Chapter Data
     ↓
Chunk Preparation
```

The processing pipeline prepares content before replacing existing chapter and chunk records, using database transactions to maintain consistency.

---

## 🧩 Phase 3 — Chunk Creation and Storage

**Status: ✅ Done**

Implemented text chunking to make book content suitable for information retrieval.

### Features

- Divides chapter text into smaller chunks.
- Uses a configurable maximum word count.
- Supports sentence overlap to preserve context between adjacent chunks.
- Stores chunks in SQLite with associated book and chapter identifiers.
- Saves chunk numbers and word counts.

### Database Structure

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

### Stored Metadata

- `book_id`
- `chapter_id`
- `chapter_number`
- `chunk_number`
- `text`
- `word_count`

---

## 🔎 Phase 4 — Question Processing and Retrieval

**Status: ✅ Done**

Implemented the initial retrieval system using traditional information retrieval techniques.

### Techniques

- Question normalization
- TF-IDF vectorization
- Cosine similarity
- Relevance scoring
- Top-K chunk retrieval

### Retrieval Flow

```text
User Question
      ↓
Question Normalization
      ↓
Retrieve Accessible Book Chunks
      ↓
TF-IDF Vectorization
      ↓
Cosine Similarity
      ↓
Rank Relevant Chunks
      ↓
Return Top-K Results
```

The current implementation retrieves up to five relevant chunks for ordinary questions, excluding chunks from chapters beyond the reader's selected chapter.

Semantic retrieval using sentence embeddings may be explored in a future improvement.

---

## 🛡️ Phase 5 — Spoiler-Aware Retrieval

**Status: ✅ Done**

Implemented chapter-based access filtering before relevant context is sent to the answer-generation model.

### Example

If the reader has completed Chapter 8:

```text
Accessible:
Chapter 1 → Chapter 8

Restricted:
Chapter 9 → Final Chapter
```

### Implementation

- Accepts the reader's current chapter.
- Filters database retrieval using the chapter number.
- Ranks only eligible chunks.
- Passes retrieved context to the answer-generation component.

**Core principle:** Future chapters must be excluded during retrieval, not retrieved and hidden afterward.

---

## 💬 Phase 6 — Question Answering and Local LLM Integration

**Status: ✅ Done**

Integrated retrieval with a locally running language model to generate answers grounded in the permitted book context.

### Technology

- Ollama
- Qwen 2.5 3B
- Python `ollama` package

### Features

- Generates answers from retrieved book passages.
- Uses a system prompt designed for spoiler-aware responses.
- Avoids relying on outside knowledge when answering book questions.
- Returns an insufficient-context response when the retrieved text cannot support an answer.
- Displays the answer and relevant source passages in the Flask interface.
- Detects requests for summaries of the story so far.
- Retrieves all chunks up to the selected chapter for summary requests.

### Answer Generation Flow

```text
User Question
      ↓
Retrieve Permitted Context
      ↓
Build Context Prompt
      ↓
Ollama — Qwen 2.5 3B
      ↓
Generate Answer
      ↓
Display Answer + Source Passages
```

### Ollama Setup

Download Ollama for Windows from:

https://ollama.com/download/windows

Download the model:

```bash
ollama pull qwen2.5:3b
```

Run and initialize the model:

```bash
ollama run qwen2.5:3b
```

Install the Python integration:

```bash
python -m pip install ollama
```

### Summary Generation

LitLens identifies summary requests separately from ordinary questions and retrieves the complete eligible chapter content.

Summary generation is being optimized to reduce latency for longer contexts while preserving important story events and spoiler protection.

---

# 🔜 Upcoming Development Phases

## 👤 Phase 7 — Character Intelligence

**Status: ⏳ Pending**

**GitHub Issue #8**

Develop character extraction and analysis capabilities.

### Goals

- Identify character names and other relevant entities.
- Detect character mentions across chapters.
- Normalize name variations where possible.
- Track the first appearance of a character.
- Build chapter-wise character information.

### Example

```text
Mr. Darcy
Darcy
Mr Darcy
     ↓
Potentially the Same Character
```

### Potential Techniques

- Named Entity Recognition (NER)
- Entity normalization
- Mention counting
- Chapter-wise entity tracking

Character information must also respect the reader's current chapter to prevent spoilers.

---

## 🕸️ Phase 8 — Character Relationship Analysis

**Status: ⏳ Pending**

**GitHub Issue #9**

Identify and represent relationships between characters.

### Initial Approach

```text
Character A
     ↕
Co-occurrence and Context
     ↕
Character B
```

### Goals

- Identify characters appearing in related contexts.
- Analyze surrounding sentences for relationship clues.
- Explore relationship classification.
- Represent relationships in a structured format.
- Ensure future-chapter relationships remain inaccessible.

### Example

```text
Harry ─── FRIEND ─── Ron
```

Co-occurrence alone does not establish a real relationship; contextual evidence will be needed to improve accuracy.

---

## 📖 Phase 9 — Reading Interface and Progress Tracking

**Status: ⏳ Pending**

**GitHub Issue #10**

Develop a more complete reading experience and connect reading progress with LitLens's NLP pipeline.

### Goals

- Improve the book-reading interface.
- Track the reader's current chapter.
- Explore page-level reading progress where reliable page information is available.
- Allow readers to ask questions while reading.
- Provide access to character information and relationships.
- Keep all generated answers restricted to the permitted reading position.

### Example

```text
Book: Example Book
Current Chapter: 8
Current Page: 142
        ↓
Spoiler-Aware Context
        ↓
Question Answering
```

The current implementation lets the reader select the highest chapter they have read. Persistent reading-progress tracking will be developed in this phase.

---

## 📊 Phase 10 — Evaluation

**Status: ⏳ Pending**

**GitHub Issue #11**

Evaluate LitLens systematically rather than relying only on manual demonstrations.

### Retrieval Evaluation

- Precision@K
- Recall@K
- Top-K retrieval accuracy
- Relevance of retrieved passages

### Question-Answering Evaluation

- Answer correctness
- Context relevance
- Faithfulness to the book
- Handling of insufficient context

### Spoiler-Protection Evaluation

Test questions whose answers occur:

```text
Before the Current Chapter
At the Current Chapter
After the Current Chapter
```

The system should not use future-chapter content to answer questions about the story.

### Performance Evaluation

- Retrieval latency
- LLM generation latency
- Summary generation time
- Performance across different book lengths

### Potential Experiment

```text
TF-IDF Retrieval
       vs
Sentence-Embedding Retrieval
```

Evaluation results will help determine which improvements provide meaningful benefits.

---

## 🚀 Phase 11 — Documentation and Deployment

**Status: ⏳ Pending**

Complete the project documentation and prepare LitLens for demonstration or deployment.

### Goals

- Finalize the README.
- Document the architecture and processing pipeline.
- Document the database schema.
- Add screenshots and usage examples.
- Include installation and setup instructions.
- Record evaluation results and limitations.
- Explore deployment options.
- Document local LLM setup and resource requirements.

**GitHub Issue:** Documentation and Deployment

---

# 🧠 NLP Techniques

LitLens is designed to explore NLP techniques progressively.

### Traditional NLP

- Text normalization
- Tokenization
- Sentence segmentation
- Stopword handling
- Stemming and lemmatization
- N-grams
- Part-of-speech tagging

### Information Extraction

- Named Entity Recognition
- Entity normalization
- Coreference resolution
- Character extraction
- Relationship extraction

### Information Retrieval

- Bag of Words
- TF-IDF
- Cosine similarity
- Relevance ranking
- Top-K retrieval

### Modern NLP

- Word embeddings
- Sentence embeddings
- Semantic similarity
- Retrieval-Augmented Generation concepts
- Context-grounded question answering
- Local LLM integration

Not every technique listed above has been implemented. Advanced methods will be evaluated and added where they provide value.

---

# 🧱 Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Templates | Jinja |
| Database | SQLite |
| Retrieval | scikit-learn |
| Ranking | TF-IDF, cosine similarity |
| Book Processing | Python text extraction and chunking modules |
| LLM Runtime | Ollama |
| Language Model | Qwen 2.5 3B |
| LLM Integration | Python `ollama` package |

### Potential Future Technologies

| Component | Candidate Technology |
|---|---|
| Advanced NLP | NLTK, spaCy |
| Semantic Retrieval | sentence-transformers |
| Vector Search | FAISS |
| Evaluation | Custom retrieval and QA test datasets |

These are potential extensions, not claims that every listed technology is already integrated.

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
             🔎 Retrieve Context
                      ↓
             🛡️ Filter Spoilers
                      ↓
                🧠 Generate
                      ↓
                💡 Understand
                      ↓
              📚 Continue Reading
```

---

# 📈 Development Philosophy

LitLens is developed incrementally, with each major phase tracked through GitHub Issues.

The project emphasizes understanding the underlying NLP and retrieval concepts instead of simply connecting a language model to a prompt.

The development progression is:

```text
Book Processing
      ↓
Traditional NLP
      ↓
Information Retrieval
      ↓
Spoiler-Aware Retrieval
      ↓
Question Answering
      ↓
Character Intelligence
      ↓
Relationship Analysis
      ↓
Reading Experience
      ↓
Evaluation
      ↓
Documentation and Deployment
```

The architecture can evolve as experimentation reveals better approaches.

---

**Current milestone:** The initial book-processing, retrieval, spoiler-filtering, and question-answering pipeline is implemented. The next phase focuses on extracting character information from book content.