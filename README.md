# Astro AI Agent

Astro AI Agent is a FastAPI-based microservice that generates astrological profiles based on user birth information. It leverages planetary data and geolocation APIs to calculate ascendants, nakshatras, Vimshottari Dasha, and more. Built with Python, SQLModel, and PostgreSQL, it is containerized for Kubernetes deployment.

---

## 🚀 Features

- Create and manage **Birth Profiles** with location and time normalization
- Calculate **Astro Profiles** (Ascendant, Nakshatra, Vimshottari Dasha, etc.)
- Generate **Personality Interpretation**, **Horoscope**.
- Robust input validation and timezone handling
- Supports **PostgreSQL** in production
- Async architecture using **FastAPI**, **SQLModel**, and **httpx**
- Full test suite using **pytest** and **testcontainers**
- Deployable via Docker and Kubernetes

---

## 📦 Tech Stack

- **Backend**: FastAPI, SQLModel, Pydantic
- **Database**: PostgreSQL
- **LLM Model**: AnyLLM with OpenAi support
- **Testing**: Pytest, Testcontainers, httpx
- **DevOps**: Docker, Kubernetes, Skaffold
- **Others**: Geocoding APIs for lat/long, timezone conversion

---

## 📦 Upcoming
- **MCP Server**
- **Chat-Engine**
---

## 📂 To run project on localhost 
- **run**: skaffold dev

