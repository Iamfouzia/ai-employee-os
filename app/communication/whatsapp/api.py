import os

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.communication.whatsapp.webhook import WhatsAppWebhookHandler


router = APIRouter(
    prefix="/webhooks/whatsapp",
    tags=["WhatsApp"],
)

handler = WhatsAppWebhookHandler()

VERIFY_TOKEN = os.getenv(
    "WHATSAPP_VERIFY_TOKEN",
    "ai-employee-os-hafiz-dev",
)


@router.get("")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if (
        hub_mode == "subscribe"
        and hub_verify_token == VERIFY_TOKEN
    ):
        return PlainTextResponse(
            content=hub_challenge,
            status_code=200,
        )

    raise HTTPException(
        status_code=403,
        detail="Webhook verification failed",
    )


@router.post("")
async def receive_whatsapp_message(request: Request):
    payload = await request.json()
    return handler.handle(payload)