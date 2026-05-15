# Product Requirements Document (PRD)
# AI Chatbot Microservice API untuk Tanya Jawab Berbasis Dokumen dan Pencarian

**Versi:** 1.1  
**Status:** Draft siap pengembangan, revisi storage lokal  
**Tanggal:** 15 Mei 2026  
**Produk:** AI Chatbot Microservice API  
**Fokus:** REST API mandiri untuk chatbot AI, pencarian semantik, dan tanya jawab berbasis dokumen  
**Target integrasi:** Semua aplikasi client melalui REST API, API key, dan tenant isolation  

---

## 0. Catatan Revisi v1.1

Revisi ini menetapkan **Local File Storage** sebagai storage utama. Semua spesifikasi terkait storage cloud, object storage eksternal, dan service storage tambahan dihapus dari kebutuhan utama. File dokumen disimpan pada direktori atau persistent volume server yang sama dengan AI Microservice.

Keputusan ini membuat MVP lebih sederhana, tidak membutuhkan biaya storage provider, dan lebih mudah dijalankan di lokal atau satu server. Batas storage mengikuti kapasitas disk server, sehingga sistem wajib memiliki validasi ukuran file, struktur folder per tenant, cleanup file sementara, dan backup berkala.

---

## 1. Ringkasan Produk

AI Chatbot Microservice API adalah layanan backend mandiri berbasis Python yang menyediakan kemampuan chatbot AI untuk menjawab pertanyaan umum, melakukan pencarian semantik, dan menjawab pertanyaan berdasarkan dokumen yang diberikan oleh aplikasi client.

Layanan ini dirancang sebagai microservice agar tidak terikat pada satu aplikasi tertentu. Aplikasi apa pun dapat mengirim dokumen, metadata, scope akses, dan prompt ke service ini. Service akan memproses dokumen, membuat embedding, menyimpan vector, mengambil konteks yang relevan, memanggil model AI, lalu mengembalikan jawaban beserta sumbernya.

Microservice ini tidak memberikan akses database langsung kepada model AI. Model hanya menerima konteks final yang sudah dipilih oleh sistem melalui proses retrieval. Dengan desain ini, sistem lebih aman, modular, dan dapat digunakan ulang oleh banyak project.

---

## 2. Tujuan Produk

Tujuan utama produk ini adalah membangun AI API mandiri yang mampu:

1. Menerima dokumen dari aplikasi client.
2. Mengekstrak isi dokumen PDF, Word, Excel, CSV, TXT, dan format teks lain.
3. Memecah dokumen menjadi chunk yang siap dicari.
4. Membuat embedding untuk setiap chunk.
5. Menyimpan metadata dokumen di database relasional.
6. Menyimpan embedding di vector database.
7. Menjawab pertanyaan pengguna dengan metode Retrieval-Augmented Generation atau RAG.
8. Mengembalikan jawaban disertai sumber dokumen.
9. Mendukung multi-tenant agar dapat digunakan oleh banyak aplikasi.
10. Menyediakan API key dan quota usage untuk kontrol akses.
11. Menyediakan log pemakaian model, token, dokumen, dan chat.
12. Menyediakan struktur yang siap dikembangkan ke production.

---

## 3. Masalah yang Diselesaikan

Banyak aplikasi membutuhkan chatbot AI, tetapi sering mencampur logika aplikasi utama dengan logika AI. Akibatnya, sistem sulit dikembangkan, sulit dipakai ulang, dan rawan masalah keamanan.

Masalah utama yang diselesaikan microservice ini:

1. Aplikasi client tidak perlu membangun sistem AI dari nol.
2. Model AI tidak perlu dan tidak boleh mengakses database aplikasi.
3. Dokumen besar tidak dikirim penuh ke model.
4. Jawaban dari file dapat dikontrol melalui retrieval.
5. Setiap aplikasi client dapat memiliki tenant, collection, dan quota sendiri.
6. Riwayat chat dan usage AI tercatat secara terpisah.
7. Service dapat digunakan ulang untuk project berbeda.

---

## 4. Prinsip Desain Produk

Microservice ini mengikuti prinsip berikut:

1. **Mandiri**  
   Service berdiri sendiri dan tidak bergantung pada struktur database aplikasi client.

2. **Reusable**  
   Satu service dapat dipakai oleh banyak aplikasi.

3. **Secure by Design**  
   Akses dilakukan melalui API key, tenant isolation, rate limit, dan metadata filter.

4. **RAG First**  
   Jawaban berbasis dokumen harus menggunakan retrieval, bukan menempelkan seluruh dokumen ke prompt.

5. **Model Agnostic**  
   Service dapat memakai banyak model melalui OpenRouter atau provider lain.

6. **Database Separation**  
   Service memiliki database sendiri untuk metadata AI, chat, dokumen, job, dan usage.

7. **Vector Search Separation**  
   Embedding disimpan di vector database khusus, bukan di database aplikasi client.

8. **No Direct DB Access by LLM**  
   Model AI tidak boleh melakukan query langsung ke database.

9. **Observable**  
   Semua proses penting dicatat melalui log, metrics, job status, dan usage log.

10. **Scalable**  
   Proses berat seperti parsing dokumen dan embedding dijalankan melalui background worker.

---

## 5. Target Pengguna

### 5.1 Developer Aplikasi Client

Developer memakai API ini untuk menambahkan fitur AI pada aplikasi mereka.

Kebutuhan utama:

- upload dokumen
- indexing dokumen
- chat berbasis dokumen
- search dokumen
- mendapatkan sumber jawaban
- mengontrol akses berdasarkan metadata
- melihat usage API

### 5.2 Admin AI Service

Admin mengelola service secara teknis.

Kebutuhan utama:

- membuat tenant
- membuat API key
- mengatur quota
- memilih model default
- memantau usage
- melihat job gagal
- mengatur collection
- melakukan re-index dokumen

### 5.3 End User

End user memakai chatbot melalui aplikasi client.

Kebutuhan utama:

- bertanya dengan bahasa natural
- mendapat jawaban ringkas dan jelas
- mendapat jawaban berdasarkan dokumen yang sesuai
- melihat sumber jawaban
- mendapat respons cepat

---

## 6. Ruang Lingkup Produk

### 6.1 In-Scope MVP

Fitur yang wajib masuk MVP:

1. REST API berbasis Python FastAPI.
2. Multi-tenant sederhana.
3. API key authentication.
4. Upload dokumen.
5. Parsing dokumen PDF, DOCX, XLSX, CSV, dan TXT.
6. Chunking dokumen.
7. Embedding dokumen.
8. Penyimpanan metadata di MySQL.
9. Penyimpanan vector di Qdrant.
10. Chat endpoint berbasis RAG.
11. Search endpoint berbasis semantic search.
12. Sumber jawaban atau citation.
13. Riwayat chat.
14. Usage log.
15. Background job untuk indexing dokumen.
16. Health check.
17. Dokumentasi OpenAPI atau Swagger.

