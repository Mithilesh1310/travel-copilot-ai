<div align="center">

# 🤖 AI Travel Copilot (Travel-Copilot-AI)
### *Next-Gen Multi-Agent Travel Routing, Hyper-Local Cab Fare Engine & Financial Travel Advisor*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-Web%20%7C%20Android%20%7C%20iOS-02569B.svg?logo=flutter&logoColor=white)](https://flutter.dev)
[![Gemini AI](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-8E75B2.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![SerpApi](https://img.shields.io/badge/Google%20Hotels-SerpApi-FF7043.svg)](https://serpapi.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

<p align="center">
  <b>An AI-powered autonomous travel copilot that calculates multi-modal routes (Flights, Trains, Buses, Metro, Cabs), predicts delay risks, calculates hyper-local cab fares, optimizes travel budgets, and facilitates live hotel bookings.</b>
</p>

</div>

---

## 🌟 Key Features

### 🧠 1. Multi-Agent Graph Routing Engine
- **Dijkstra Multi-Modal Pathfinding**: Combines **Flights**, **Express Trains (Vande Bharat, Shatabdi)**, **Intercity Buses (UPSRTC, Zingbus)**, **Metro**, and **Local Cabs** to construct the optimal trip.
- **Preference Optimization**: Toggle optimization modes instantly:
  - 💰 *Cheapest Route*
  - ⚡ *Fastest Non-Stop Route*
  - 🌿 *Eco-Friendly / Low-Carbon Transit*
  - 🛡️ *Lowest Delay Risk*
  - ⚖️ *Best Value (Hybrid)*

---

### 📍 2. Hyper-Local Exact Location & Real Cab Fare Engine
- **Exact Landmark Recognition**: Recognizes sub-locations such as **`PSIT Kanpur (Pranveer Singh Institute of Technology, Bhaunti)`**, **`IIT Kanpur`**, **`Janakpuri Delhi`**, **`Whitefield Bangalore`**, and **`Electronic City`**.
- **Real-Time Fare Calculations**:
  - 🚗 **Uber Go / Ola Mini**: Base ₹50 + ₹16/km (e.g., PSIT Kanpur ➔ Kanpur Central CNB = **₹402** for 22 km).
  - 🛺 **Uber Auto / Ola Auto**: Base ₹30 + ₹12/km (e.g., PSIT Kanpur ➔ Kanpur Central CNB = **₹294**).
  - 🚕 **Uber Intercity / Outstation Cab**: Base ₹150 + ₹14/km (e.g., PSIT Kanpur ➔ Lucknow Airport LKO = **₹1,382** for 88 km via NH19).
- **Direct Booking Deep-Links**: Pre-fills exact pickup coordinates with one-click **`[ 🚗 Book Uber Cab ]`** buttons.

---

### 💰 3. AI Financial Travel Advisor & Budget Optimizer
- **Intelligent Budget Analysis**:
  - Analyzes total budget, stay duration, and destination tariffs to provide an **AI Health Rating** (*Excellent*, *Moderate*, *Tight*).
  - Calculates **Recommended Budget** & **Estimated Savings**.
- **Day-Wise Expense Allocation**: Dynamic daily breakdown (Arrival ➔ Sightseeing ➔ Souvenir Shopping & Checkout).
- **Hotel Nightly Rate Optimization**: Compares hotel options within 400m radius to save up to **₹1,800/night**.
- **Hidden Cost Breakdown**: Transparently details airport taxes, extra baggage fees, seat selection, and GST.

---

### 🏨 4. Live Hotel Booking Hub
- **SerpApi Google Hotels Integration**: Queries live verified hotels with real-time room tariffs in **INR**, star ratings, and location metrics.
- **Instant Room Booking**: Embedded modal system for browsing destination hotels and redirecting to official partner booking portals.

---

### 🔐 5. Production Authentication System
- **Real SQLite Database Storage**: Users, Trips, Itineraries, Notifications, and Chat History managed via SQLAlchemy.
- **Security**: Password hashing with **SHA-256 & Salt**, JWT Access Tokens (30-day expiry).
- **OAuth Integration**: Supports **Google Sign-In** with automated profile creation.

---

### 🗺️ 6. AI Sightseeing & Explore Engine (Real Road Navigation & In-App Voice Guidance)
- **OSRM Real Road Navigation Routes**: Replaces straight displacement lines with actual street-level road-following polylines (`#4285F4` double-stroke blue lines with camera auto-bounds fitting).
- **1-Click Sightseeing Mission Trails**: Instant 1-click trail generation (*History & Heritage Trail*, *Street Food & Flavors*, *Photography & Golden Hour*, *Shopping & Local Bazaars*).
- **Authentic Landmark Photographs**: Displays verified photos matching Google Maps & Wikipedia Commons for all destinations (Jama Masjid, Red Fort, Lodhi Gardens, Chandni Chowk, Qutub Minar, Gateway of India, Taj Mahal, Eiffel Tower, etc.) with skeleton loaders and error fallbacks.
- **In-App Turn-By-Turn Live Navigation**:
  - Green Google Maps direction banner (*"In 250m, Turn Right onto Main Entrance Road"*).
  - Distance remaining (`1.2 km`) and drive ETA (`4 mins`).
  - **Voice Guidance Assistant**: Speaks turn instructions aloud using HTML5 Web Speech Synthesis API.
  - Close-up tracking camera (`zoom: 16.5`) with **Next Stop** and **Exit Nav** controls.
- **Emergency Facilities Overlay**: One-tap toggle displaying nearby Hospitals, Police Stations, and Pharmacies with instant dialing.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend App** | `Flutter (Dart)` | Responsive Web & Mobile Dashboard with Material 3 Dark Glassmorphic Design |
| **Backend Service** | `FastAPI (Python 3.11+)` | High-performance async REST API with auto-generated OpenAPI OpenAPI docs |
| **AI Intelligence** | `Google Gemini 2.0 Flash` | Autonomous multi-agent reasoning, plan explanations, and natural language copilot |
| **Graph Routing** | `Dijkstra Algorithm` | Dynamic graph generation with weighted node costs (price, duration, carbon, risk) |
| **Database** | `SQLite / SQLAlchemy ORM` | Persistent storage for users, trip records, and system notifications |
| **External APIs** | `SerpApi`, `AviationStack`, `OpenWeather` | Live Google Flights, Google Hotels, real-time flight status, and weather forecasts |

---

## 📁 Repository Structure

```text
travel-copilot-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Application Entrypoint
│   │   ├── database.py              # SQLite Database Configuration
│   │   ├── models.py                # SQLAlchemy Models (User, Trip, Notification, etc.)
│   │   ├── schemas.py               # Pydantic Schemas & Request/Response Models
│   │   ├── routers/
│   │   │   ├── routes.py            # Search, Chat, Itinerary, Budget & Hotel Endpoints
│   │   │   └── auth.py              # Authentication (Register, Login, Google OAuth)
│   │   └── services/
│   │       ├── agents.py            # TravelAgentSystem & AI Copilot Logic
│   │       ├── routing_engine.py    # Dijkstra Graph Engine & Hyper-Local Cab Calculator
│   │       └── live_travel_api.py   # SerpApi Google Flights/Hotels & Weather Integration
│   ├── tests/
│   │   └── test_api.py              # Comprehensive Pytest Suite (100% Passed)
│   └── requirements.txt             # Python Package Dependencies
│
├── frontend/
│   ├── lib/
│   │   ├── main.dart                # Main Flutter App Dashboard & Auth Gate Screen
│   │   ├── models/
│   │   │   └── travel_models.dart   # Dart Data Models (Itinerary, BudgetReport, HotelItem)
│   │   └── services/
│   │       └── api_service.dart     # HTTP Service communicating with FastAPI Backend
│   ├── test/
│   │   └── widget_test.dart         # Flutter Unit & Widget Test Suite (100% Passed)
│   └── pubspec.yaml                 # Flutter App Configuration & Assets
└── README.md                        # Project Documentation
```

---

## ⚡ Quick Start Guide

### Prerequisites
- **Python 3.11+** installed
- **Flutter SDK (3.24+)** installed
- **Git**

---

### 1. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API Keys (Optional, fallback provided)
# GEMINI_API_KEY=your_gemini_key
# SERPAPI_API_KEY=your_serpapi_key

# Run FastAPI Server
uvicorn app.main:app --reload --port 8000
```
> 🌐 Backend API will be live at: `http://localhost:8000`  
> 📑 Interactive Swagger Docs at: `http://localhost:8000/docs`

---

### 2. Frontend Setup (Flutter Web / Mobile)

```bash
# Navigate to frontend directory
cd frontend

# Get Flutter packages
flutter pub get

# Run Flutter Web Application
flutter run -d chrome

# Or build production release web bundle
flutter build web --release
```
> 📱 Web Application will open live at: `http://localhost:8080`

---

## 🧪 Testing & Verification

Run the full automated test suites to ensure 100% code quality:

```bash
# Backend Test Suite (Pytest)
cd backend
python -m pytest tests/

# Frontend Test Suite (Flutter Test)
cd frontend
flutter test
```

---

## 🔌 Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Create a new user account with hashed password |
| `POST` | `/api/auth/login` | Authenticate user & return JWT token |
| `POST` | `/api/auth/google` | Google OAuth authentication & user registration |
| `POST` | `/api/search` | Search optimal travel itineraries using Dijkstra engine |
| `POST` | `/api/chat` | AI Copilot conversational assistant with exact cab fares |
| `POST` | `/api/budget/analyze` | AI Financial Advisor budget optimization report |
| `POST` | `/api/explore/plan` | Plan AI Sightseeing itinerary with OSRM real road polylines |
| `GET` | `/api/explore/missions` | Fetch 1-click curated sightseeing mission trails |
| `GET` | `/api/explore/audio-guide/{id}` | Generate AI Voice Guide script for attraction stops |
| `GET` | `/api/hotels` | Fetch live hotels in target destination via SerpApi |
| `GET` | `/api/notifications` | Get real-time delay & weather notifications |
| `GET` | `/api/user/analytics` | Retrieve cumulative savings & travel statistics |

---

## 📄 License
Distributed under the **MIT License**. See `LICENSE` for details.

---

<div align="center">
  <sub>Built with ❤️ by <b><a href="https://github.com/Mithilesh1310">Mithilesh Sahni</a></b></sub>
</div>
