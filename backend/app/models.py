import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    auth_provider = Column(String, default="email")
    preferences = Column(Text, default="{}") # JSON block for travel preferences
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_login = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    start_date = Column(String, nullable=False) # YYYY-MM-DD
    end_date = Column(String, nullable=True) # YYYY-MM-DD
    budget = Column(Float, nullable=True)
    status = Column(String, default="planning") # planning, booked, completed
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    type = Column(String, nullable=False) # e.g. "Best Overall", "Cheapest", "Fastest", "Lowest Risk", "Eco Friendly"
    total_price = Column(Float, nullable=False)
    total_duration = Column(Float, nullable=False) # in hours
    carbon_footprint = Column(Float, default=0.0) # in kg CO2
    reliability_score = Column(Float, default=100.0) # 0 to 100
    delay_probability = Column(Float, default=0.0) # percentage
    average_delay = Column(Float, default=0.0) # in minutes
    ai_explanation = Column(Text, nullable=True)
    is_saved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    trip = relationship("Trip", back_populates="itineraries")
    legs = relationship("ItineraryLeg", back_populates="itinerary", cascade="all, delete-orphan")

class ItineraryLeg(Base):
    __tablename__ = "itinerary_legs"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    transport_type = Column(String, nullable=False) # Flight, Train, Bus, Metro, Cab
    provider = Column(String, nullable=False) # e.g., Air India, IndiGo, Shatabdi, Uber
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(String, nullable=False) # ISO timestamp or HH:MM
    arrival_time = Column(String, nullable=False) # ISO timestamp or HH:MM
    price = Column(Float, nullable=False)
    duration = Column(Float, nullable=False) # in hours
    delay_probability = Column(Float, default=0.0)
    average_delay = Column(Float, default=0.0)
    refundability = Column(String, default="Non-refundable") # Refundable, Partial, Non-refundable
    seat_class = Column(String, default="Economy / Standard")
    carbon_footprint = Column(Float, default=0.0)
    booking_link = Column(String, nullable=True)
    hidden_costs = Column(Text, default="{}") # JSON breakdown (taxes, baggage, meals, airport transfers)

    itinerary = relationship("Itinerary", back_populates="legs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False) # price_drop, delay, gate_change, schedule
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="notifications")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="chats")
