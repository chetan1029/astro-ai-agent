from datetime import datetime

from app.src.birthprofile.models import Relationship, BirthProfileCreate


def parse_message_to_birth_profile(text: str) -> BirthProfileCreate:
    """
    Parse a simple comma-separated message into BirthProfileCreate.
    Expected format:
    Name, YYYY-MM-DD HH:MM, City, Country, Relationship
    Example:
    Arjun Kumar, 1995-08-15 10:45, Delhi, India, Self
    """
    print(text)
    parts = [p.strip() for p in text.split(",")]
    print(parts)
    if len(parts) < 4:
        raise ValueError("Invalid format")

    name = parts[0]
    dob = datetime.fromisoformat(parts[1])  # expects "YYYY-MM-DD HH:MM"
    place = parts[2]
    relationship = (
        Relationship.self if len(parts) < 5 else Relationship(parts[4].lower())
    )

    return BirthProfileCreate(
        name=name, date_of_birth=dob, birth_place=place, relationship=relationship
    )
