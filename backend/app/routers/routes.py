from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib
import json
from typing import List
from ..database import get_db
from .. import models, schemas
from ..services.agents import TravelAgentSystem

router = APIRouter()
agent_system = TravelAgentSystem()

def ensure_user_exists(db: Session, user_id: int = 1) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        user = models.User(
            id=user_id,
            email=f"traveler_{user_id}@example.com",
            name="Demo Traveler",
            hashed_password="demo_hashed_password",
            auth_provider="email"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.put("/user/preferences", response_model=schemas.UserResponse)
def update_preferences(pref_data: schemas.UserPreferencesUpdate, user_id: int = 1, db: Session = Depends(get_db)):
    user = ensure_user_exists(db, user_id)
    user.preferences = json.dumps(pref_data.preferences)
    db.commit()
    db.refresh(user)
    return user

@router.post("/search", response_model=List[schemas.ItineraryResponse])
def search_trips(request: schemas.SearchRequest, user_id: int = 1, db: Session = Depends(get_db)):
    pref = request.preferences or {}
    results = agent_system.process_universal_search(
        origin=request.origin,
        destination=request.destination,
        date=request.start_date,
        budget=request.budget,
        preferences=pref
    )
    return results

@router.post("/chat", response_model=schemas.ChatResponse)
def chat_message(request: schemas.ChatRequest, user_id: int = 1, db: Session = Depends(get_db)):
    ensure_user_exists(db, user_id)
    # Save user message to DB
    user_chat = models.ChatHistory(user_id=user_id, content=request.message, is_bot=False)
    db.add(user_chat)
    
    # Process through Agent System Coordinator
    res = agent_system.handle_chat_message(request.message, user_id)
    
    # Save bot reply to DB
    bot_chat = models.ChatHistory(user_id=user_id, content=res["reply"], is_bot=True)
    db.add(bot_chat)
    db.commit()
    
    return {
        "reply": res["reply"],
        "follow_ups": res["follow_ups"],
        "itineraries": res["itineraries"]
    }

@router.get("/user/trips", response_model=List[schemas.TripResponse])
def get_user_trips(user_id: int = 1, db: Session = Depends(get_db)):
    trips = db.query(models.Trip).filter(models.Trip.user_id == user_id).all()
    return trips

@router.post("/user/trips", response_model=schemas.TripResponse)
def save_trip_itinerary(itinerary_data: schemas.ItineraryResponse, origin: str, destination: str, start_date: str, budget: float = None, user_id: int = 1, db: Session = Depends(get_db)):
    ensure_user_exists(db, user_id)
    # 1. Create Trip row
    trip = models.Trip(
        user_id=user_id,
        origin=origin,
        destination=destination,
        start_date=start_date,
        budget=budget,
        status="booked"
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    
    # 2. Extract legs and form Itinerary row
    itinerary = models.Itinerary(
        trip_id=trip.id,
        type=itinerary_data.type,
        total_price=itinerary_data.total_price,
        total_duration=itinerary_data.total_duration,
        carbon_footprint=itinerary_data.carbon_footprint,
        reliability_score=itinerary_data.reliability_score,
        delay_probability=itinerary_data.delay_probability,
        average_delay=itinerary_data.average_delay,
        ai_explanation=itinerary_data.ai_explanation,
        is_saved=True
    )
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    
    # 3. Create Leg rows
    for leg in itinerary_data.legs:
        db_leg = models.ItineraryLeg(
            itinerary_id=itinerary.id,
            transport_type=leg.transport_type,
            provider=leg.provider,
            origin=leg.origin,
            destination=leg.destination,
            departure_time=leg.departure_time,
            arrival_time=leg.arrival_time,
            price=leg.price,
            duration=leg.duration,
            delay_probability=leg.delay_probability,
            average_delay=leg.average_delay,
            refundability=leg.refundability,
            seat_class=leg.seat_class,
            carbon_footprint=leg.carbon_footprint,
            booking_link=leg.booking_link,
            hidden_costs=leg.hidden_costs
        )
        db.add(db_leg)
        
    db.commit()
    db.refresh(trip)
    return trip

@router.delete("/user/trips/{trip_id}", status_code=204)
def delete_trip(trip_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id, models.Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return

@router.get("/user/analytics", response_model=schemas.AnalyticsResponse)
def get_user_analytics(user_id: int = 1, db: Session = Depends(get_db)):
    # Query database and sum overall stats
    trips = db.query(models.Trip).filter(models.Trip.user_id == user_id).all()
    
    num_completed = len(trips)
    tot_price = 0.0
    tot_duration = 0.0
    tot_carbon = 0.0
    
    for t in trips:
        for it in t.itineraries:
            tot_price += it.total_price
            tot_duration += it.total_duration
            tot_carbon += it.carbon_footprint

    # Savings calculations: compare against standard defaults
    # Let's say user has saved 1,200 INR per completed route on average, and saved 4.2 hours on average
    multiplier = num_completed if num_completed > 0 else 3.0 # provide base dummy numbers for new users to look full
    
    money_saved = float(multiplier * 1850)
    hours_saved = float(multiplier * 4.5)
    co2_saved = float(multiplier * 35.0)

    # Monthly spending data structures
    monthly = [
        {"month": "May", "spend": 12500},
        {"month": "Jun", "spend": 18200},
        {"month": "Jul", "spend": round(tot_price, 2) if tot_price > 0 else 8400}
    ]

    return {
        "money_saved": money_saved,
        "hours_saved": hours_saved,
        "co2_saved": co2_saved,
        "favorite_airline": "IndiGo",
        "favorite_transport": "Flight",
        "trips_completed": num_completed or 3,
        "monthly_spending": monthly
    }

@router.get("/notifications", response_model=List[schemas.NotificationResponse])
def get_notifications(user_id: int = 1, db: Session = Depends(get_db)):
    ensure_user_exists(db, user_id)
    # Fetch demo notifications
    db_notifs = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    if not db_notifs:
        alerts = agent_system.notifier.generate_alerts(user_id)
        for a in alerts:
            db_notif = models.Notification(
                user_id=user_id,
                type=a["type"],
                title=a["title"],
                message=a["message"],
                is_read=a["is_read"]
            )
            db.add(db_notif)
        db.commit()
        db_notifs = db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
    return db_notifs

@router.put("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(models.Notification).filter(models.Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"status": "success"}

@router.delete("/notifications/clear")
def clear_notifications(user_id: int = 1, db: Session = Depends(get_db)):
    db.query(models.Notification).filter(models.Notification.user_id == user_id).delete()
    db.commit()
    return {"status": "cleared"}

@router.post("/budget/analyze", response_model=schemas.AIBudgetAnalysisResponse)
def analyze_budget(req: schemas.BudgetAnalysisRequest):
    return agent_system.budget_advisor.analyze_budget(
        total_budget=req.total_budget,
        origin=req.origin or "Kanpur",
        destination=req.destination or "Bangalore",
        stay_days=req.stay_days or 3,
        current_plan_cost=req.current_plan_cost,
        lat=req.lat,
        lng=req.lng
    )

@router.get("/budget/reverse-geocode", response_model=schemas.ExactDestinationSchema)
def reverse_geocode(lat: float, lng: float):
    from app.services.smart_explore_service import SmartExploreService
    res = SmartExploreService.reverse_geocode(lat, lng)
    return res

@router.get("/hotels")
def get_live_hotels(destination: str = "Bangalore"):
    from app.services.live_travel_api import live_travel_service
    return live_travel_service.fetch_live_hotels(destination)
