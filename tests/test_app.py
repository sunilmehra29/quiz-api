import pytest
from app import app, quizzes

SAMPLE_QUIZ = {
    "title": "Python Basics",
    "questions": [
        {
            "question": "What does len() do?",
            "options": ["Adds numbers", "Returns length", "Loops", "Prints"],
            "answer": "Returns length",
        },
        {
            "question": "Which keyword defines a function?",
            "options": ["func", "def", "define", "fun"],
            "answer": "def",
        },
    ],
}


# hey what's up with you.
@pytest.fixture(autouse=True)
def clear_store():
    quizzes.clear()
    # reset the ID counter too
    import app as app_module

    app_module.next_id = 1
    yield
    quizzes.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def created_quiz(client):
    response = client.post("/quizzes", json=SAMPLE_QUIZ)
    return response.get_json()


# --- Health ---


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# --- Create quiz ---


def test_create_quiz(client):
    r = client.post("/quizzes", json=SAMPLE_QUIZ)
    assert r.status_code == 201
    data = r.get_json()
    assert data["title"] == "Python Basics"
    assert len(data["questions"]) == 2
    assert "_answers" not in data  # answers must stay hidden


def test_create_quiz_missing_title(client):
    r = client.post("/quizzes", json={"questions": []})
    assert r.status_code == 400


def test_create_quiz_no_questions(client):
    r = client.post("/quizzes", json={"title": "Empty", "questions": []})
    assert r.status_code == 400


# --- List quizzes ---


def test_list_quizzes(client, created_quiz):
    r = client.get("/quizzes")
    assert r.status_code == 200
    assert len(r.get_json()["quizzes"]) == 1


# --- Submit ---


def test_submit_perfect_score(client, created_quiz):
    r = client.post("/quizzes/1/submit", json={"answers": ["Returns length", "def"]})
    assert r.status_code == 200
    data = r.get_json()
    assert data["score"] == 2
    assert data["percentage"] == 100.0
    assert data["passed"] is True


def test_submit_failing_score(client, created_quiz):
    r = client.post("/quizzes/1/submit", json={"answers": ["wrong", "wrong"]})
    assert r.status_code == 200
    data = r.get_json()
    assert data["score"] == 0
    assert data["passed"] is False


def test_submit_wrong_number_of_answers(client, created_quiz):
    r = client.post("/quizzes/1/submit", json={"answers": ["def"]})
    assert r.status_code == 400
