from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from app.services.chat_service import ChatService
from app.db.database import SessionLocal, engine
from app.models.chat import ChatHistory
from sqlalchemy.orm import Session
from app.utils.logger import logger
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI()

# Serve HTML templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.debug("Home endpoint called")  # Debug log
    return templates.TemplateResponse("index.html", {"request": request})

# Create database tables
ChatHistory.metadata.create_all(bind=engine)

class ChatRequest(BaseModel):
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    logger.debug("Chat endpoint called")  # Debug log
    chat_service = ChatService()
    try:
        response = chat_service.get_response(request.message)

        # Save chat history
        chat_record = ChatHistory(
            user_message=request.message,
            bot_response=response
        )
        db.add(chat_record)
        db.commit()
        logger.debug("Chat history saved to database")  # Debug log

        return {"response": response}

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")  # Error log
        raise HTTPException(status_code=500, detail=str(e))