### 6.2 In-Scope Versi 1

Fitur setelah MVP stabil:

1. Streaming response.
2. Model routing.
3. Reranking hasil retrieval.
4. Hybrid search: keyword search + vector search.
5. Document versioning.
6. Feedback jawaban.
7. Rate limit per API key.
8. Quota bulanan.
9. Webhook untuk status indexing.
10. Admin API untuk tenant dan API key.
11. Export usage log.
12. Re-index collection.
13. Delete dokumen beserta vector.
14. Support local file path dan local file serving internal.
15. Support OCR opsional.

### 6.3 In-Scope Versi 2

Fitur lanjutan:

1. Multi-modal input.
2. OCR untuk scan PDF dan gambar.
3. Knowledge graph ringan.
4. Agentic workflow terbatas.
5. Tool calling internal yang tetap dikontrol sistem.
6. Evaluation dashboard.
7. A/B testing model.
8. Fine-tuned prompt template per tenant.
9. Guardrail lanjutan.
10. Enterprise audit log.
11. Deployment Kubernetes.
12. High availability setup.

### 6.4 Out-of-Scope MVP

Fitur berikut tidak wajib untuk MVP:

1. UI dashboard admin.
2. Fine-tuning model.
3. Training model sendiri.
4. Direct database query oleh model.
5. OCR kompleks.
6. Real-time collaboration.
7. Integrasi billing payment.
8. Speech to text.
9. Text to speech.
10. Image generation.

---

## 7. Spesifikasi Teknologi

### 7.1 Bahasa dan Framework

| Komponen | Teknologi |
|---|---|
| Bahasa utama | Python 3.12 |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Production server | Gunicorn + Uvicorn Worker |
| API schema | OpenAPI 3 |
| Validation | Pydantic v2 |
| HTTP client | httpx |
| ORM | SQLAlchemy 2.x |
| Migration | Alembic |

### 7.2 Database dan Storage

| Kebutuhan | Teknologi |
|---|---|
| Metadata AI | MySQL 8.4 LTS |
| Vector database | Qdrant |
| Queue broker | Redis |
| Background worker | Celery |
| Storage file utama | Local File Storage |
| Lokasi storage | Persistent volume atau direktori server |
| Cache ringan | Redis |
| File sementara | Local temp storage dengan cleanup otomatis |

#### Keputusan Storage Final

Storage utama microservice ditetapkan menggunakan **Local File Storage**. Sistem tidak memakai storage cloud atau object storage eksternal pada spesifikasi utama. Keputusan ini dipilih untuk menjaga pengembangan tetap sederhana, tanpa biaya tambahan, tanpa konfigurasi cloud, dan tanpa risiko tagihan provider.

Local File Storage tetap memiliki batas fisik sesuai kapasitas disk server. Karena itu, sistem wajib menyediakan validasi ukuran file, struktur folder per tenant, cleanup file sementara, serta prosedur backup manual atau terjadwal.

Struktur storage default:

```text
storage/
  tenants/
    {tenant_uuid}/
      documents/
        original/
        extracted/
        chunks/
      temp/
      logs/
```

Konfigurasi `.env` default:

```env
STORAGE_DRIVER=local
LOCAL_STORAGE_PATH=/app/storage
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,xlsx,csv,txt,md,html
KEEP_ORIGINAL_FILE=true
KEEP_EXTRACTED_TEXT=true
TEMP_FILE_TTL_HOURS=24
```

### 7.3 AI dan RAG

| Kebutuhan | Teknologi |
|---|---|
| LLM provider utama | OpenRouter |
| Mode model | Chat completion |
| Embedding provider | Pluggable provider |
| Default embedding lokal | BGE-M3 atau sentence-transformers compatible model |
| Default embedding API | OpenAI text-embedding-3-small atau provider setara |
| Retrieval | Qdrant vector search |
| Metadata filter | Qdrant payload filter |
| Reranking | Optional cross-encoder reranker |
| Prompt template | YAML atau database-driven prompt template |
| Token estimation | tiktoken atau tokenizer provider |

### 7.4 Document Processing

| Format | Library |
|---|---|
| PDF native text | PyMuPDF |
| PDF table fallback | pdfplumber |
| DOCX | python-docx |
| XLSX | openpyxl + pandas |
| CSV | pandas |
| TXT | native Python |
| HTML | BeautifulSoup |
| Markdown | markdown parser |
| OCR opsional | Tesseract atau PaddleOCR |

### 7.5 Observability dan Security

| Kebutuhan | Teknologi |
|---|---|
| Logging | structlog atau loguru |
| Metrics | Prometheus |
| Error tracking | Sentry opsional |
| Tracing | OpenTelemetry opsional |
| API authentication | API key hashed |
| Rate limit | Redis-based limiter |
| Secret management | Environment variables atau Vault |
| Containerization | Docker |
| Deployment | Docker Compose untuk MVP, Kubernetes untuk production lanjutan |

---

## 8. Arsitektur Sistem

### 8.1 Diagram Konseptual

```mermaid
flowchart TD
    A[Client Application] --> B[AI Microservice API]
    B --> C[Auth and Tenant Guard]
    C --> D[Document API]
    C --> E[Chat API]
    C --> F[Search API]

    D --> G[Document Parser]
    G --> H[Chunker]
    H --> I[Embedding Service]
    I --> J[Qdrant Vector Database]
    D --> K[MySQL Metadata Database]
    D --> L[Local File Storage]

    E --> M[Context Retriever]
    M --> J
    M --> K
    M --> N[Prompt Builder]
    N --> O[LLM Provider via OpenRouter]
    O --> P[Response Formatter]
    P --> Q[Usage Logger]
    Q --> K
    P --> A

    D --> R[Redis Queue]
    R --> S[Celery Worker]
    S --> G
```

### 8.2 Penjelasan Arsitektur

1. Client application memanggil AI Microservice melalui REST API.
2. Semua request melewati API key authentication dan tenant validation.
3. Dokumen yang masuk disimpan sebagai metadata di MySQL.
4. File asli disimpan di Local File Storage pada persistent volume server.
5. Job indexing dikirim ke queue.
6. Worker memproses file secara asynchronous.
7. Worker mengekstrak teks, melakukan chunking, membuat embedding, dan menyimpan vector ke Qdrant.
8. Ketika chat berjalan, service mencari chunk paling relevan berdasarkan query dan scope metadata.
9. Prompt builder menyusun system prompt, context, dan user message.
10. LLM menjawab berdasarkan konteks yang diberikan.
11. Service mengembalikan jawaban, sumber, dan metadata usage ke client.

---

## 9. Modul Utama

### 9.1 API Gateway Layer

Bertugas menerima semua request dari client.

Fungsi:

- validasi API key
- validasi tenant
- validasi request body
- rate limit
- routing ke service internal
- response formatting
- error handling

