import os, requests
from datetime import datetime
from app.src.birthprofile.models import BirthProfileCreate, Relationship
from app.src.core.config import get_settings

ACCESS_TOKEN = get_settings().whatsapp_access_token
PHONE_NUMBER_ID = get_settings().whatsapp_phone_number_id


def send_whatsapp_message(to: str, message: str):
    """Send message back to user via WhatsApp Cloud API"""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("WhatsApp send response:", r.json())


def parse_message_to_birth_profile(text: str) -> BirthProfileCreate:
    """
    Parse a simple comma-separated message into BirthProfileCreate.
    Expected format:
    Name, YYYY-MM-DD HH:MM, City, Country, Relationship
    Example:
    Arjun Kumar, 1995-08-15 10:45, Delhi, India, Self
    """
    parts = [p.strip() for p in text.split(",")]
    if len(parts) < 4:
        raise ValueError("Invalid format")

    name = parts[0]
    dob = datetime.fromisoformat(parts[1])  # expects "YYYY-MM-DD HH:MM"
    place = parts[2]
    relationship = Relationship.self if len(parts) < 5 else Relationship(parts[4].lower())

    return BirthProfileCreate(
        name=name,
        date_of_birth=dob,
        birth_place=place,
        relationship=relationship
    )
