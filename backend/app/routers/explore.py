from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List

from app.schemas import (
    ExploreRequest,
    ReplanRequest,
    ExploreItineraryResponse,
    EmergencyLocation,
    ExploreMission,
)
from app.services.smart_explore_service import SmartExploreService

router = APIRouter(prefix="/api/explore", tags=["AI Smart Explore Mode"])


@router.get("/status")
def get_api_credentials_status():
    """
    Check if required API credentials exist in environment.
    """
    return SmartExploreService.get_api_credentials_status()


@router.get("/missions", response_model=List[ExploreMission])
def get_explore_missions():
    """
    Get 12 preset 1-click sightseeing trail missions.
    """
    return SmartExploreService.get_explore_missions()


@router.get("/emergency", response_model=List[EmergencyLocation])
def get_emergency_facilities(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
):
    """
    Fetch 1-tap emergency facilities (Hospitals, Police, Pharmacies, ATMs, EV Charging, Embassies).
    """
    return SmartExploreService.get_emergency_facilities(lat, lng)


@router.post("/plan", response_model=ExploreItineraryResponse)
def plan_sightseeing_itinerary(req: ExploreRequest):
    """
    Generate optimized sightseeing itinerary using real constraints (Distance, Opening Hours, Budget, Traffic, Weather).
    If API keys are missing, cleanly returns 'Waiting for API Credentials.' status.
    """
    return SmartExploreService.plan_explore_itinerary(req.model_dump())


@router.post("/replan", response_model=ExploreItineraryResponse)
def replan_sightseeing_itinerary(req: ReplanRequest):
    """
    Dynamically recalculates sightseeing itinerary on skip, re-order, budget adjustment, or weather changes.
    """
    return SmartExploreService.replan_explore_itinerary(req.model_dump())


@router.get("/audio-guide/{attraction_id}")
def get_audio_guide_script(
    attraction_id: str,
    name: Optional[str] = Query("Heritage Attraction", description="Attraction name"),
):
    """
    Fetch AI Voice Tour Guide transcript, photography advice, and voice audio status.
    """
    return SmartExploreService.get_audio_guide_script(attraction_id, name)


@router.get("/tts")
def get_tts_audio(text: str = Query("Welcome to Travel Copilot", description="Text to speak")):
    """
    Stream ElevenLabs / Web TTS audio MP3 bytes.
    """
    audio_bytes = SmartExploreService.generate_tts_audio(text)
    if audio_bytes:
        return Response(content=audio_bytes, media_type="audio/mpeg")
    raise HTTPException(status_code=400, detail="ElevenLabs API key missing or unavailable")