### 9.2 Tenant Management

Bertugas memisahkan data antar client.

Fungsi:

- membuat tenant
- mengatur status tenant
- menyimpan limit tenant
- menyimpan konfigurasi default tenant
- memisahkan collection per tenant

### 9.3 API Key Management

Bertugas mengatur akses client.

Fungsi:

- membuat API key
- menyimpan hash API key
- revoke API key
- membatasi scope API key
- mencatat penggunaan API key
- mengatur quota

### 9.4 Document Ingestion Service

Bertugas menerima dan mendaftarkan dokumen.

Fungsi:

- upload file
- upload by URL
- validasi format file
- validasi ukuran file
- simpan file
- buat document record
- kirim indexing job
- update status dokumen

### 9.5 Document Parser

Bertugas mengekstrak teks dari file.

Fungsi:

- baca PDF
- baca DOCX
- baca XLSX
- baca CSV
- baca TXT
- ekstrak halaman
- ekstrak tabel sederhana
- normalisasi whitespace
- hapus karakter rusak
- simpan hasil ekstraksi mentah jika diperlukan

### 9.6 Chunking Service

Bertugas memecah teks menjadi potongan kecil.

Fungsi:

- recursive text splitting
- heading-aware splitting
- page-aware splitting
- overlap antar chunk
- token counting
- simpan chunk metadata
- menjaga nomor halaman

Rekomendasi awal:

```text
chunk_size: 800 sampai 1200 token
chunk_overlap: 100 sampai 200 token
top_k: 5 sampai 8 chunk
max_context_tokens: 6000 sampai 12000 token, tergantung model
```

### 9.7 Embedding Service

Bertugas mengubah chunk menjadi vector.

Fungsi:

- memilih provider embedding
- batch embedding
- retry jika gagal
- menyimpan vector ID
- menyimpan dimensi vector
- logging biaya embedding
- mendukung re-embedding

### 9.8 Vector Store Service

Bertugas menyimpan dan mencari vector.

Fungsi:

- create collection
- upsert vector
- delete vector
- search vector
- metadata filtering
- payload indexing
- collection isolation
- tenant isolation

### 9.9 Retrieval Service

Bertugas memilih konteks yang akan diberikan ke model.

Fungsi:

- menerima user query
- membuat query embedding
- mencari chunk relevan
- memfilter tenant, collection, document, dan scope
- melakukan reranking opsional
- membuang chunk duplikat
- menyusun daftar sumber
- membatasi total token konteks

### 9.10 Prompt Builder

Bertugas menyusun prompt final.

Fungsi:

- memasukkan system instruction
- memasukkan konteks dari retrieval
- memasukkan aturan jawaban
- memasukkan riwayat chat terpilih
- memasukkan pesan user
- membatasi token
- mengatur format jawaban

### 9.11 LLM Provider Adapter

Bertugas memanggil model AI.

Fungsi:

- OpenRouter chat completion
- model selection
- fallback model
- retry
- timeout
- streaming response
- usage extraction
- error normalization

### 9.12 Chat Session Service

Bertugas menyimpan sesi percakapan.

Fungsi:

- membuat session
- menyimpan user message
- menyimpan assistant response
- menyimpan sources
- menyimpan model usage
- mengambil riwayat terbatas
- menghapus session

### 9.13 Search Service

Bertugas menyediakan pencarian semantik tanpa chat.

Fungsi:

- semantic search
- keyword search opsional
- hybrid search opsional
- filter by tenant, collection, document, metadata
- return snippet
- return score

### 9.14 Usage and Billing Log

Bertugas mencatat penggunaan.

Fungsi:

- jumlah request
- token input
- token output
- total token
- model yang dipakai
- embedding usage
- retrieval usage
- error count
- estimated cost
- quota remaining

### 9.15 Feedback Service

Bertugas menyimpan evaluasi jawaban.

Fungsi:

- like atau dislike
- rating 1 sampai 5
- alasan feedback
- label jawaban salah
- label sumber tidak sesuai
- data untuk evaluasi prompt

---

## 10. Alur Kerja Utama

### 10.1 Flow Indexing Dokumen

```mermaid
sequenceDiagram
    participant C as Client Application
    participant API as AI Microservice API
    participant DB as MySQL
    participant OS as Local File Storage
    participant Q as Redis Queue
    participant W as Celery Worker
    participant V as Qdrant

    C->>API: POST /v1/documents
    API->>API: Validate API Key and Tenant
    API->>OS: Store File in Local Storage
    API->>DB: Create Document Record
    API->>Q: Enqueue Indexing Job
    API-->>C: Return document_id and job_id
    W->>Q: Consume Job
    W->>OS: Read Local File
    W->>W: Parse Text
    W->>W: Chunk Text
    W->>W: Generate Embeddings
    W->>V: Upsert Vectors
    W->>DB: Save Chunks and Update Status
```

### 10.2 Flow Chat Berbasis Dokumen

```mermaid
sequenceDiagram
    participant C as Client Application
    participant API as AI Microservice API
    participant DB as MySQL
    participant V as Qdrant
    participant LLM as OpenRouter LLM

    C->>API: POST /v1/chat
    API->>API: Validate API Key, Tenant, Scope
    API->>DB: Load Session and Config
    API->>V: Search Relevant Chunks
    API->>DB: Load Chunk Metadata
    API->>API: Build Prompt
    API->>LLM: Send Chat Completion Request
    LLM-->>API: Return Answer
    API->>DB: Store Message, Sources, Usage
    API-->>C: Return Answer and Sources
```

### 10.3 Flow Search Dokumen

```mermaid
sequenceDiagram
    participant C as Client Application
    participant API as AI Microservice API
    participant V as Qdrant
    participant DB as MySQL

    C->>API: POST /v1/search
    API->>API: Validate API Key and Tenant
    API->>API: Generate Query Embedding
    API->>V: Vector Search with Metadata Filter
    API->>DB: Load Document and Chunk Metadata
    API-->>C: Return Search Results
```

---

## 11. Data Model MySQL

### 11.1 `tenants`

Menyimpan data organisasi atau aplikasi client.

```sql
CREATE TABLE tenants (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    tenant_uuid CHAR(36) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    status ENUM('active', 'inactive', 'suspended') NOT NULL DEFAULT 'active',
    default_model VARCHAR(150) NULL,
    default_embedding_model VARCHAR(150) NULL,
    monthly_quota_tokens BIGINT NULL,
    monthly_quota_requests BIGINT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);
```

### 11.2 `api_clients`

Menyimpan aplikasi client yang memakai service.

```sql
CREATE TABLE api_clients (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    client_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_api_clients_tenant (tenant_uuid)
);
```

### 11.3 `api_keys`

Menyimpan API key dalam bentuk hash.

