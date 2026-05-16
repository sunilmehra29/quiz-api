import os
import string
import random
import time
from flask import Flask, jsonify, request, redirect, abort
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

quizzes = {}
next_id = 1

# Prometheus metrics
REQUEST_COUNT = Counter(
    'quiz_api_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'quiz_api_request_duration_seconds',
    'Request latency in seconds',
    ['endpoint']
)

@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def track_metrics(response):
    if request.path != '/metrics':
        latency = time.time() - request._start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    return response

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})

# ... rest of your app stays the same

@app.route("/quizzes", methods=["GET"])
def list_quizzes():
    return jsonify({"quizzes": list(quizzes.values())})


@app.route("/quizzes", methods=["POST"])
def create_quiz():
    global next_id
    data = request.get_json()

    if not data or "title" not in data:
        abort(400, description="Missing 'title' field")

    if "questions" not in data or len(data["questions"]) == 0:
        abort(400, description="Quiz must have at least one question")

    for q in data["questions"]:
        if not all(k in q for k in ("question", "options", "answer")):
            abort(400, description="Each question needs 'question', 'options', and 'answer'")
        if q["answer"] not in q["options"]:
            abort(400, description=f"Answer '{q['answer']}' must be one of the options")

    quiz = {
        "id": next_id,
        "title": data["title"],
        "questions": [
            {
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
            }
            for i, q in enumerate(data["questions"])
        ],
        "_answers": [q["answer"] for q in data["questions"]],
    }

    quizzes[next_id] = quiz
    next_id += 1

    # Return quiz without internal _answers key
    public_quiz = {k: v for k, v in quiz.items() if not k.startswith("_")}
    return jsonify(public_quiz), 201


@app.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    quiz = quizzes.get(quiz_id)
    if not quiz:
        abort(404, description=f"Quiz {quiz_id} not found")

    data = request.get_json()
    if not data or "answers" not in data:
        abort(400, description="Missing 'answers' field")

    submitted = data["answers"]
    correct_answers = quiz["_answers"]

    if len(submitted) != len(correct_answers):
        abort(400, description=f"Expected {len(correct_answers)} answers, got {len(submitted)}")

    score = sum(1 for s, c in zip(submitted, correct_answers) if s == c)
    total = len(correct_answers)
    percentage = round((score / total) * 100, 1)

    return jsonify({
        "quiz_id": quiz_id,
        "score": score,
        "total": total,
        "percentage": percentage,
        "passed": percentage >= 50.0,
    })


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)