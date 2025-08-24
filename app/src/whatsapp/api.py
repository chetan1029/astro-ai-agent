from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse

from app.src.birthprofile.service import BirthProfileService
from app.src.core.db import get_session
from app.src.whatsapp.dependencies import get_messaging_provider
from app.src.whatsapp.exceptions import WhatsappError
from app.src.whatsapp.providers.base import MessagingProvider
from app.src.whatsapp.service import parse_message_to_birth_profile
from app.src.core.config import get_settings

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_verify_token == get_settings().whatsapp_verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Verification failed", status_code=403)


@router.post("/webhook")
async def receive_whatsapp_message(
    request: Request,
    session=Depends(get_session),
    messaging: MessagingProvider = Depends(get_messaging_provider)
):
    provider = get_settings().whatsapp_provider

    # Handle Twilio (form-data) vs Cloud API (json)
    if provider == "twilio":
        form = await request.form()
        data = dict(form)
    else:
        data = await request.json()

    print("Incoming:", data)
    from_number, text, contact_name = messaging.parse_incoming(data)
    response_text = ""

    try:
        birth_profile = parse_message_to_birth_profile(text)
        service = BirthProfileService(session)
        result = await service.set_birth_profile(birth_profile)

        response_text = f"✅ Profile saved for {contact_name} {birth_profile.name} with id {result.id}"
        messaging.send_message(from_number, response_text)

    except WhatsappError as e:
        print("Error:", e)
        if from_number:
            messaging.send_message(
                from_number,
                "⚠️ Sorry, could not process your message. Please use format:\n\n"
                "Name, DOB (YYYY-MM-DD HH:MM), Place, Relationship"
            )

    return {"status": f"received {response_text}"}