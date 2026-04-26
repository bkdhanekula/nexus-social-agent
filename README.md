# 🔗 Nexus Social — Python FastAPI + Gemini

AI-powered social media platform with **Python FastAPI backend**.
All 8 AI features live in Python. Frontend is pure UI — zero AI logic in JS.

---

## Architecture

```
Browser (HTML / CSS / JS)
  — Pure UI. gemini.js = thin fetch client only —
        ↓  HTTP POST to /api/social/*
FastAPI Backend (Python 3.12)
  ├── POST /api/social/captions          ← 3 caption variations
  ├── POST /api/social/hashtags          ← 20 tiered hashtags
  ├── POST /api/social/moderate          ← Safety scoring (JSON)
  ├── POST /api/social/sentiment         ← Emotional analysis
  ├── POST /api/social/growth            ← Creator strategy
  ├── POST /api/social/predict           ← Engagement prediction
  ├── POST /api/social/search            ← Smart search results
  ├── POST /api/social/trending-summary  ← Topic explanation
  └── GET  /health
        ↓
GeminiService (backend/services/gemini_service.py)
  — ALL prompt engineering, parsing, business logic —
        ↓
Secret Manager → Gemini 1.5 Flash API
```

---

## Project Structure

```
nexus-python/
├── backend/
│   ├── main.py                   # FastAPI app + static serving
│   ├── config.py                 # Pydantic settings (per-feature temperatures)
│   ├── routers/
│   │   └── social.py             # 8 HTTP endpoints (thin, no logic)
│   ├── services/
│   │   └── gemini_service.py     # ALL 8 AI features in Python
│   └── models/
│       └── schemas.py            # Pydantic request/response models
├── frontend/
│   ├── index.html                # App shell
│   ├── styles.css                # Styling
│   ├── gemini.js                 # API client (fetch only)
│   └── app.js                   # UI logic
├── requirements.txt
├── Dockerfile
├── deploy.sh
└── .env.example
```

---

## Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/nexus-social-app.git
cd nexus-social-app

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env → set GEMINI_API_KEY=AIza...

uvicorn backend.main:app --reload --port 8080
```

Open:
- **App** → http://localhost:8080
- **Swagger UI** → http://localhost:8080/api/docs
- **ReDoc** → http://localhost:8080/api/redoc

---

## API Reference

| Method | Endpoint | Input | Output |
|---|---|---|---|
| POST | `/api/social/captions` | description, style, platform | 3 captions array |
| POST | `/api/social/hashtags` | topic | 20 hashtags array |
| POST | `/api/social/moderate` | content | verdict + category scores |
| POST | `/api/social/sentiment` | text | sentiment breakdown |
| POST | `/api/social/growth` | niche | growth strategy |
| POST | `/api/social/predict` | post | engagement prediction |
| POST | `/api/social/search` | query | 4 result objects |
| POST | `/api/social/trending-summary` | hashtag | 2-sentence summary |
| GET | `/health` | — | status |

### Example

```bash
curl -X POST http://localhost:8080/api/social/captions \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Built an AI app at the GDG hackathon using Gemini + Cloud Run",
    "style": "Professional",
    "platform": "LinkedIn"
  }'
```

Response:
```json
{
  "captions": [
    "Shipped a production AI app at the GDG hackathon...",
    "Three hours. One AI wellness app. Deployed on GCP...",
    "The future of agentic AI is here..."
  ],
  "style": "Professional",
  "platform": "LinkedIn"
}
```

---

## Deploy to GCP

```bash
# Set PROJECT_ID in deploy.sh
chmod +x deploy.sh && ./deploy.sh

# After deploy:
# https://your-app.run.app/api/docs  ← Full Swagger UI
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML/CSS/JS (pure UI) |
| Backend | Python 3.12 + FastAPI |
| AI | Google Gemini 1.5 Flash |
| Validation | Pydantic v2 |
| Config | Pydantic Settings |
| Security | GCP Secret Manager |
| Deployment | GCP Cloud Run |
| Container | Docker multi-stage |
