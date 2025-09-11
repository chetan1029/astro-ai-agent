from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.src.birthprofile.exceptions import BirthProfileAlreadyExistsError, DataStoreError
from app.src.core.db import get_session
from app.src.whatsapp.dependencies import get_messaging_provider
from app.src.whatsapp.providers.base import MessagingProvider
from app.src.whatsapp.service import WhatsAppService
from app.src.core.config import get_settings

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if (
        hub_mode == "subscribe"
        and hub_verify_token == get_settings().whatsapp_verify_token
    ):
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Verification failed", status_code=403)


@router.post("/webhook")
async def receive_whatsapp_message(
    request: Request,
    session=Depends(get_session),
    messaging: MessagingProvider = Depends(get_messaging_provider),
):
    provider = get_settings().whatsapp_provider

    # Handle Twilio (form-data) vs Cloud API (json)
    if provider == "twilio":
        form = await request.form()
        data = dict(form)
    else:
        data = await request.json()

    print("Incoming:", data)
    try:
        from_number, text, contact_name = messaging.parse_incoming(data)
        response_text = await WhatsAppService(session, messaging).handle_incoming_message(
            from_number, text, contact_name
        )
        return {"status": f"received {response_text}"}
    except BirthProfileAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DataStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        return {"status": f"Error: {e}"}
