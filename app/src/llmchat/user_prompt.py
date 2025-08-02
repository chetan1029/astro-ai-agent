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

    Generate:
    1. Personality analysis (Lagna + Moon traits)
    2. Dasha Summary (focus of life now)
    3. Horoscope of key planets
    """


async def generate_user_horoscope_prompt(
    today_date: date,
    birth_profile: BirthProfileResponse,
    astro_profile: AstroProfileResponse,
) -> str:
    return f"""
    Today is {today_date}. Based on the following details, generate a daily horoscope focused on career, health, and relationships.

    Name: {birth_profile.name}
    Date of Birth: {birth_profile.date_of_birth}
    Birth Place: {birth_profile.birth_place}
    Ascendant Degree: {astro_profile.ascendant}
    Moon Nakshatra: {astro_profile.moon_nakshatra} (ruled by {astro_profile.nakshatra_ruler})
    Current Mahadasha: {astro_profile.nakshatra_ruler}

    Avoid specific transit predictions, just use Dasha influence and natal chart traits.
    """
