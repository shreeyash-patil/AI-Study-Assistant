from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str
    session_id: str

class AnswerResponse(BaseModel):
    answer: str
    session_id: str
    source_pages: list[int] = []