```sql
CREATE TABLE api_keys (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    key_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    client_uuid CHAR(36) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(150) NOT NULL,
    scopes JSON NULL,
    last_used_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    status ENUM('active', 'revoked') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_api_keys_tenant_client (tenant_uuid, client_uuid)
);
```

### 11.4 `collections`

Menyimpan kelompok knowledge base.

```sql
CREATE TABLE collections (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    collection_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    vector_collection_name VARCHAR(200) NOT NULL,
    metadata_schema JSON NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_collections_tenant (tenant_uuid)
);
```

### 11.5 `documents`

Menyimpan metadata dokumen.

```sql
CREATE TABLE documents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    document_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    collection_uuid CHAR(36) NOT NULL,
    external_document_id VARCHAR(150) NULL,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NULL,
    file_type VARCHAR(50) NULL,
    mime_type VARCHAR(100) NULL,
    file_size_bytes BIGINT NULL,
    storage_path TEXT NULL,
    source_url TEXT NULL,
    metadata JSON NULL,
    status ENUM('uploaded', 'processing', 'indexed', 'failed', 'deleted') NOT NULL DEFAULT 'uploaded',
    total_pages INT NULL,
    total_chunks INT NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_documents_tenant_collection (tenant_uuid, collection_uuid),
    INDEX idx_documents_external (external_document_id)
);
```

### 11.6 `document_versions`

Menyimpan versi dokumen.

```sql
CREATE TABLE document_versions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    version_uuid CHAR(36) NOT NULL UNIQUE,
    document_uuid CHAR(36) NOT NULL,
    version_number INT NOT NULL,
    storage_path TEXT NULL,
    status ENUM('processing', 'indexed', 'failed') NOT NULL DEFAULT 'processing',
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_document_versions_doc (document_uuid)
);
```

### 11.7 `document_chunks`

Menyimpan metadata chunk dan teks chunk.

```sql
CREATE TABLE document_chunks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    chunk_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    collection_uuid CHAR(36) NOT NULL,
    document_uuid CHAR(36) NOT NULL,
    version_uuid CHAR(36) NULL,
    chunk_index INT NOT NULL,
    page_number INT NULL,
    heading VARCHAR(255) NULL,
    content MEDIUMTEXT NOT NULL,
    token_count INT NULL,
    vector_id VARCHAR(150) NOT NULL,
    metadata JSON NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_chunks_doc (document_uuid),
    INDEX idx_chunks_tenant_collection (tenant_uuid, collection_uuid)
);
```

### 11.8 `indexing_jobs`

Menyimpan status job indexing.

```sql
CREATE TABLE indexing_jobs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    job_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    document_uuid CHAR(36) NOT NULL,
    status ENUM('queued', 'running', 'success', 'failed', 'cancelled') NOT NULL DEFAULT 'queued',
    progress INT NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_jobs_tenant_status (tenant_uuid, status)
);
```

### 11.9 `chat_sessions`

Menyimpan sesi chat.

```sql
CREATE TABLE chat_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    external_user_id VARCHAR(150) NULL,
    collection_uuid CHAR(36) NULL,
    title VARCHAR(255) NULL,
    metadata JSON NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    INDEX idx_chat_sessions_tenant_user (tenant_uuid, external_user_id)
);
```

### 11.10 `chat_messages`

Menyimpan pesan chat.

```sql
CREATE TABLE chat_messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    message_uuid CHAR(36) NOT NULL UNIQUE,
    session_uuid CHAR(36) NOT NULL,
    tenant_uuid CHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content LONGTEXT NOT NULL,
    sources JSON NULL,
    model VARCHAR(150) NULL,
    prompt_tokens INT NULL,
    completion_tokens INT NULL,
    total_tokens INT NULL,
    latency_ms INT NULL,
    created_at TIMESTAMP NULL,
    INDEX idx_messages_session (session_uuid),
    INDEX idx_messages_tenant (tenant_uuid)
);
```

### 11.11 `retrieval_logs`

Menyimpan log retrieval.

```sql
CREATE TABLE retrieval_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    retrieval_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    session_uuid CHAR(36) NULL,
    query TEXT NOT NULL,
    filters JSON NULL,
    retrieved_chunks JSON NULL,
    top_k INT NULL,
    latency_ms INT NULL,
    created_at TIMESTAMP NULL,
    INDEX idx_retrieval_tenant (tenant_uuid)
);
```

### 11.12 `usage_logs`

Menyimpan log penggunaan AI.

```sql
CREATE TABLE usage_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    usage_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    client_uuid CHAR(36) NULL,
    api_key_uuid CHAR(36) NULL,
    endpoint VARCHAR(100) NOT NULL,
    model VARCHAR(150) NULL,
    embedding_model VARCHAR(150) NULL,
    prompt_tokens INT NULL,
    completion_tokens INT NULL,
    total_tokens INT NULL,
    estimated_cost DECIMAL(12, 6) NULL,
    status ENUM('success', 'failed') NOT NULL DEFAULT 'success',
    error_code VARCHAR(100) NULL,
    created_at TIMESTAMP NULL,
    INDEX idx_usage_tenant_created (tenant_uuid, created_at)
);
```

### 11.13 `model_configs`

Menyimpan konfigurasi model.

```sql
CREATE TABLE model_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NULL,
    name VARCHAR(150) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(150) NOT NULL,
    temperature DECIMAL(4, 2) NOT NULL DEFAULT 0.20,
    max_tokens INT NULL,
    top_p DECIMAL(4, 2) NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);
```

### 11.14 `answer_feedback`

Menyimpan feedback jawaban.

```sql
CREATE TABLE answer_feedback (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    feedback_uuid CHAR(36) NOT NULL UNIQUE,
    tenant_uuid CHAR(36) NOT NULL,
    session_uuid CHAR(36) NULL,
    message_uuid CHAR(36) NOT NULL,
    rating INT NULL,
    is_helpful BOOLEAN NULL,
    reason TEXT NULL,
    metadata JSON NULL,
    created_at TIMESTAMP NULL,
    INDEX idx_feedback_tenant (tenant_uuid)
);
```

---

## 12. Desain Qdrant Collection

### 12.1 Nama Collection

Rekomendasi nama collection:

```text
tenant_{tenant_uuid}_collection_{collection_uuid}
```

Alternatif untuk skala besar:

```text
global_ai_chunks
```

Dengan filter wajib:

```json
{
  "tenant_uuid": "...",
  "collection_uuid": "..."
}
```

### 12.2 Vector Payload

Setiap vector wajib membawa payload berikut:

```json
{
  "tenant_uuid": "tenant_001",
  "collection_uuid": "collection_001",
  "document_uuid": "doc_001",
  "chunk_uuid": "chunk_001",
  "external_document_id": "materi_1001",
  "source_type": "document",
  "visibility": "restricted",
  "metadata": {
    "subject": "IPA",
    "grade": "7",
    "topic": "Ekosistem"
  },
  "page_number": 2,
  "chunk_index": 5,
  "created_at": "2026-05-15T00:00:00Z"
}
```

