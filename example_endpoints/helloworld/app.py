from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class MessagePayload(BaseModel):
    message: str
    chat_id: int

@app.post("/myendpoint")
async def handle_message(payload: MessagePayload):
    try:
        # Here you can add your message processing logic
        print(f"Received message: {payload.message} from chat_id: {payload.chat_id}")
        
        # Return a success response with messageToUser
        # If messageToUser is present in the response, it will be sent to the Telegram user
        return {
            "status": "success", 
            "message": "Message received successfully",
            "messageToUser": "Hello user, this is a test message from the local helloworld example backend.",
            "includeVoiceMessage": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
