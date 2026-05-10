from fastapi import FastAPI
from pydantic import BaseModel
from Main import MainExecution

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Jagruti AI Running"}

@app.post("/chat")
async def chat(req: ChatRequest):

    user_message = req.message

    response = MainExecution(user_message)

    return {
        "response": response
    }
