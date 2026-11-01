from pydantic import BaseModel


class WhatsAppMessage(BaseModel):
    sender: str
    message: str
    language: str = "auto"


class WhatsAppReply(BaseModel):
    message: str
    intent: str