### 12.3 Metadata Filter

Saat chat, service wajib memfilter vector berdasarkan:

1. tenant_uuid
2. collection_uuid
3. allowed_document_ids jika ada
4. metadata scope jika dikirim client
5. document status indexed
6. visibility policy

Contoh filter konseptual:

```json
{
  "must": [
    {"key": "tenant_uuid", "match": {"value": "tenant_001"}},
    {"key": "collection_uuid", "match": {"value": "collection_001"}},
    {"key": "metadata.grade", "match": {"value": "7"}},
    {"key": "metadata.subject", "match": {"value": "IPA"}}
  ]
}
```

---

## 13. API Specification

### 13.1 Base URL

```http
https://api.your-ai-service.com
```

### 13.2 Authentication

Semua endpoint protected memakai header:

```http
Authorization: Bearer sk_live_xxxxxxxxx
X-Tenant-ID: tenant_uuid
```

### 13.3 Standard Response

Response sukses:

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-05-15T10:00:00Z"
  }
}
```

Response gagal:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "File type is not supported",
    "details": {}
  },
  "meta": {
    "request_id": "req_123",
    "timestamp": "2026-05-15T10:00:00Z"
  }
}
```

---

## 14. Endpoint Detail

### 14.1 Health Check

```http
GET /v1/health
```

Response:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "database": "connected",
    "vector_db": "connected",
    "queue": "connected"
  }
}
```

---

### 14.2 Create Collection

```http
POST /v1/collections
```

Request:

```json
{
  "name": "Materi Sekolah",
  "description": "Knowledge base untuk materi pembelajaran",
  "metadata_schema": {
    "grade": "string",
    "subject": "string",
    "topic": "string"
  }
}
```

Response:

```json
{
  "success": true,
  "data": {
    "collection_uuid": "col_001",
    "name": "Materi Sekolah",
    "status": "active"
  }
}
```

---

### 14.3 Upload and Index Document

```http
POST /v1/documents
Content-Type: multipart/form-data
```

Form data:

```text
file: binary
collection_uuid: col_001
title: Materi Ekosistem
external_document_id: materi_1001
metadata: {"grade":"7","subject":"IPA","topic":"Ekosistem"}
indexing_mode: async
```

Response:

```json
{
  "success": true,
  "data": {
    "document_uuid": "doc_001",
    "job_uuid": "job_001",
    "status": "processing"
  }
}
```

---

### 14.4 Index Document from URL

```http
POST /v1/documents/from-url
```

Request:

```json
{
  "collection_uuid": "col_001",
  "title": "Materi Ekosistem",
  "source_url": "https://example.com/file.pdf",
  "external_document_id": "materi_1001",
  "metadata": {
    "grade": "7",
    "subject": "IPA",
    "topic": "Ekosistem"
  },
  "indexing_mode": "async"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "document_uuid": "doc_001",
    "job_uuid": "job_001",
    "status": "processing"
  }
}
```

---

### 14.5 Get Document Status

```http
GET /v1/documents/{document_uuid}
```

Response:

```json
{
  "success": true,
  "data": {
    "document_uuid": "doc_001",
    "title": "Materi Ekosistem",
    "status": "indexed",
    "total_pages": 12,
    "total_chunks": 28,
    "created_at": "2026-05-15T10:00:00Z"
  }
}
```

---

### 14.6 Delete Document

```http
DELETE /v1/documents/{document_uuid}
```

Response:

```json
{
  "success": true,
  "data": {
    "document_uuid": "doc_001",
    "status": "deleted"
  }
}
```

Saat delete, service wajib:

1. update status dokumen menjadi deleted
2. hapus atau soft-delete metadata chunk
3. hapus vector dari Qdrant
4. simpan audit log

---

### 14.7 Get Indexing Job Status

```http
GET /v1/jobs/{job_uuid}
```

Response:

```json
{
  "success": true,
  "data": {
    "job_uuid": "job_001",
    "status": "running",
    "progress": 65,
    "message": "Generating embeddings"
  }
}
```

---

### 14.8 Semantic Search

```http
POST /v1/search
```

Request:

```json
{
  "collection_uuid": "col_001",
  "query": "Apa itu ekosistem?",
  "top_k": 5,
  "filters": {
    "metadata.grade": "7",
    "metadata.subject": "IPA"
  },
  "allowed_document_ids": ["doc_001", "doc_002"],
  "include_content": true
}
```

Response:

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "chunk_uuid": "chunk_001",
        "document_uuid": "doc_001",
        "title": "Materi Ekosistem",
        "page_number": 2,
        "score": 0.87,
        "content": "Ekosistem adalah hubungan antara makhluk hidup dan lingkungannya..."
      }
    ]
  }
}
```

---

### 14.9 Chat Completion

```http
POST /v1/chat
```

Request:

```json
{
  "session_uuid": "sess_001",
  "collection_uuid": "col_001",
  "external_user_id": "user_123",
  "message": "Jelaskan pengertian ekosistem dengan bahasa sederhana",
  "filters": {
    "metadata.grade": "7",
    "metadata.subject": "IPA"
  },
  "allowed_document_ids": ["doc_001"],
  "options": {
    "model": "openai/gpt-4o-mini",
    "temperature": 0.2,
    "top_k": 5,
    "with_sources": true,
    "answer_style": "simple"
  }
}
```

Response:

```json
{
  "success": true,
  "data": {
    "session_uuid": "sess_001",
    "message_uuid": "msg_002",
    "answer": "Ekosistem adalah hubungan antara makhluk hidup dan lingkungan tempat mereka hidup. Contohnya, ikan hidup di sungai dan membutuhkan air, makanan, serta tumbuhan air.",
    "sources": [
      {
        "document_uuid": "doc_001",
        "title": "Materi Ekosistem",
        "page_number": 2,
        "chunk_uuid": "chunk_001",
        "score": 0.87
      }
    ],
    "usage": {
      "model": "openai/gpt-4o-mini",
      "prompt_tokens": 1420,
      "completion_tokens": 120,
      "total_tokens": 1540
    }
  }
}
```

---

### 14.10 Streaming Chat

```http
POST /v1/chat/stream
```

Mode response:

```text
text/event-stream
```

Event contoh:

```text
event: token
data: {"content":"Ekosistem"}

event: token
data: {"content":" adalah"}

event: done
data: {"message_uuid":"msg_002","sources":[...],"usage":{...}}
```

---

### 14.11 Create Feedback

```http
POST /v1/feedback
```

Request:

```json
{
  "message_uuid": "msg_002",
  "rating": 4,
  "is_helpful": true,
  "reason": "Jawaban mudah dipahami"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "feedback_uuid": "fb_001",
    "status": "saved"
  }
}
```

---

### 14.12 Usage Summary

