from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: Optional[str] = None
    email: str
    name: str
    google_id: Optional[str] = None
    photo_url: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]

class UserResponse(UserBase):
    id: int
    photo_url: Optional[str] = None
    auth_provider: Optional[str] = "email"
    preferences: Optional[str] = "{}"
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class SearchRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: Optional[str] = None
    budget: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None

class PricePredictionResponse(BaseModel):
    indicator: str
    confidence: int
    explanation: str
    historical_trend: List[float]

class DelayPredictionResponse(BaseModel):
    airport_congestion: str
    weather_impact: str
    average_delay: float

class ExplanationDetailsResponse(BaseModel):
    why_selected: str
    pros: List[str] = []
    cons: List[str] = []
    trade_offs: str
    money_saved: float
    time_saved_mins: int

class ItineraryLegResponse(BaseModel):
    id: Optional[int] = None
    transport_type: str
    provider: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    duration: float
    delay_probability: float
    average_delay: float
    refundability: str
    seat_class: str
    carbon_footprint: float
    booking_link: Optional[str] = None
    hidden_costs: str

    model_config = ConfigDict(from_attributes=True)

class ItineraryResponse(BaseModel):
    id: Optional[int] = None
    type: str
    total_price: float
    total_duration: float
    carbon_footprint: float
    reliability_score: float
    delay_probability: float
    average_delay: float
    ai_explanation: Optional[str] = None
    legs: List[ItineraryLegResponse]
    is_saved: bool = False
    price_prediction: Optional[PricePredictionResponse] = None
    delay_prediction: Optional[DelayPredictionResponse] = None
    explanation_details: Optional[ExplanationDetailsResponse] = None

    model_config = ConfigDict(from_attributes=True)

