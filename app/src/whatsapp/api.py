from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse

from app.src.birthprofile.service import BirthProfileService
from app.src.core.config import get_settings
from app.src.core.db import get_session
from app.src.whatsapp.exceptions import WhatsappError
from app.src.whatsapp.service import parse_message_to_birth_profile, send_whatsapp_message

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
async def receive_whatsapp_message(request: Request, session=Depends(get_session)):
    data = await request.json()
    print("Incoming:", data)
    from_number = None
    response_text = ""

    try:
        change = data["entry"][0]["changes"][0]
        value = change["value"]

        msg = value["messages"][0]
        from_number = msg["from"]
        text = msg.get("text", {}).get("body", "")

        contact_name = value["contacts"][0]["profile"]["name"]

        # arse user text → BirthProfileCreate
        birth_profile = parse_message_to_birth_profile(text)

        # Save via BirthProfileService
        service = BirthProfileService(session)
        result = await service.set_birth_profile(birth_profile)

        # Send success message back
        response_text = f"✅ Profile saved for {contact_name} {birth_profile.name} with id {result.id}"
        send_whatsapp_message(from_number, response_text)

    except WhatsappError as e:
        print("Error:", e)
        # Friendly error for user
        if from_number:
            send_whatsapp_message(from_number, "⚠️ Sorry, could not process your message. Please use format:\n\nName, DOB (YYYY-MM-DD HH:MM), Place, Relationship")

    return {"status": f"received {response_text}"}