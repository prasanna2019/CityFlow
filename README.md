# 🌆 VibeCity: Urban Intelligence Platform

A high-performance **FastAPI** application that correlates real-time atmospheric data with local event streams to provide personalized "City Vibe" recommendations.

## 🚀 Overview

VibeCity is designed to solve the "What should I do today?" problem by merging **Weather API** data with **Sports Event** schedules. It provides users with actionable insights based on the current environment—suggesting outdoor matches on sunny days or indoor fan-zones during monsoon.

### Key Features
- **Real-time Weather Sync**: Integrated with OpenWeather/AccuWeather for live urban conditions.
- **Sports Event Ingestion**: Streams upcoming matches and stadium events using external providers.
- **Intelligent Logic**: Dynamic recommendation engine that filters activities based on weather severity.
- **Async Architecture**: Built with `httpx` and `FastAPI` lifespan management for maximum concurrency.

---

## 🛠 Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI |
| **Data Fetching** | HTTPX (Async Client with Connection Pooling) |
| **Validation** | Pydantic v2 |
| **Deployment** | Docker, Google Cloud Run |
| **Database** | SQLAlchemy 2.0 (PostgreSQL) |

---

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- API Keys for Weather and Sports providers