class TripResponse(BaseModel):
    id: int
    origin: str
    destination: str
    start_date: str
    end_date: Optional[str] = None
    budget: Optional[float] = None
    status: str
    created_at: datetime
    itineraries: List[ItineraryResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    follow_ups: List[str] = []
    itineraries: List[ItineraryResponse] = []

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BudgetAnalysisRequest(BaseModel):
    total_budget: float
    origin: Optional[str] = "Kanpur"
    destination: Optional[str] = "Bangalore"
    stay_days: Optional[int] = 3
    current_plan_cost: Optional[float] = 43200.0
    lat: Optional[float] = None
    lng: Optional[float] = None

class BudgetAllocationItem(BaseModel):
    category: str
    amount: float
    percentage: float
    status: str
    reason: str

class SavingSuggestionItem(BaseModel):
    title: str
    savings: float
    category: str

class PaymentOptimizationItem(BaseModel):
    provider: str
    savings: float
    type: str

class HotelOptimizationItem(BaseModel):
    current_name: str
    current_price: float
    current_rating: str
    recommended_name: str
    recommended_price: float
    recommended_rating: str
    distance_difference: str
    savings_per_night: float

class DailyBudgetBreakdownItem(BaseModel):
    day: str
    amount: float
    highlights: str

class HiddenExpensesBreakdown(BaseModel):
    airport_tax: float
    seat_selection: float
    extra_baggage: float
    meals: float
    gst: float
    total_hidden_cost: float

class BudgetOptimizationResult(BaseModel):
    before_item: str
    before_cost: float
    after_item: str
    after_cost: float
    savings: float
    explanation: str

class ExactDestinationSchema(BaseModel):
    exact_name: str
    formatted_address: str
    lat: float
    lng: float
    city: str

class RecommendedHotelSchema(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    distance_km: str
    rating: str
    price_per_night: float
    total_stay_cost: float
    ai_reason: str
    booking_link: Optional[str] = ""

class RecommendedPlaceSchema(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lng: float
    distance_km: str
    estimated_cost: float
    visit_duration: str
    ai_reason: str

class RouteStopSchema(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lng: float
    distance_from_origin: str
    ai_reason: str

class AIBudgetAnalysisResponse(BaseModel):
    total_budget: float
    recommended_budget: float
    estimated_savings: float
    budget_health: str
    health_percentage: float
    ai_confidence: int
    ai_explanation: str
    allocations: List[BudgetAllocationItem]
    savings_suggestions: List[SavingSuggestionItem]
    potential_savings: float
    is_over_budget: bool
    extra_required: float
    over_budget_suggestions: List[SavingSuggestionItem]
    payment_optimizations: List[PaymentOptimizationItem]
    hotel_optimization: HotelOptimizationItem
    daily_breakdown: List[DailyBudgetBreakdownItem]
    hidden_expenses: HiddenExpensesBreakdown
    emergency_reserve: float
    current_plan_cost: float
    optimized_plan_cost: float
    total_plan_savings: float
    ai_score: int
    score_reasons: List[str]
    optimization_scenario_higher: str
    optimization_scenario_lower: str
    optimization_result: Optional[BudgetOptimizationResult] = None
    exact_destination: Optional[ExactDestinationSchema] = None
    ai_destination_summary: Optional[str] = ""
    recommended_hotels: List[RecommendedHotelSchema] = []
    places_to_visit: List[RecommendedPlaceSchema] = []
    route_stops: List[RouteStopSchema] = []


class AnalyticsResponse(BaseModel):
    money_saved: float
    hours_saved: float
    co2_saved: float
    favorite_airline: str
    favorite_transport: str
    trips_completed: int
    monthly_spending: List[Dict[str, Any]]


# AI Smart Explore Mode Schemas
class ExploreRequest(BaseModel):
    location: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    travel_dates: Optional[str] = None
    available_hours: Optional[float] = 6.0
    available_days: Optional[int] = 1
    budget: Optional[float] = 2000.0
    interests: List[str] = []
    preferences: Optional[Dict[str, Any]] = None

class ReplanRequest(BaseModel):
    current_itinerary: Dict[str, Any]
    skipped_stops: List[str] = []
    added_stops: List[str] = []
    updated_budget: Optional[float] = None
    updated_hours: Optional[float] = None
    updated_preferences: Optional[Dict[str, Any]] = None

class AttractionStop(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lng: float
    address: str
    visit_duration_mins: int
    estimated_cost: float
    travel_time_from_prev_mins: int
    travel_mode_from_prev: str
    scheduled_time: str
    ai_reasoning: str
    ai_score: int
    image_url: str
    description: str
    history_summary: str
    facts: List[str] = []
    architecture: str
    cultural_importance: str
    entry_fee: str
    opening_hours: str
    best_visiting_time: str
    photo_tips: str
    safety_tips: str
    accessibility: str
    nearby_amenities: Dict[str, Any] = {}
    spending_estimate: Dict[str, float] = {}

class EmergencyLocation(BaseModel):
    id: str
    name: str
    category: str
    lat: float
    lng: float
    address: str
    phone: str
    distance_km: float
    open_24h: bool = True

class ExploreMission(BaseModel):
    id: str
    title: str
    icon: str
    description: str
    trail_category: str
    estimated_hours: float
    estimated_cost: float
    recommended_stops_count: int

class ExploreItineraryResponse(BaseModel):
    location: str
    lat: float = 28.6139
    lng: float = 77.2090
    total_stops: int
    total_hours: float
    total_cost: float
    remaining_budget: float
    stops: List[AttractionStop]
    time_blocked_schedule: List[Dict[str, Any]]
    multi_transport_mix: List[str]
    hidden_gems: List[AttractionStop]
    photo_spots: List[Dict[str, Any]]
    food_recommendations: List[Dict[str, Any]]
    shopping_recommendations: List[Dict[str, Any]]
    waiting_for_api_credentials: bool = False
    api_credentials_message: Optional[str] = None
    road_polyline: List[List[float]] = []
    total_road_distance_km: float = 0.0
    total_road_duration_mins: int = 0
    eta: Optional[str] = None



