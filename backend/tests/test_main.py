import io
from fastapi.testclient import TestClient
from main import app
import main

client = TestClient(app)


def test_root_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Study Assistant API is running"


def test_upload_rejects_non_pdf_file():
    fake_file = io.BytesIO(b"just some text, not a real pdf")
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400


def test_upload_accepts_valid_pdf(sample_pdf_bytes):
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["message"] == "PDF uploaded successfully"


def test_ask_with_unknown_session_returns_404():
    response = client.post(
        "/ask",
        json={"question": "What is this about?", "session_id": "does-not-exist"}
    )
    assert response.status_code == 404


def test_ask_returns_mocked_answer(sample_pdf_bytes, monkeypatch):
    upload_response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")}
    )
    session_id = upload_response.json()["session_id"]

    def fake_get_answer(question, collection):
        return "This is a mocked answer.", [1]

    monkeypatch.setattr(main, "get_answer", fake_get_answer)

    response = client.post(
        "/ask",
        json={"question": "What is this document about?", "session_id": session_id}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer."
    assert data["source_pages"] == [1]