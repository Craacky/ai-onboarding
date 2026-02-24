# AI Onboarding Assistant — SaaS Platform

**AI Onboarding Assistant** is a B2B SaaS platform designed to streamline employee integration using Artificial Intelligence. It allows companies to upload internal documentation (regulations, policies, instructions, FAQs) and provides new hires with a personal AI assistant that answers questions based strictly on the uploaded data.

The project is designed as a **Portfolio/Educational** piece demonstrating a fullstack + AI implementation at a **Junior to Middle developer level**.

---

## 🚀 Key Features

- **RAG-based AI:** High-fidelity answers based on company documents with zero hallucinations.
- **Multi-tenant Architecture:** Total data isolation between different organizations at the database and vector levels.
- **Real-time Interaction:** Chat streaming and document processing updates via WebSockets.
- **Role-Based Access (RBAC):** Admin (can upload docs/invite users) and Member (read-only) roles.
- **Subscription Management:** Integrated Stripe billing with tiered plans (Free, Pro, Enterprise).
- **Automated Pipeline:** Background document processing using Celery and Redis.



---

## 🛠 Technical Stack

| Category | Technology | Purpose |
| --- | --- | --- |
| **Backend** | FastAPI (Python 3.11+), SQLAlchemy, Alembic | REST API, WebSockets, ORM & Migrations |
| **Frontend** | React 18, TypeScript, TailwindCSS, React Query | SPA Interface, styling, and state management |
| **AI / LLM** | LangChain, OpenAI (GPT-4o-mini), ChromaDB | RAG pipeline, embeddings, and vector storage |
| **Infrastructure** | Docker & Compose, Nginx, MinIO | Containerization, Proxy, and S3-compatible storage |
| **Data & Cache** | PostgreSQL 15, Redis 7, Celery | Relational data, task queuing, and caching |
| **CI/CD** | GitHub Actions | Automated testing and deployment |


---

## 🏗 System Architecture

### 1. Document Processing Flow

1. **Upload:** User uploads PDF/DOCX/TXT via React.
2. **Storage:** FastAPI saves the file to **MinIO** and marks it "pending" in **PostgreSQL**.
3. **Queue:** A task is sent to **Celery** via **Redis**.
4. **Vectorization:** Celery Worker extracts text, creates chunks, generates embeddings via **OpenAI**, and saves them to an isolated **ChromaDB** namespace.
5. **Notify:** Status updates to "ready" and the frontend is notified via **WebSocket**.



### 2. RAG Request Flow (Chat)

1. User asks a question; FastAPI verifies JWT and plan limits.
2. **LangChain** retrieves the top-5 relevant chunks from ChromaDB.
3. A prompt is formed using the retrieved context and sent to **OpenAI**.
4. The response is streamed back to the user via **WebSocket**.



---

## 🔐 Security & Multi-tenancy

- **Data Isolation:** Every table includes an `organization_id`. API requests automatically filter data based on the JWT token.
- **Vector Isolation:** Each organization has a unique namespace (`org_{id}`) in ChromaDB.
- **Auth:** JWT with short-lived access tokens (15 min) and long-lived refresh tokens (7 days).
- **Safety:** Rate limiting via Redis, SQL injection prevention via SQLAlchemy, and file type validation.



---

## 📂 Repository Structure

```text
├── backend/                # FastAPI application
│   ├── app/api/            # Resource routes
│   ├── app/models/         # SQLAlchemy models
│   ├── app/services/       # Business logic (LangChain, Stripe)
│   └── app/tasks/          # Celery tasks
├── frontend/               # React application
├── nginx/                  # Nginx configuration
├── .github/workflows/      # CI/CD pipelines
└── docker-compose.yml      # Local development setup
```
---
**WORK IN PROGRESS(WIP)**
