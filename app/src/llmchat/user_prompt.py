from datetime import date

from app.src.astroprofile.models import AstroProfileResponse
from app.src.birthprofile.models import BirthProfileResponse


async def generate_user_interpretation_prompt(
    birth_profile: BirthProfileResponse, astro_profile: AstroProfileResponse
) -> str:
    return f"""
    Name: {birth_profile.name}
    Date of Birth: {birth_profile.date_of_birth}
    Birthplace: {birth_profile.birth_place}
    Ascendant: {astro_profile.ascendant}°
    Moon Nakshatra: {astro_profile.moon_nakshatra} (ruled by {astro_profile.nakshatra_ruler})
    Current Mahadasha: {astro_profile.nakshatra_ruler}
    Planet Positions: {astro_profile.planet_positions}

    Please write:
    1. A simple explanation of personality
    2. What kind of energy or challenges the person is facing in life now
    3. Key advice for their health, career, and relationships
    4. One inspiring line about their future
    """


async def generate_user_horoscope_prompt(
    today_date: date,
    birth_profile: BirthProfileResponse,
    astro_profile: AstroProfileResponse,
) -> str:
    return f"""
    Today is {today_date}. Please generate a short, friendly daily horoscope for this user.

    Name: {birth_profile.name}
    Date of Birth: {birth_profile.date_of_birth}
    Birth Place: {birth_profile.birth_place}
    Ascendant Degree: {astro_profile.ascendant}
    Moon Nakshatra: {astro_profile.moon_nakshatra} (ruled by {astro_profile.nakshatra_ruler})
    Current Mahadasha: {astro_profile.nakshatra_ruler}

    Focus on how the user may feel or experience today in:
    - Career or money
    - Health and energy
    - Relationships or family

    Use soft and positive tone. Avoid technical astrology language.
    """