```http
GET /v1/usage?start_date=2026-05-01&end_date=2026-05-31
```

Response:

```json
{
  "success": true,
  "data": {
    "total_requests": 1200,
    "total_tokens": 850000,
    "estimated_cost": 3.75,
    "by_model": [
      {
        "model": "openai/gpt-4o-mini",
        "requests": 1100,
        "tokens": 790000
      }
    ]
  }
}
```

---

## 15. Prompt Design

### 15.1 System Prompt Default

```text
Anda adalah asisten AI yang menjawab berdasarkan konteks yang diberikan sistem.
Gunakan hanya informasi yang tersedia dalam konteks jika pertanyaan berkaitan dengan dokumen.
Jika konteks tidak cukup, katakan bahwa informasi tidak ditemukan dalam dokumen.
Jangan membuat sumber palsu.
Jawab dengan bahasa yang jelas, ringkas, dan sesuai kebutuhan pengguna.
Sertakan sumber jika tersedia.
```

### 15.2 Context Template

```text
Berikut konteks yang relevan dari dokumen:

[Source 1]
Document: {title}
Page: {page_number}
Content:
{chunk_content}

[Source 2]
Document: {title}
Page: {page_number}
Content:
{chunk_content}
```

### 15.3 User Message Template

```text
Pertanyaan pengguna:
{user_message}
```

### 15.4 Aturan Jawaban Berbasis Dokumen

1. Jawab berdasarkan konteks.
2. Jangan mengarang data di luar konteks.
3. Jika konteks tidak cukup, sampaikan keterbatasan.
4. Gunakan bahasa sesuai parameter `answer_style`.
5. Sertakan sumber jika `with_sources = true`.
6. Jangan menampilkan potongan konteks mentah kecuali diminta.

---

## 16. Retrieval Strategy

### 16.1 Tahap Retrieval

1. Terima query dari user.
2. Buat embedding query.
3. Jalankan vector search dengan filter metadata.
4. Ambil top_k chunk.
5. Buang chunk yang terlalu mirip atau duplikat.
6. Rerank jika fitur aktif.
7. Batasi konteks sesuai max_context_tokens.
8. Susun context block untuk prompt.

### 16.2 Parameter Default

```yaml
retrieval:
  top_k: 6
  min_score: 0.35
  max_context_tokens: 8000
  chunk_size_tokens: 1000
  chunk_overlap_tokens: 150
  rerank_enabled: false
  hybrid_search_enabled: false
```

### 16.3 Mode Retrieval

| Mode | Fungsi |
|---|---|
| document_only | Hanya mencari dari dokumen tertentu |
| collection | Mencari semua dokumen dalam collection |
| scoped | Mencari berdasarkan metadata filter |
| global | Mencari semua data tenant |
| hybrid | Gabungan vector dan keyword search |

---

## 17. Security Requirements

### 17.1 API Key

1. API key hanya ditampilkan sekali saat dibuat.
2. Database hanya menyimpan hash API key.
3. API key memiliki prefix untuk identifikasi.
4. API key dapat di-revoke.
5. API key dapat dibatasi scope.

### 17.2 Tenant Isolation

1. Semua tabel wajib menyimpan `tenant_uuid`.
2. Semua query wajib memfilter `tenant_uuid`.
3. Semua vector payload wajib menyimpan `tenant_uuid`.
4. Request tanpa tenant valid harus ditolak.

### 17.3 Scope Access

Client dapat mengirim scope:

```json
{
  "allowed_document_ids": ["doc_001"],
  "filters": {
    "metadata.grade": "7",
    "metadata.subject": "IPA"
  }
}
```

Service wajib hanya mencari konteks dalam scope tersebut.

### 17.4 File Security

1. Validasi MIME type.
2. Validasi extension.
3. Batasi ukuran file.
4. Rename file saat disimpan.
5. Scan file opsional.
6. Tolak file executable.
7. Cleanup file sementara.

### 17.5 Rate Limit

Contoh default:

```yaml
rate_limit:
  requests_per_minute: 60
  chat_requests_per_minute: 30
  upload_requests_per_minute: 10
  max_file_size_mb: 50
```

### 17.6 Data Privacy

1. Jangan kirim seluruh dokumen ke model.
2. Kirim hanya chunk relevan.
3. Jangan log API key.
4. Jangan log file mentah di application log.
5. Masking data sensitif opsional.
6. Set retention policy untuk chat log.

---

## 18. Non-Functional Requirements

### 18.1 Performance

Target MVP:

| Aktivitas | Target |
|---|---|
| Health check | < 200 ms |
| Semantic search | < 1.5 detik |
| Chat non-streaming | < 15 detik |
| Chat streaming first token | < 3 detik |
| Upload response async | < 2 detik |
| Indexing PDF 20 halaman | < 2 menit, tergantung embedding provider |

### 18.2 Scalability

Service harus dapat diskalakan dengan pola:

1. Tambah API container.
2. Tambah worker container.
3. Tambah Redis worker concurrency.
4. Tambah Qdrant resource.
5. Tambah MySQL read replica jika perlu.
6. Pisahkan embedding worker jika beban besar.

### 18.3 Availability

Target awal:

```text
MVP: 99%
Production v1: 99.5%
Production v2: 99.9%
```

### 18.4 Reliability

1. Job indexing harus retry otomatis.
2. LLM call harus punya timeout.
3. Provider error harus dinormalisasi.
4. Worker gagal tidak boleh merusak metadata.
5. Delete dokumen harus idempotent.
6. Vector dan metadata harus bisa di-reconcile.

### 18.5 Maintainability

1. Struktur modul jelas.
2. Semua endpoint terdokumentasi.
3. Migration database wajib memakai Alembic.
4. Config memakai environment variable.
5. Unit test untuk service utama.
6. Integration test untuk API utama.

---

## 19. Error Handling

### 19.1 Error Code

| Code | HTTP | Penjelasan |
|---|---:|---|
| UNAUTHORIZED | 401 | API key tidak valid |
| FORBIDDEN | 403 | Scope tidak diizinkan |
| TENANT_INACTIVE | 403 | Tenant tidak aktif |
| VALIDATION_ERROR | 422 | Request tidak valid |
| FILE_TOO_LARGE | 413 | File terlalu besar |
| UNSUPPORTED_FILE_TYPE | 415 | Format file tidak didukung |
| DOCUMENT_NOT_FOUND | 404 | Dokumen tidak ditemukan |
| COLLECTION_NOT_FOUND | 404 | Collection tidak ditemukan |
| INDEXING_FAILED | 500 | Indexing gagal |
| VECTOR_DB_ERROR | 500 | Vector database error |
| LLM_PROVIDER_ERROR | 502 | Provider model error |
| RATE_LIMITED | 429 | Request terlalu banyak |
| QUOTA_EXCEEDED | 429 | Quota habis |

