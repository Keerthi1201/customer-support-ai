from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from query_engine import ask_question, load_dataset
from anomaly import detect_anomalies


app = FastAPI(
    title="AI Customer Support Ticket System",
    description="Python Pandas + Ollama based support ticket query and anomaly detection API",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    question: str


@app.on_event("startup")
def startup_event():
    load_dataset()


@app.get("/health")
def health():
    return {
        "status": "running",
        "message": "AI Support Ticket API is running successfully"
    }


@app.post("/query")
def query(data: QueryRequest):
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        return ask_question(data.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomalies")
def anomalies():
    try:
        return detect_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
