# Quiz API

A simple Python/Flask quiz app built for learning CI/CD monitoring with GitHub Actions.

---

## What it does

- Create quizzes with multiple-choice questions
- List all available quizzes
- Submit answers and get a score back instantly
- `/health` endpoint for CI/CD pipeline health checks

---

## Project structure

```
quiz-api/
├── app.py               # Flask app — 4 endpoints
├── tests/
│   ├── __init__.py
│   └── test_app.py      # 8 pytest test cases
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check — used by CI/CD after every deploy |
| GET | `/quizzes` | List all quizzes |
| POST | `/quizzes` | Create a new quiz |
| POST | `/quizzes/<id>/submit` | Submit answers and get your score |

---

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/your-username/quiz-api.git
cd quiz-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
python app.py
```

The app runs at `http://localhost:5000`.

---

## Run tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

All 8 tests should pass with ~95%+ coverage.

---

## Try it out

**Create a quiz:**
```bash
curl -X POST http://localhost:5000/quizzes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "questions": [
      {
        "question": "What does len() do?",
        "options": ["Adds numbers", "Returns length", "Loops", "Prints"],
        "answer": "Returns length"
      },
      {
        "question": "Which keyword defines a function?",
        "options": ["func", "def", "define", "fun"],
        "answer": "def"
      }
    ]
  }'
```

**List all quizzes:**
```bash
curl http://localhost:5000/quizzes
```

**Submit answers:**
```bash
curl -X POST http://localhost:5000/quizzes/1/submit \
  -H "Content-Type: application/json" \
  -d '{"answers": ["Returns length", "def"]}'
```

**Example response:**
```json
{
  "quiz_id": 1,
  "score": 2,
  "total": 2,
  "percentage": 100.0,
  "passed": true
}
```

**Health check:**
```bash
curl http://localhost:5000/health
```

---

## CI/CD

This project uses GitHub Actions for continuous integration. On every push:

1. Installs dependencies
2. Runs all tests with `pytest`
3. Reports test coverage
4. (Phase 4) Deploys to staging and pings `/health` to confirm the app is live

See `.github/workflows/ci.yml` for the full pipeline definition.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |
| `requests` | HTTP calls in tests |

---

## Learning goals

This project is Phase 1 of a 5-phase CI/CD monitoring course:

| Phase | What you learn |
|-------|---------------|
| 1 | Python app structure, writing testable code, the `/health` endpoint |
| 2 | GitHub Actions — triggers, jobs, steps, runners |
| 3 | Test monitoring — coverage reports, PR comments, status badges |
| 4 | Deployment monitoring — auto-deploy, post-deploy health checks |
| 5 | Alerting — Slack notifications, monitoring dashboard |