### 19.2 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "File type .exe is not supported",
    "details": {
      "allowed_types": ["pdf", "docx", "xlsx", "csv", "txt"]
    }
  },
  "meta": {
    "request_id": "req_001"
  }
}
```

---

## 20. Configuration

### 20.1 Environment Variables

```env
APP_NAME=ai-chatbot-service
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000

DATABASE_URL=mysql+asyncmy://user:password@mysql:3306/ai_service_db

REDIS_URL=redis://redis:6379/0

QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=

OBJECT_STORAGE_DRIVER=minio
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=miniosecret
MINIO_BUCKET=ai-documents

OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_CHAT_MODEL=openai/gpt-4o-mini

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

MAX_FILE_SIZE_MB=50
DEFAULT_CHUNK_SIZE=1000
DEFAULT_CHUNK_OVERLAP=150
DEFAULT_TOP_K=6
DEFAULT_MAX_CONTEXT_TOKENS=8000

RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

---

## 21. Struktur Folder Project

```text
ai-chatbot-service/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes_health.py
│   │   │   ├── routes_collections.py
│   │   │   ├── routes_documents.py
│   │   │   ├── routes_chat.py
│   │   │   ├── routes_search.py
│   │   │   ├── routes_jobs.py
│   │   │   ├── routes_usage.py
│   │   │   └── routes_feedback.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   ├── errors.py
│   │   └── rate_limit.py
│   ├── db/
│   │   ├── session.py
│   │   ├── models/
│   │   └── repositories/
│   ├── schemas/
│   ├── services/
│   │   ├── tenant_service.py
│   │   ├── api_key_service.py
│   │   ├── document_service.py
│   │   ├── parser_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_service.py
│   │   ├── retrieval_service.py
│   │   ├── prompt_service.py
│   │   ├── llm_service.py
│   │   ├── chat_service.py
│   │   ├── search_service.py
│   │   ├── usage_service.py
│   │   └── feedback_service.py
│   ├── providers/
│   │   ├── llm/
│   │   │   ├── openrouter_provider.py
│   │   │   └── base.py
│   │   ├── embedding/
│   │   │   ├── openai_embedding.py
│   │   │   ├── local_embedding.py
│   │   │   └── base.py
│   │   └── storage/
│   │       ├── local_storage.py
│   │       └── base.py
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks_indexing.py
│   └── utils/
├── migrations/
├── tests/
│   ├── unit/
│   └── integration/
├── docker/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── alembic.ini
└── README.md
```

---

## 22. Docker Compose MVP

```yaml
version: "3.9"

services:
  api:
    build: .
    container_name: ai_service_api
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - local_storage:/app/storage
    depends_on:
      - mysql
      - redis
      - qdrant

  worker:
    build: .
    container_name: ai_service_worker
    command: celery -A app.workers.celery_app worker --loglevel=info
    env_file:
      - .env
    volumes:
      - local_storage:/app/storage
    depends_on:
      - mysql
      - redis
      - qdrant

  mysql:
    image: mysql:8.4
    container_name: ai_service_mysql
    environment:
      MYSQL_DATABASE: ai_service_db
      MYSQL_USER: ai_user
      MYSQL_PASSWORD: ai_password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7
    container_name: ai_service_redis
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ai_service_qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  mysql_data:
  qdrant_data:
  local_storage:
```

---

## 23. Guardrail Produk

### 23.1 Guardrail Jawaban

1. Jawaban berbasis dokumen harus mengikuti konteks.
2. Jika sumber tidak cukup, sistem harus menyatakan tidak cukup informasi.
3. Jangan membuat kutipan atau sumber palsu.
4. Jangan mengklaim isi dokumen jika chunk tidak ditemukan.
5. Hindari instruksi yang meminta model mengabaikan system prompt.

### 23.2 Guardrail Dokumen

1. Reject file tidak valid.
2. Batasi ukuran file.
3. Hapus file sementara.
4. Sanitasi nama file.
5. Simpan file dengan UUID.
6. Pastikan vector terhapus saat dokumen dihapus.

### 23.3 Guardrail Multi-Tenant

1. Tenant A tidak boleh melihat data tenant B.
2. Semua query database wajib membawa tenant filter.
3. Semua vector search wajib membawa tenant filter.
4. API key hanya berlaku untuk tenant yang sesuai.

---

## 24. Acceptance Criteria

### 24.1 MVP

Produk dianggap lolos MVP jika:

1. API dapat berjalan dengan Docker Compose.
2. Dokumentasi Swagger aktif di `/docs`.
3. Tenant dan API key dapat dibuat.
4. Client dapat upload PDF, DOCX, XLSX, CSV, dan TXT.
5. Dokumen diproses secara asynchronous.
6. Status indexing dapat dilihat.
7. Chunk tersimpan di MySQL.
8. Vector tersimpan di Qdrant.
9. Endpoint search mengembalikan hasil relevan.
10. Endpoint chat menjawab berdasarkan dokumen.
11. Jawaban chat menyertakan sumber.
12. Riwayat chat tersimpan.
13. Usage log tersimpan.
14. Rate limit berjalan.
15. Delete dokumen menghapus metadata dan vector.
16. Semua endpoint protected membutuhkan API key.
17. Tenant isolation berjalan.
18. Unit test utama lulus.
19. Integration test upload, indexing, search, dan chat lulus.

### 24.2 Quality Acceptance

Kriteria kualitas:

1. Jawaban tidak mengarang saat konteks kosong.
2. Jawaban mencantumkan sumber jika tersedia.
3. Retrieval memakai metadata filter.
4. Response error konsisten.
5. Indexing gagal tidak membuat dokumen berstatus indexed.
6. Worker retry berjalan.
7. Service tetap responsif saat indexing berjalan.

---

## 25. Roadmap Pengembangan

### Sprint 1: Fondasi Service

Durasi: 1 minggu

Output:

1. Setup FastAPI project.
2. Setup Docker Compose.
3. Setup MySQL.
4. Setup Redis.
5. Setup Qdrant.
6. Setup Local File Storage dengan persistent volume.
7. Setup SQLAlchemy dan Alembic.
8. Endpoint health check.
9. Struktur folder final.

### Sprint 2: Auth, Tenant, dan Collection

Durasi: 1 minggu

Output:

1. Tabel tenant.
2. Tabel api_clients.
3. Tabel api_keys.
4. Hash API key.
5. Middleware authentication.
6. Endpoint collection.
7. Tenant isolation basic.
8. Rate limit basic.

### Sprint 3: Document Upload dan Storage

Durasi: 1 minggu

Output:

1. Upload file endpoint.
2. Validasi file.
3. Simpan file ke Local File Storage.
4. Tabel documents.
5. Tabel indexing_jobs.
6. Queue indexing.
7. Endpoint status job.
8. Delete dokumen basic.

### Sprint 4: Parser dan Chunking

Durasi: 1 minggu

Output:

