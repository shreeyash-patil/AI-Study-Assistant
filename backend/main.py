from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import QuestionRequest, AnswerResponse
from pdf_processor import parse_pdf, generate_session_id
from rag import build_vector_store, get_answer, get_vector_store, check_cache, store_in_cache
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

@app.get("/")
def root():
    return {"message": "Study Assistant API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_bytes = await file.read()
    session_id = generate_session_id()
    chunks = parse_pdf(file_bytes)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    vector_store = build_vector_store(chunks, session_id)
    sessions[session_id] = vector_store
    
    return {"session_id": session_id, "message": "PDF uploaded successfully"}

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    vector_store = get_vector_store(request.session_id)

    if vector_store is None:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first")

    cached_answer = check_cache(request.question, request.session_id)
    if cached_answer:
        return AnswerResponse(answer=cached_answer, session_id=request.session_id)

    answer = get_answer(request.question, vector_store)
    store_in_cache(request.question, answer, request.session_id)

    return AnswerResponse(answer=answer, session_id=request.session_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)