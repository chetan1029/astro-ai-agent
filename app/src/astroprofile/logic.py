import logging
from datetime import datetime
from typing import Dict, Any

import swisseph as swe

from app.src.core.constant import (
    NAKSHATRAS,
    NAKSHATRA_RULERS,
    VIMSHOTTARI_ORDER,
    VIMSHOTTARI_YEARS,
    ZODIAC_SIGNS,
)

logger = logging.getLogger(__name__)


class AstroProfileLogic:

    async def get_astro_profile(
        self,
        date_of_birth_utc: datetime,
        birth_place_latitude: float,
        birth_place_longitude: float,
    ) -> Dict[str, Any]:
        try:
            swe.set_ephe_path(None)

            jd = swe.julday(
                date_of_birth_utc.year,
                date_of_birth_utc.month,
                date_of_birth_utc.day,
                date_of_birth_utc.hour
                + date_of_birth_utc.minute / 60.0
                + date_of_birth_utc.second / 3600.0,
            )

            # Ayanamsa for sidereal calculation
            ayanamsa = swe.get_ayanamsa(jd)

            # Planet Positions
            planets = self._get_sidereal_planet_positions(jd, ayanamsa)

            # Ascendant and Houses
            ascendant, houses = self._get_lagna_and_houses(
                jd, birth_place_latitude, birth_place_longitude
            )

            # Nakshatra + Ruler
            moon_deg = planets["Moon"]
            nakshatra, ruler = self._get_nakshatra_and_ruler(moon_deg)

            # Vimshottari Dasha (basic placeholder — expand later)
            dasha_periods = self._get_dasha_periods(moon_deg, date_of_birth_utc)

            return {
                "planet_positions": planets,
                "ascendant": round(ascendant, 2),
                "houses": houses,
                "moon_nakshatra": nakshatra,
                "nakshatra_ruler": ruler,
                "vimshottari_dasha": dasha_periods,
            }
        except Exception as e:
            logger.exception("Error generating astro profile")
            raise e

    @staticmethod
    def _get_sidereal_planet_positions(jd: float, ayanamsa: float) -> Dict[str, float]:
        planet_names = [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Rahu",
            "Ketu",
        ]
        planet_codes = [
            swe.SUN,
            swe.MOON,
            swe.MARS,
            swe.MERCURY,
            swe.JUPITER,
            swe.VENUS,
            swe.SATURN,
            swe.TRUE_NODE,
            swe.TRUE_NODE,
        ]

        positions = {}
        for name, code in zip(planet_names, planet_codes):
            lon_tuple, _ = swe.calc_ut(jd, code)
            lon = lon_tuple[0]
            if name == "Ketu":
                lon = (lon + 180.0) % 360
            sidereal_lon = (lon - ayanamsa) % 360
            positions[name] = round(sidereal_lon, 6)

        return positions

    @staticmethod
    def _degree_to_sign(degree: float) -> str:
        sign_index = int(degree // 30) % 12
        deg_in_sign = degree % 30
        return f"{round(deg_in_sign, 2)}° {ZODIAC_SIGNS[sign_index]}"

    @staticmethod
    def _get_lagna_and_houses(jd: float, lat: float, lon: float) -> tuple[float, list]:
        try:
            # 'W' → Whole Sign, 'P' → Placidus (use 'W' for Vedic)
            asc, house_deg = swe.houses(jd, lat, lon, b"W")

            formatted_houses = [
                {
                    "house": i + 1,
                    "starts_at": AstroProfileLogic._degree_to_sign(house_deg),
                }
                for i, house_deg in enumerate(house_deg)
            ]

            return asc[0], formatted_houses
        except Exception as e:
            logger.exception("Error calculating ascendant/houses")
            raise ValueError("Could not compute houses. Check input data.") from e

    @staticmethod
    def _get_nakshatra_and_ruler(moon_deg: float) -> tuple[str, str]:
        index = int(moon_deg // (360 / 27))
        nakshatra = NAKSHATRAS[index]
        ruler = NAKSHATRA_RULERS[nakshatra]
        return nakshatra, ruler

    @staticmethod
    def _get_dasha_periods(moon_deg: float, dob: datetime) -> Dict[str, Any]:
        try:
            nak_index = int(moon_deg // (360 / 27))
            nak_start = nak_index * (360 / 27)
            nakshatra = NAKSHATRAS[nak_index]
            ruling_planet = NAKSHATRA_RULERS[nakshatra]

            # Get how far Moon is inside current Nakshatra (in degrees)
            degrees_into_nak = moon_deg - nak_start
            portion_completed = degrees_into_nak / (360 / 27)  # portion (0 to 1)

            total_dasha_years = VIMSHOTTARI_YEARS[ruling_planet]
            elapsed_years = portion_completed * total_dasha_years
            remaining_years = total_dasha_years - elapsed_years

            # Build Mahadasha timeline (starting from birth)
            start_index = VIMSHOTTARI_ORDER.index(ruling_planet)
            timeline = []
            start_date = dob

            for i in range(len(VIMSHOTTARI_ORDER)):
                planet = VIMSHOTTARI_ORDER[(start_index + i) % len(VIMSHOTTARI_ORDER)]
                dasha_years = VIMSHOTTARI_YEARS[planet]

                # Handle the first planet: subtract elapsed years
                if i == 0:
                    years = remaining_years
                else:
                    years = dasha_years

                end_date = start_date.replace(year=int(start_date.year + years))
                timeline.append(
                    {
                        "planet": planet,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "years": round(years, 2),
                    }
                )
                start_date = end_date

            return {
                "timeline": timeline,
            }
        except Exception as e:
            logger.exception("Error computing Dasha periods")
            raise ValueError("Could not compute Vimshottari Dasha periods.") from e