1. Parser PDF.
2. Parser DOCX.
3. Parser XLSX.
4. Parser CSV.
5. Parser TXT.
6. Text cleaning.
7. Chunking.
8. Simpan chunk ke database.

### Sprint 5: Embedding dan Vector Store

Durasi: 1 minggu

Output:

1. Embedding provider adapter.
2. Batch embedding.
3. Qdrant collection.
4. Upsert vector.
5. Metadata payload.
6. Delete vector.
7. Re-index basic.

### Sprint 6: Search dan Retrieval

Durasi: 1 minggu

Output:

1. Endpoint semantic search.
2. Metadata filter.
3. top_k retrieval.
4. Score threshold.
5. Load source metadata.
6. Search response with snippet.

### Sprint 7: Chat RAG

Durasi: 1 minggu

Output:

1. Chat endpoint.
2. Prompt builder.
3. OpenRouter adapter.
4. Context injection.
5. Source citation.
6. Chat session.
7. Chat message storage.
8. Usage log.

### Sprint 8: Hardening MVP

Durasi: 1 minggu

Output:

1. Error handling konsisten.
2. Unit test.
3. Integration test.
4. Rate limit final.
5. Logging.
6. Retry worker.
7. Documentation.
8. Deployment guide.

---

## 26. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Retrieval tidak akurat | Jawaban tidak sesuai dokumen | Perbaiki chunking, metadata filter, reranking |
| Dokumen terlalu besar | Indexing lambat | Async worker, batch embedding, file limit |
| Biaya model tinggi | Operasional mahal | Model routing, quota, cache, model murah untuk default |
| Data tenant bocor | Risiko keamanan tinggi | Tenant filter wajib, test isolation |
| Model mengarang | Jawaban tidak valid | Strict prompt, source-based answer, fallback saat konteks kosong |
| Vector dan metadata tidak sinkron | Search rusak | Reconcile job dan delete idempotent |
| API disalahgunakan | Biaya membengkak | API key, rate limit, quota |
| File berbahaya | Risiko server | MIME validation, extension validation, scanner opsional |

---

## 27. Rekomendasi Konfigurasi MVP

### 27.1 Model Chat Default

```yaml
chat_model:
  provider: openrouter
  model: openai/gpt-4o-mini
  temperature: 0.2
  max_tokens: 1000
```

Alternatif hemat:

```yaml
chat_model:
  provider: openrouter
  model: meta-llama/llama-3.1-8b-instruct
  temperature: 0.2
  max_tokens: 1000
```

### 27.2 Embedding Default

Jika ingin simpel:

```yaml
embedding:
  provider: openai
  model: text-embedding-3-small
```

Jika ingin lebih mandiri:

```yaml
embedding:
  provider: local
  model: bge-m3
```

### 27.3 Chunking Default

```yaml
chunking:
  strategy: recursive
  chunk_size_tokens: 1000
  chunk_overlap_tokens: 150
```

### 27.4 Retrieval Default

```yaml
retrieval:
  top_k: 6
  min_score: 0.35
  max_context_tokens: 8000
```

---

## 28. Deployment Strategy

### 28.1 Development

Gunakan:

```text
Docker Compose
FastAPI reload
MySQL container
Redis container
Qdrant container
Local File Storage volume
```

### 28.2 Staging

Gunakan:

```text
Docker Compose atau single VM
HTTPS reverse proxy
Persistent volume
Backup database
Monitoring basic
```

### 28.3 Production

Gunakan:

```text
Container orchestration
Managed MySQL atau dedicated MySQL
Dedicated Qdrant storage
Redis managed atau dedicated
Persistent Local File Storage volume atau dedicated disk
Horizontal scaling API
Horizontal scaling worker
Centralized logging
Metrics monitoring
Automated backup
```

Catatan penting: jika tetap memakai Local File Storage, deployment production paling aman dimulai dari satu server atau satu shared persistent volume. Jika API dan worker berjalan di beberapa server, semua instance harus mengakses folder storage yang sama melalui shared volume agar file dapat dibaca konsisten.

---

## 29. Testing Plan

### 29.1 Unit Test

Test wajib:

1. API key hashing.
2. Tenant validation.
3. File validation.
4. Parser per format.
5. Chunking.
6. Embedding adapter mock.
7. Prompt builder.
8. Error formatter.

### 29.2 Integration Test

Test wajib:

1. Upload dokumen.
2. Indexing job.
3. Vector upsert.
4. Semantic search.
5. Chat RAG.
6. Delete dokumen.
7. Tenant isolation.
8. Rate limit.

### 29.3 Evaluation Test

Buat dataset evaluasi sederhana:

```text
10 dokumen
50 pertanyaan
50 expected answer points
50 expected source chunks
```

Metrik:

1. retrieval precision
2. source accuracy
3. answer faithfulness
4. response latency
5. cost per request
6. failure rate

---

## 30. Dokumentasi untuk Client Developer

Dokumentasi minimum:

1. Getting started.
2. Cara membuat API key.
3. Cara membuat collection.
4. Cara upload dokumen.
5. Cara cek status indexing.
6. Cara search.
7. Cara chat.
8. Cara streaming chat.
9. Cara delete dokumen.
10. Error code.
11. Rate limit.
12. Contoh integrasi JavaScript.
13. Contoh integrasi PHP.
14. Contoh integrasi Python.

---

## 31. Kesimpulan Desain

Microservice ini dirancang sebagai AI API mandiri yang dapat dipakai oleh banyak aplikasi. Database aplikasi client tidak dicampur dengan database AI. Model AI tidak diberi akses langsung ke database. Semua konteks dipilih oleh Python service melalui proses RAG, metadata filtering, dan prompt builder.

Spesifikasi utama yang digunakan:

1. Python 3.12
2. FastAPI
3. MySQL 8.4 LTS
4. SQLAlchemy 2
5. Alembic
6. Redis
7. Celery
8. Qdrant
9. Local File Storage
10. OpenRouter
11. Pluggable embedding provider
12. Docker Compose untuk MVP
13. API key authentication
14. Multi-tenant isolation
15. RAG sebagai metode utama

Dengan desain ini, produk dapat dimulai dari MVP yang sederhana, lalu berkembang menjadi AI service production yang reusable, aman, dan scalable.

---

## 32. Referensi Teknis

1. FastAPI Documentation: https://fastapi.tiangolo.com/
2. OpenRouter Documentation: https://openrouter.ai/docs/
3. Qdrant Documentation: https://qdrant.tech/documentation/
4. MySQL 8.4 Reference Manual: https://dev.mysql.com/doc/refman/8.4/en/
5. SQLAlchemy Documentation: https://docs.sqlalchemy.org/
6. Celery Documentation: https://docs.celeryq.dev/
7. Redis Documentation: https://redis.io/docs/latest/
8. Pydantic Documentation: https://docs.pydantic.dev/
9. Alembic Documentation: https://alembic.sqlalchemy.org/
