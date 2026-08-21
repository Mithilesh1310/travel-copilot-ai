import os
import json
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from .routing_engine import find_routes_dijkstra, RouterEdge
from .live_travel_api import live_travel_service

def parse_date_from_text(msg: str) -> str:
    """
    Parses date mentioned in user message (e.g. 'tomorrow', 'today', '20 August', '15-08-2026', '2026-08-20').
    Defaults to today's date if no date is specified.
    """
    today = datetime.now()
    msg_lower = msg.lower()
    
    if "tomorrow" in msg_lower or "kal" in msg_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "day after tomorrow" in msg_lower or "parso" in msg_lower:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    elif "next week" in msg_lower:
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Regex match YYYY-MM-DD
    match_iso = re.search(r'\b(202[4-9])-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b', msg)
    if match_iso:
        return match_iso.group(0)

    # Regex match DD/MM/YYYY or DD-MM-YYYY
    match_dmy = re.search(r'\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](202[4-9])\b', msg)
    if match_dmy:
        d, m, y = match_dmy.groups()
        return f"{y}-{m}-{d}"
        
    # Match month names e.g. "20 august", "25 aug", "15 sept"
    months = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }
    for month_name, month_num in months.items():
        match_mon = re.search(r'\b(\d{1,2})\s*(st|nd|rd|th)?\s*' + month_name + r'\b|\b' + month_name + r'\s*(\d{1,2})\b', msg_lower)
        if match_mon:
            day = int(match_mon.group(1) or match_mon.group(3))
            year = today.year if (month_num > today.month or (month_num == today.month and day >= today.day)) else today.year + 1
            return f"{year}-{month_num:02d}-{day:02d}"

    return today.strftime("%Y-%m-%d")

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def call_gemini_api(prompt: str, system_instruction: str = "", response_json: bool = False) -> str:
    """
    Calls Google Gemini API using active models (gemini-2.0-flash, gemini-2.0-flash-lite, gemini-1.5-flash).
    Supports official google-genai SDK with an HTTP REST fallback.
    """
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = raw_key.strip()
    if not api_key:
        return ""
        
    candidate_models = [
        os.environ.get("GEMINI_MODEL", "").strip() or "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash"
    ]
    # Remove duplicates while preserving order
    models_to_try = []
    for m in candidate_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    # Method 1: Try official google-genai SDK
    try:
        from google import genai
        
        client = genai.Client(api_key=api_key)
        config_kwargs = {}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if response_json:
            config_kwargs["response_mime_type"] = "application/json"
            
        gen_config = genai.types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        
        for model in models_to_try:
            try:
                res = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=gen_config
                )
                if res and res.text:
                    return res.text.strip()
            except Exception:
                continue
    except Exception:
        pass

    # Method 2: Fallback direct HTTP REST API request to Gemini endpoint
    try:
        import requests
        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload: Dict[str, Any] = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
                if response_json:
                    payload["generationConfig"] = {"responseMimeType": "application/json"}
                    
                resp = requests.post(url, json=payload, timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                continue
    except Exception:
        pass

    return ""


class PlannerAgent:
    """
    Parses natural language requests to determine intent type (search vs conversation)
    and extracts travel parameters using Gemini AI, with smart heuristic fallback.
    """
    def parse_intent(self, message: str) -> Dict[str, Any]:
        msg = message.strip()
        msg_lower = msg.lower()

        # Check for simple greetings or general non-search queries
        greetings = {"hi", "hello", "hey", "hlo", "hola", "namaste", "who are you", "what can you do", "help", "thanks", "thank you", "good morning", "good evening"}
        words = [w.strip(".,!?") for w in msg_lower.split()]
        
        # If query is short greeting or explicitly general question without route keywords
        has_route_keyword = any(k in msg_lower for k in ["from", " to ", "flight", "train", "bus", "cab", "ticket", "route", "travel", "budget", "cheapest", "fastest", "₹", "rs", "inr"])
        
        if (msg_lower in greetings or (len(words) <= 3 and not has_route_keyword)) and not ("from" in words and "to" in words):
            return {
                "is_search_intent": False,
                "message": msg
            }

        # Attempt Gemini AI Intent Parsing for route queries
        today_str = datetime.now().strftime("%Y-%m-%d")
        if os.environ.get("GEMINI_API_KEY", "").strip():
            system_prompt = (
                f"Today's date is {today_str}. You are an AI Travel Copilot Intent Parser. "
                "Determine if the user wants to search for a travel route. "
                "If it's a general question or greeting, return JSON: {\"is_search_intent\": false}. "
                "If it is a route query, return JSON: {\"is_search_intent\": true, \"origin\": string, \"destination\": string, "
                "\"start_date\": string, \"budget\": number or null, \"preferences\": {\"optimize_by\": string, \"non_stop\": boolean, \"refundable\": boolean, \"eco_friendly\": boolean}}. "
                "If user specifies a date like 'tomorrow', 'next Monday', '20 August', calculate exact YYYY-MM-DD from today's date. If no date specified, set start_date to today's date."
            )
            gemini_res = call_gemini_api(msg, system_instruction=system_prompt, response_json=True)
            if gemini_res:
                try:
                    data = json.loads(gemini_res)
                    if data.get("is_search_intent") is False:
                        return {"is_search_intent": False, "message": msg}
                    if data.get("origin") and data.get("destination"):
                        pref = data.get("preferences", {})
                        if "optimize_by" not in pref:
                            pref["optimize_by"] = "best_value"
                        return {
                            "is_search_intent": True,
                            "origin": str(data["origin"]).title(),
                            "destination": str(data["destination"]).title(),
                            "start_date": data.get("start_date") or parse_date_from_text(msg),
                            "budget": float(data["budget"]) if data.get("budget") else None,
                            "preferences": pref
                        }
                except Exception:
                    pass

        # Heuristic Rule-Based Intent Extraction
        INVALID_CITY_WORDS = {
            "want", "go", "to", "from", "for", "with", "flight", "flights", "train", "trains",
            "bus", "buses", "cab", "cabs", "taxi", "route", "routes", "travel", "ticket",
            "cheap", "cheapest", "fast", "fastest", "best", "eco", "green", "time", "enough",
            "just", "have", "need", "please", "find", "show", "get", "reach", "visit", "trip",
            "search", "book", "buy", "check", "i", "you", "he", "she", "it", "we", "they", "me",
            "my", "our", "a", "an", "the", "under", "below", "above", "rs", "inr", "budget", "day"
        }

        CITY_ALIASES = {
            "kanpur": "Kanpur",
            "banglore": "Bangalore",
            "bangalore": "Bangalore",
            "bengaluru": "Bangalore",
            "delhi": "Delhi",
            "new delhi": "Delhi",
            "mumbai": "Mumbai",
            "bombay": "Mumbai",
            "london": "London",
            "paris": "Paris",
            "new york": "New York",
            "nyc": "New York",
            "tokyo": "Tokyo",
            "dubai": "Dubai",
            "singapore": "Singapore",
            "jaipur": "Jaipur",
            "goa": "Goa",
            "agra": "Agra",
            "varanasi": "Varanasi",
            "banaras": "Varanasi",
            "lucknow": "Lucknow",
            "kolkata": "Kolkata",
            "calcutta": "Kolkata",
            "chennai": "Chennai",
            "hyderabad": "Hyderabad",
            "pune": "Pune",
            "ahmedabad": "Ahmedabad",
        }

        found_cities_in_order = []
        for token in words:
            for city_key, clean_city in CITY_ALIASES.items():
                if token == city_key or city_key in token:
                    if not found_cities_in_order or found_cities_in_order[-1] != clean_city:
                        found_cities_in_order.append(clean_city)

        origin = None
        destination = None

        if "from" in words:
            try:
                from_idx = words.index("from")
                for i in range(from_idx + 1, min(from_idx + 4, len(words))):
                    w = words[i].lower()
                    if w not in INVALID_CITY_WORDS and len(w) >= 3:
                        origin = CITY_ALIASES.get(w, words[i].title())
                        break
            except Exception:
                pass

        if "to" in words:
            try:
                for to_idx in [idx for idx, w in enumerate(words) if w == "to"]:
                    if to_idx < len(words) - 1:
                        next_word = words[to_idx + 1].lower()
                        if next_word in ["go", "travel", "fly", "visit", "reach"]:
                            if to_idx + 2 < len(words):
                                target_word = words[to_idx + 2].lower()
                                if target_word not in INVALID_CITY_WORDS and len(target_word) >= 3:
                                    destination = CITY_ALIASES.get(target_word, words[to_idx + 2].title())
                        elif next_word not in INVALID_CITY_WORDS and len(next_word) >= 3:
                            destination = CITY_ALIASES.get(next_word, words[to_idx + 1].title())
            except Exception:
                pass

        if not origin and len(found_cities_in_order) >= 1:
            if "from" in msg_lower:
                for c in found_cities_in_order:
                    if f"from {c.lower()}" in msg_lower or f"from {c.lower()[:4]}" in msg_lower:
                        origin = c
                        break
            if not origin:
                origin = found_cities_in_order[0]

        if not destination and len(found_cities_in_order) >= 1:
            for c in found_cities_in_order:
                if c != origin:
                    destination = c
                    break

        # Safety check: Origin and Destination can NEVER be stop words
        if origin and origin.lower() in INVALID_CITY_WORDS:
            origin = None
        if destination and destination.lower() in INVALID_CITY_WORDS:
            destination = None

        budget = None
        for arg in ["budget", "rs", "₹", "inr"]:
            if arg in msg_lower:
                try:
                    parts = msg_lower.split(arg)
                    num_str = "".join([c for c in parts[1].split()[0] if c.isdigit()])
                    if num_str:
                        budget = float(num_str)
                except Exception:
                    pass

        # If after heuristic parsing we still have no valid origin and destination, treat as general conversation
        if not origin or not destination or origin.lower() in greetings or destination.lower() in greetings:
            return {
                "is_search_intent": False,
                "message": msg
            }

        pref = "best_value"
        if "cheap" in msg_lower:
            pref = "cheapest"
        elif "fast" in msg_lower or "quick" in msg_lower:
            pref = "fastest"
        elif "green" in msg_lower or "carbon" in msg_lower or "eco" in msg_lower:
            pref = "eco_friendly"
        elif "safe" in msg_lower or "delay" in msg_lower or "risk" in msg_lower:
            pref = "lowest_risk"

        preferences = {
            "optimize_by": pref,
            "non_stop": "non-stop" in msg_lower or "direct" in msg_lower or "non stop" in msg_lower,
            "wheelchair": "wheelchair" in msg_lower or "accessible" in msg_lower,
            "cabin_only": "cabin baggage" in msg_lower or "cabin only" in msg_lower,
            "refundable": "refundable" in msg_lower
        }
        
        return {
            "is_search_intent": True,
            "origin": origin,
            "destination": destination,
            "start_date": parse_date_from_text(msg),
            "budget": budget,
            "preferences": preferences
        }


class SearchAgent:
    """Gets relevant route links using the graph routing engine."""
    def gather_routes(self, origin: str, destination: str, optimize_by: str, preferences: dict = None) -> List[List[RouterEdge]]:
        all_paths = []
        seen_sig = set()
        
        for opt in ["cheapest", "fastest", "eco_friendly", "lowest_risk", "comfortable_journey", "best_value"]:
            paths = find_routes_dijkstra(origin, destination, optimize_by=opt, max_routes=2, preferences=preferences)
            for path in paths:
                sig = "+".join([f"{e.transport_type}::{e.provider}" for e in path])
                if sig not in seen_sig:
                    seen_sig.add(sig)
                    all_paths.append(path)
        return all_paths


class OptimizationAgent:
    """Collates and structures multi-modal segments into structured itineraries."""
    def format_itinerary(self, path: List[RouterEdge], idx: int) -> Dict[str, Any]:
        total_price = sum(e.price for e in path)
        total_duration = sum(e.duration for e in path)
        total_carbon = sum(e.carbon for e in path)
        
        delay_prob = max(e.delay_prob for e in path) if path else 0.0
        avg_delay = sum(e.avg_delay for e in path)
        reliability = float(max(10, 100 - (delay_prob * 100 * 1.5)))

        leg_comforts = []
        legs_data = []
        for e in path:
            taxes = e.price * 0.18
            baggage = 0.0 if "Flight" not in e.transport_type else 500.0
            seat_fee = 150.0 if "Cab" not in e.transport_type else 0.0
            meals = 350.0 if "Flight" in e.transport_type or "Train" in e.transport_type else 0.0
            base_fare = e.price - (taxes + seat_fee + meals)
            
            hidden_breakdown = {
                "base_fare": round(base_fare, 2),
                "taxes": round(taxes, 2),
                "baggage": round(baggage, 2),
                "seat_fee": round(seat_fee, 2),
                "meals": round(meals, 2),
                "airport_transfer": 450.0 if "Airport" in e.to_node or "Airport" in e.from_node else 0.0
            }
            
            prov = e.provider.lower()
            if "first" in prov or "1a" in prov or "business" in prov or "luxury" in prov or "volvo" in prov:
                leg_comforts.append(9.5)
            elif "2a" in prov or "3a" in prov or "ac sleeper" in prov or "sedan" in prov or "suv" in prov:
                leg_comforts.append(8.6)
            elif "sleeper" in prov or "semi" in prov or "ac" in prov:
                leg_comforts.append(7.2)
            else:
                leg_comforts.append(5.5)

            # Generate real, official booking URL based on transport type
            if e.transport_type == "Flight":
                link = f"https://www.google.com/travel/flights?q=Flights%20to%20{e.to_node}%20from%20{e.from_node}"
            elif e.transport_type == "Train":
                link = "https://www.irctc.co.in/nget/train-search"
            elif e.transport_type == "Bus":
                link = f"https://www.redbus.in/bus-tickets/{e.from_node.lower()}-to-{e.to_node.lower()}"
            elif e.transport_type in ["Cab", "Metro", "Taxi", "Auto"]:
                link = "https://m.uber.com/looking"
            else:
                link = f"https://www.google.com/search?q=book+{e.provider}+{e.from_node}+to+{e.to_node}"

            legs_data.append({
                "transport_type": e.transport_type,
                "provider": e.provider,
                "origin": e.from_node,
                "destination": e.to_node,
                "departure_time": e.departure_time,
                "arrival_time": e.arrival_time,
                "price": e.price,
                "duration": e.duration,
                "delay_probability": e.delay_prob,
                "average_delay": e.avg_delay,
                "refundability": e.refundability,
                "seat_class": "Standard",
                "carbon_footprint": e.carbon,
                "booking_link": link,
                "hidden_costs": json.dumps(hidden_breakdown)
            })

        avg_leg_c = (sum(leg_comforts) / max(1, len(leg_comforts))) if leg_comforts else 8.0
        transfer_penalty = (len(path) - 1) * 0.5
        comfort_score = round(max(3.5, min(9.9, avg_leg_c - transfer_penalty)), 1)

        return {
            "type": "Recommendation",
            "total_price": total_price,
            "total_duration": round(total_duration, 1),
            "carbon_footprint": round(total_carbon, 1),
            "reliability_score": round(reliability, 1),
            "delay_probability": round(delay_prob, 2),
            "average_delay": round(avg_delay, 1),
            "comfort_score": comfort_score,
            "legs": legs_data,
            "is_saved": False
        }


class PredictionAgent:
    """Adds pricing indicators (historical trend graphs and buy/wait recommendations)."""
    def enrich_predictions(self, itinerary: Dict[str, Any]) -> Dict[str, Any]:
        current_price = itinerary["total_price"]
        trend = [current_price * multiplier for multiplier in [1.12, 1.08, 1.05, 1.02, 1.0, 0.98]]
        
        change_direction = random.choice(["up", "down", "stable"])
        confidence = random.randint(70, 95)
        
        if change_direction == "up":
            indicator = "Buy Now"
            explanation = f"Prices are expected to rise by {random.randint(5,15)}% in the next 48 hours. Buy now to secure this fare."
        elif change_direction == "down":
            indicator = "Wait"
            explanation = f"Price trend is downward. Wait to save up to {random.randint(8,20)}% on your booking."
        else:
            indicator = "Buy Now"
            explanation = "Prices are stable but capacity is filling fast."
            
        itinerary["price_prediction"] = {
            "indicator": indicator,
            "confidence": confidence,
            "explanation": explanation,
            "historical_trend": trend
        }
        
        weather_impacts = ["Clear Sky", "Light Rain", "Foggy Conditions", "Heavy Crosswinds"]
        itinerary["delay_prediction"] = {
            "airport_congestion": random.choice(["Low", "Medium", "High"]),
            "weather_impact": random.choice(weather_impacts),
            "average_delay": itinerary["average_delay"]
        }
        
        return itinerary


class RecommendationAgent:
    """Identifies and groups itineraries into specific filter labels."""
    def rank_and_classify(self, itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not itineraries:
            return []
            
        sorted_by_price = sorted(itineraries, key=lambda x: x["total_price"])
        sorted_by_dur = sorted(itineraries, key=lambda x: x["total_duration"])
        sorted_by_carbon = sorted(itineraries, key=lambda x: x["carbon_footprint"])
        sorted_by_risk = sorted(itineraries, key=lambda x: x["delay_probability"])
        
        assigned_types = set()
        
        for it in itineraries:
            labels = []
            if it == sorted_by_price[0]:
                labels.append("Cheapest")
            if it == sorted_by_dur[0]:
                labels.append("Fastest")
            if it == sorted_by_carbon[0]:
                labels.append("Eco Friendly")
            if it == sorted_by_risk[0]:
                labels.append("Lowest Risk")
                
            if not labels:
                labels.append("Best Value" if len(assigned_types) < 2 else "Optimal Route")
                
            primary_label = labels[0]
            it["type"] = primary_label
            assigned_types.add(primary_label)
            
        return itineraries


class ExplanationAgent:
    """Generates natural language reasoning using Gemini AI (with heuristic fallback)."""
    def generate_explanation(self, itinerary: Dict[str, Any], origin: str, dest: str) -> Dict[str, Any]:
        label = itinerary["type"]
        price = itinerary["total_price"]
        duration = itinerary["total_duration"]
        carbon = itinerary["carbon_footprint"]
        transports = [leg["transport_type"] for leg in itinerary["legs"]]
        unique_t = list(set(transports))

        # Attempt Gemini Explanation Generation
        if os.environ.get("GEMINI_API_KEY", "").strip():
            system_prompt = (
                "You are an AI Travel Copilot. Analyze the recommended travel route and return ONLY a JSON object "
                "with keys: why_selected (string), pros (array of strings), cons (array of strings), trade_offs (string)."
            )
            user_prompt = f"Route Type: {label}, Origin: {origin}, Dest: {dest}, Price: ₹{price}, Duration: {duration}h, Carbon: {carbon}kg, Modes: {', '.join(unique_t)}"
            res = call_gemini_api(user_prompt, system_instruction=system_prompt, response_json=True)
            if res:
                try:
                    data = json.loads(res)
                    if data.get("why_selected"):
                        itinerary["ai_explanation"] = data["why_selected"]
                        itinerary["explanation_details"] = {
                            "why_selected": data["why_selected"],
                            "pros": data.get("pros", []),
                            "cons": data.get("cons", []),
                            "trade_offs": data.get("trade_offs", ""),
                            "money_saved": max(0.00, 8000.0 - price),
                            "time_saved_mins": int(max(0.00, 20.0 - duration) * 60)
                        }
                        return itinerary
                except Exception:
                    pass

        # Heuristic Fallback Explanation
        pros = []
        cons = []
        trade_offs = ""
        explanation = ""
        
        if label == "Cheapest":
            pros.append(f"Most budget-friendly route costing just ₹{price}")
            if "Train" in unique_t:
                cons.append(f"Takes longer ({duration} hrs) compared to flights")
                trade_offs = "Saves money but increases travel time compared to flying."
            explanation = f"Selected this route because it is the most competitive rate available between {origin} and {dest}."
        elif label == "Fastest":
            pros.append(f"Completed in just {duration} hours")
            cons.append("Higher cost compared to rail or bus alternatives")
            trade_offs = "Trading off an extra expense for a quicker journey."
            explanation = f"Recommended for business travelers or short stays where speed is critical."
        elif label == "Eco Friendly":
            pros.append(f"Carbon emissions capped at only {carbon} kg CO2")
            cons.append("May involve multi-modal transitions")
            trade_offs = "Reduces CO2 footprint by opting for low-emission rail/metro systems."
            explanation = "Excellent sustainable selection by prioritizing high-efficiency rail infrastructure."
        else:
            pros.append(f"Optimized combination of price (₹{price}) and duration ({duration} hrs)")
            cons.append("Requires coordination between taxi transfers and main tickets")
            trade_offs = "Balanced option. Avoids expensive flights while minimizing transit overhead."
            explanation = "Best value option that coordinates direct flight/express rail with local metro options."
            
        itinerary["ai_explanation"] = explanation
        itinerary["explanation_details"] = {
            "why_selected": explanation,
            "pros": pros,
            "cons": cons,
            "trade_offs": trade_offs,
            "money_saved": max(0.00, 8000.0 - price),
            "time_saved_mins": int(max(0.00, 20.0 - duration) * 60)
        }
        return itinerary


class NotificationAgent:
    def generate_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        return [
            {
                "type": "price_drop",
                "title": "Price Drop Alert: Kanpur to Bangalore",
                "message": "Flight fares dropped by 12% (₹850 savings) for your target travel dates!",
                "is_read": False
            },
            {
                "type": "delay_warning",
                "title": "Delay Forecast: Fog Warning",
                "message": "Light fog expected at Delhi connection hub. Estimated delay: 25 mins.",
                "is_read": False
            },
            {
                "type": "carbon_saving",
                "title": "Green Travel Badge Earned!",
                "message": "Your selected Vande Bharat train route saved 45kg CO2 emissions.",
                "is_read": True
            }
        ]


class BudgetAdvisorAgent:
    """
    AI Financial Travel Advisor that performs intelligent budget analysis,
    allocations, saving suggestions, over-budget detection, hotel/payment optimizations,
    hidden expense analysis, daily breakdowns, and AI confidence scoring.
    """
    def analyze_budget(self, total_budget: float, origin: str = "Kanpur", destination: str = "Bangalore", stay_days: int = 3, current_plan_cost: float = None, lat: float = None, lng: float = None) -> Dict[str, Any]:
        if total_budget <= 0:
            total_budget = 45000.0
        
        if stay_days <= 0:
            stay_days = 3
        
        if current_plan_cost is None or current_plan_cost <= 0:
            current_plan_cost = round(total_budget * 0.96, 2)

        is_over_budget = current_plan_cost > total_budget
        extra_required = round(current_plan_cost - total_budget, 2) if is_over_budget else 0.0

        recommended_budget = round(total_budget * 0.96, 2)
        estimated_savings = round(total_budget - recommended_budget, 2) if not is_over_budget else 0.0

        health_percentage = round((current_plan_cost / total_budget) * 100, 1)
        if health_percentage <= 96:
            budget_health = "Excellent"
        elif health_percentage <= 100:
            budget_health = "Good"
        else:
            budget_health = "Over Budget"

        # 2. Smart Allocations
        flights_amt = round(total_budget * 0.55, 2)
        hotels_amt = round(total_budget * 0.25, 2)
        food_amt = round(total_budget * 0.12, 2)
        transport_amt = round(total_budget * 0.08, 2)

        allocations = [
            {
                "category": "Flights",
                "amount": flights_amt,
                "percentage": 55.0,
                "status": "Excellent",
                "reason": f"Flight prices between {origin} and {destination} are within normal competitive range."
            },
            {
                "category": "Hotels",
                "amount": hotels_amt,
                "percentage": 25.0,
                "status": "Good",
                "reason": f"Hotel rates in {destination} offer high value for 3 to 4-star properties."
            },
            {
                "category": "Food",
                "amount": food_amt,
                "percentage": 12.0,
                "status": "Slightly High",
                "reason": "Selecting dining spots 1-2 km outside prime tourist zones reduces food expenses by 20%."
            },
            {
                "category": "Local Transport",
                "amount": transport_amt,
                "percentage": 8.0,
                "status": "Good",
                "reason": "Direct metro lines and ride-sharing passes are readily available."
            }
        ]

        # 3. AI Savings Suggestions
        savings_suggestions = [
            {"title": "Shift hotel 2 km away from city center", "savings": 2200.0, "category": "Hotels"},
            {"title": "Book flight today before price hike window", "savings": 1300.0, "category": "Flights"},
            {"title": "Use Metro rail pass instead of private taxi", "savings": 850.0, "category": "Transport"},
            {"title": "Choose hotel with complimentary breakfast included", "savings": 1800.0, "category": "Food"}
        ]
        potential_savings = sum(s["savings"] for s in savings_suggestions)

        # 5. Over Budget Suggestions
        over_budget_suggestions = [
            {"title": "Switch to 400m nearby 4-star hotel", "savings": 1800.0, "category": "Hotels"},
            {"title": "Take Vande Bharat Express instead of peak flight", "savings": 1600.0, "category": "Transport"},
            {"title": "Opt for early morning flight leg", "savings": 1100.0, "category": "Flights"}
        ]

        # 7. Payment Optimizations
        payment_optimizations = [
            {"provider": "SBI Cashback Credit Card", "savings": 900.0, "type": "Credit Card Offer"},
            {"provider": "HDFC SmartBuy Travel Direct", "savings": 650.0, "type": "Partner Bank Offer"},
            {"provider": "Instant UPI Cashback Voucher", "savings": 250.0, "type": "UPI Discount"}
        ]

        # 8. Live Hotel Optimization via SerpApi Google Hotels Engine
        live_hotels = live_travel_service.fetch_live_hotels(destination)
        if len(live_hotels) >= 2:
            h1 = live_hotels[0]
            h2 = live_hotels[1]
            if h1["price_per_night"] >= h2["price_per_night"]:
                curr_h, rec_h = h1, h2
            else:
                curr_h, rec_h = h2, h1
            
            savings_p_night = round(curr_h["price_per_night"] - rec_h["price_per_night"], 2)
            if savings_p_night <= 0:
                savings_p_night = 800.0

            hotel_optimization = {
                "current_name": curr_h["name"],
                "current_price": float(curr_h["price_per_night"]),
                "current_rating": str(curr_h["rating"]),
                "recommended_name": rec_h["name"],
                "recommended_price": float(rec_h["price_per_night"]),
                "recommended_rating": str(rec_h["rating"]),
                "distance_difference": "400m from city center",
                "savings_per_night": savings_p_night
            }
        else:
            hotel_optimization = {
                "current_name": f"Grand Palace {destination} Center",
                "current_price": 3500.0,
                "current_rating": "4.2 Stars",
                "recommended_name": f"Courtyard Suites {destination}",
                "recommended_price": 2700.0,
                "recommended_rating": "4.3 Stars",
                "distance_difference": "400m from city center",
                "savings_per_night": 800.0
            }

        # 9. Dynamic Day-Wise Spending Breakdown based on stay_days
        daily_breakdown = []
        per_day_share = 1.0 / stay_days
        for d in range(1, stay_days + 1):
            if d == 1:
                highlight = "Arrival, Airport Transit & Hotel Check-in"
            elif d == stay_days:
                highlight = "Checkout, Souvenir Shopping & Return Airport Transit"
            else:
                highlight = f"Day {d} Sightseeing, Local Food & Metro Travel"
            
            daily_breakdown.append({
                "day": f"Day {d}",
                "amount": round(total_budget * per_day_share, 2),
                "highlights": highlight
            })

        # 10. Hidden Expense Analysis
        hidden_expenses = {
            "airport_tax": 650.0,
            "seat_selection": 300.0,
            "extra_baggage": 900.0,
            "meals": 450.0,
            "gst": 1200.0,
            "total_hidden_cost": 3500.0
        }

        # 11. Emergency Reserve
        emergency_reserve = round(total_budget * 0.05, 2)

        # 12. Plan Comparison
        optimized_plan_cost = round(current_plan_cost - 4200.0, 2)
        total_plan_savings = 4200.0

        # 13. AI Score
        ai_score = 94 if not is_over_budget else 72
        score_reasons = [
            "✔ Excellent transport allocation balancing flights and metro.",
            "✔ Highly affordable 4-star hotel recommendation.",
            "✔ Food budget is well-balanced for local dining.",
            "✔ Local transport cost is optimized with public transit."
        ]

        # 15. Dynamic Scenario Explanations
        scenario_higher = f"If your budget increases to ₹{int(total_budget + 5000):,}, AI recommends upgrading to a premier 4-star hotel with executive lounge access."
        scenario_lower = f"If your budget reduces to ₹{int(max(15000, total_budget - 10000)):,}, AI recommends replacing flights with express Vande Bharat Rail to save ₹9,000."

        # 14. AI Explanation
        ai_explanation = (
            f"Based on travel between {origin} and {destination}, current airline pricing models, and destination hotel rates, "
            f"your budget of ₹{int(total_budget):,} is {'sufficient for a comfortable, high-value trip' if not is_over_budget else 'slightly exceeded by your current selections'}. "
            "Flights receive 55% of allocation because airfare is the primary long-distance expense. Hotels receive 25% due to competitive local lodging rates."
        )

        # 16. Exact Destination Geocoding & Intelligence
        dest_intel = self._resolve_destination_intelligence(origin, destination, stay_days, total_budget, lat=lat, lng=lng)

        return {
            "total_budget": total_budget,
            "recommended_budget": recommended_budget,
            "estimated_savings": estimated_savings,
            "budget_health": budget_health,
            "health_percentage": health_percentage,
            "ai_confidence": 95,
            "ai_explanation": ai_explanation,
            "allocations": allocations,
            "savings_suggestions": savings_suggestions,
            "potential_savings": potential_savings,
            "is_over_budget": is_over_budget,
            "extra_required": extra_required,
            "over_budget_suggestions": over_budget_suggestions,
            "payment_optimizations": payment_optimizations,
            "hotel_optimization": hotel_optimization,
            "daily_breakdown": daily_breakdown,
            "hidden_expenses": hidden_expenses,
            "emergency_reserve": emergency_reserve,
            "current_plan_cost": current_plan_cost,
            "optimized_plan_cost": optimized_plan_cost,
            "total_plan_savings": total_plan_savings,
            "ai_score": ai_score,
            "score_reasons": score_reasons,
            "optimization_scenario_higher": scenario_higher,
            "optimization_scenario_lower": scenario_lower,
            "optimization_result": {
                "before_item": "Standard Flight + City Center Hotel",
                "before_cost": current_plan_cost,
                "after_item": "Optimized Flight + 400m Nearby Hotel",
                "after_cost": optimized_plan_cost,
                "savings": total_plan_savings,
                "explanation": "Switched to a 400m nearby 4-star hotel and booked flight 3 weeks earlier, reducing total trip cost without altering dates."
            },
            "exact_destination": dest_intel["exact_destination"],
            "ai_destination_summary": dest_intel["ai_destination_summary"],
            "recommended_hotels": dest_intel["recommended_hotels"],
            "places_to_visit": dest_intel["places_to_visit"],
            "route_stops": dest_intel["route_stops"]
        }

    def _haversine_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 1)

    def _resolve_destination_intelligence(self, origin: str, destination: str, stay_days: int, total_budget: float, lat: float = None, lng: float = None) -> Dict[str, Any]:
        import urllib.parse
        try:
            from .smart_explore_service import SmartExploreService
            if lat is not None and lng is not None:
                dest_lat, dest_lng = float(lat), float(lng)
            else:
                dest_lat, dest_lng = SmartExploreService.resolve_location_coordinates(destination)
            origin_lat, origin_lng = SmartExploreService.resolve_location_coordinates(origin)
        except Exception as err:
            print(f"Notice: Geocode fallback for '{destination}': {err}")
            dest_lat, dest_lng = lat if lat is not None else 12.9716, lng if lng is not None else 77.5946
            origin_lat, origin_lng = 26.4499, 80.3319

        dest_clean = destination.strip()
        parts = [p.strip() for p in dest_clean.split(',')]
        exact_name = parts[0] if parts else dest_clean
        city = parts[-1] if len(parts) > 1 else dest_clean
        formatted_address = f"{exact_name}, {city}" if len(parts) > 1 else f"{exact_name}"

        print(f"[Target Input] {destination} -> Resolved: ({dest_lat}, {dest_lng}) Exact: {exact_name}, City: {city}")

        hotel_budget = total_budget * 0.25
        target_nightly_rate = round(hotel_budget / max(1, stay_days), 2)
        if target_nightly_rate < 800:
            target_nightly_rate = 1200.0

        # Hotel 1 (0.8 km)
        h1_lat, h1_lng = round(dest_lat + 0.005, 4), round(dest_lng + 0.004, 4)
        h1_dist = self._haversine_distance_km(dest_lat, dest_lng, h1_lat, h1_lng)

        # Hotel 2 (1.4 km)
        h2_lat, h2_lng = round(dest_lat - 0.008, 4), round(dest_lng + 0.006, 4)
        h2_dist = self._haversine_distance_km(dest_lat, dest_lng, h2_lat, h2_lng)

        # Hotel 3 (2.2 km)
        h3_lat, h3_lng = round(dest_lat + 0.012, 4), round(dest_lng - 0.007, 4)
        h3_dist = self._haversine_distance_km(dest_lat, dest_lng, h3_lat, h3_lng)

        recommended_hotels = [
            {
                "id": "hotel_1",
                "name": f"Grand Stay Suites ({exact_name})",
                "lat": h1_lat,
                "lng": h1_lng,
                "distance_km": f"{h1_dist} km from {exact_name}",
                "rating": "4.6",
                "price_per_night": round(target_nightly_rate * 0.95, 2),
                "total_stay_cost": round(target_nightly_rate * 0.95 * stay_days, 2),
                "ai_reason": f"Highest value 4-star hotel within {h1_dist} km of {exact_name}.",
                "booking_link": f"https://www.google.com/travel/hotels?q={urllib.parse.quote(exact_name + ' hotel')}"
            },
            {
                "id": "hotel_2",
                "name": f"Courtyard Express near {exact_name}",
                "lat": h2_lat,
                "lng": h2_lng,
                "distance_km": f"{h2_dist} km from {exact_name}",
                "rating": "4.3",
                "price_per_night": round(target_nightly_rate * 0.75, 2),
                "total_stay_cost": round(target_nightly_rate * 0.75 * stay_days, 2),
                "ai_reason": f"Budget saver saving {round((target_nightly_rate * 0.25) * stay_days)} INR while staying {h2_dist} km from {exact_name}.",
                "booking_link": f"https://www.google.com/travel/hotels?q={urllib.parse.quote(exact_name + ' hotel')}"
            },
            {
                "id": "hotel_3",
                "name": f"Royal Heritage Hotel ({city})",
                "lat": h3_lat,
                "lng": h3_lng,
                "distance_km": f"{h3_dist} km from {exact_name}",
                "rating": "4.8",
                "price_per_night": round(target_nightly_rate * 1.25, 2),
                "total_stay_cost": round(target_nightly_rate * 1.25 * stay_days, 2),
                "ai_reason": f"Premium luxury stay with complimentary breakfast and pool access near {exact_name}.",
                "booking_link": f"https://www.google.com/travel/hotels?q={urllib.parse.quote(exact_name + ' hotel')}"
            }
        ]

        p1_lat, p1_lng = dest_lat, dest_lng
        p1_dist = self._haversine_distance_km(dest_lat, dest_lng, p1_lat, p1_lng)

        p2_lat, p2_lng = round(dest_lat + 0.009, 4), round(dest_lng - 0.005, 4)
        p2_dist = self._haversine_distance_km(dest_lat, dest_lng, p2_lat, p2_lng)

        p3_lat, p3_lng = round(dest_lat - 0.007, 4), round(dest_lng - 0.008, 4)
        p3_dist = self._haversine_distance_km(dest_lat, dest_lng, p3_lat, p3_lng)

        p4_lat, p4_lng = round(dest_lat + 0.015, 4), round(dest_lng + 0.011, 4)
        p4_dist = self._haversine_distance_km(dest_lat, dest_lng, p4_lat, p4_lng)

        places_to_visit = [
            {
                "id": "place_1",
                "name": f"{exact_name} Main Landmark Zone",
                "category": "Primary Destination",
                "lat": p1_lat,
                "lng": p1_lng,
                "distance_km": f"{p1_dist} km",
                "estimated_cost": 0.0,
                "visit_duration": "1.5 - 2 hrs",
                "ai_reason": f"Your primary destination! Explore key highlights, architecture, and photography spots."
            },
            {
                "id": "place_2",
                "name": f"{city} Cultural Promenade",
                "category": "Sightseeing & Heritage",
                "lat": p2_lat,
                "lng": p2_lng,
                "distance_km": f"{p2_dist} km",
                "estimated_cost": 50.0,
                "visit_duration": "2 hrs",
                "ai_reason": f"Top rated architectural and cultural attraction near {exact_name}."
            },
            {
                "id": "place_3",
                "name": f"{city} Local Cuisine & Craft Market",
                "category": "Food & Shopping",
                "lat": p3_lat,
                "lng": p3_lng,
                "distance_km": f"{p3_dist} km",
                "estimated_cost": 300.0,
                "visit_duration": "2 - 3 hrs",
                "ai_reason": f"Popular food hub for authentic local dishes and souvenir shopping."
            },
            {
                "id": "place_4",
                "name": f"{city} Eco Park & Gardens",
                "category": "Nature & Relaxation",
                "lat": p4_lat,
                "lng": p4_lng,
                "distance_km": f"{p4_dist} km",
                "estimated_cost": 20.0,
                "visit_duration": "1.5 hrs",
                "ai_reason": f"Peaceful green space ideal for evening walks and relaxation."
            }
        ]

        route_stops = []
        if origin.lower().strip() != destination.lower().strip():
            mid_lat = round((origin_lat + dest_lat) / 2.0, 4)
            mid_lng = round((origin_lng + dest_lng) / 2.0, 4)
            route_stops = [
                {
                    "id": "stop_1",
                    "name": f"Highway Scenic Break Point ({origin} ➔ {city})",
                    "category": "Travel Break Point",
                    "lat": mid_lat,
                    "lng": mid_lng,
                    "distance_from_origin": "Intermediate Transit Hub",
                    "ai_reason": f"Recommended rest stop for snacks, fuel, and refreshment on the route to {exact_name}."
                }
            ]

        ai_summary = (
            f"Based on your ₹{int(total_budget):,} budget and {stay_days}-day trip to {exact_name}, "
            f"I have identified 3 top-rated hotels within 2 km of {exact_name} and 4 curated sightseeing spots "
            f"that fit seamlessly into your financial allocation."
        )

        return {
            "exact_destination": {
                "exact_name": exact_name,
                "formatted_address": formatted_address,
                "lat": dest_lat,
                "lng": dest_lng,
                "city": city
            },
            "ai_destination_summary": ai_summary,
            "recommended_hotels": recommended_hotels,
            "places_to_visit": places_to_visit,
            "route_stops": route_stops
        }


class TravelAgentSystem:
    def __init__(self):
        self.planner = PlannerAgent()
        self.search = SearchAgent()
        self.optimization = OptimizationAgent()
        self.prediction = PredictionAgent()
        self.recommendation = RecommendationAgent()
        self.explanation = ExplanationAgent()
        self.notifier = NotificationAgent()
        self.budget_advisor = BudgetAdvisorAgent()

    def process_universal_search(self, origin: str, destination: str, date: str, budget: float = None, preferences: dict = None) -> List[Dict[str, Any]]:
        raw_paths = self.search.gather_routes(origin, destination, preferences.get("optimize_by", "best_value") if preferences else "best_value", preferences=preferences)
        
        itineraries = []
        for idx, path in enumerate(raw_paths):
            it = self.optimization.format_itinerary(path, idx)
            it = self.prediction.enrich_predictions(it)
            it = self.explanation.generate_explanation(it, origin, destination)
            itineraries.append(it)
            
        ranked_itineraries = self.recommendation.rank_and_classify(itineraries)
        ranked_itineraries = sorted(ranked_itineraries, key=lambda x: (x["type"] != "Best Value", x["total_price"]))
        
        return ranked_itineraries

    def handle_chat_message(self, message: str, user_id: int) -> Dict[str, Any]:
        parsed = self.planner.parse_intent(message)
        
        # If user intent is NOT a travel route search (e.g. greeting, general inquiry)
        if not parsed.get("is_search_intent"):
            # Try Gemini conversational response first
            if os.environ.get("GEMINI_API_KEY", "").strip():
                system_prompt = (
                    "You are an AI Travel Copilot. Be friendly, helpful, and concise. "
                    "Introduce yourself, answer the user's travel question or greeting, and invite them to search routes."
                )
                gemini_reply = call_gemini_api(message, system_instruction=system_prompt)
                if gemini_reply:
                    return {
                        "reply": gemini_reply,
                        "follow_ups": [
                            "Cheapest Kanpur to Bangalore under ₹5000",
                            "Fastest non-stop option from Delhi to Mumbai",
                            "Eco-friendly train route to Jaipur"
                        ],
                        "itineraries": []
                    }
            
            # Smart Conversational Fallback (no forced default search cards!)
            reply = (
                "👋 Hello! I am your AI Travel Copilot. "
                "I can analyze multi-modal travel routes combining **Flights, Trains, Buses, Cabs, and Metro** to find your optimal path.\n\n"
                "Try asking me something like:\n"
                "• *'Find cheapest route from Kanpur to Bangalore under ₹5000'*\n"
                "• *'Fastest non-stop flight from Delhi to Mumbai'*\n"
                "• *'Eco-friendly train options from Lucknow to Jaipur'*"
            )
            return {
                "reply": reply,
                "follow_ups": [
                    "Cheapest Kanpur to Bangalore under ₹5000",
                    "Fastest non-stop option from Delhi to Mumbai",
                    "Eco-friendly train route to Jaipur"
                ],
                "itineraries": []
            }

        # Otherwise, process travel route search request
        origin = parsed.get("origin", "Kanpur")
        destination = parsed.get("destination", "Bangalore")
        
        results = self.process_universal_search(
            origin=origin,
            destination=destination,
            date=parsed.get("start_date"),
            budget=parsed.get("budget"),
            preferences=parsed.get("preferences")
        )
        
        from .routing_engine import resolve_hyperlocal_info, calculate_cab_fare, resolve_global_city
        org_info = resolve_hyperlocal_info(origin)
        dst_global = resolve_global_city(destination)
        
        cab_summary = ""
        if org_info.get("station_distance_km"):
            cab_summary = (
                f"\n\n📍 **Exact Pickup Location Breakdown ({org_info['full_name']})**:\n"
                f"• Distance to {org_info['nearest_station']}: **{org_info['station_distance_km']} km** (~{int(org_info['station_time_hrs']*60)} mins)\n"
                f"• Estimated Uber Go / Ola Fare: **₹{calculate_cab_fare(org_info['station_distance_km'], 'uber_go'):.0f}**\n"
                f"• Estimated Uber Auto Fare: **₹{calculate_cab_fare(org_info['station_distance_km'], 'uber_auto'):.0f}**\n"
                f"• Distance to {org_info['nearest_airport']}: **{org_info['airport_distance_km']} km** (~{int(org_info['airport_time_hrs']*60)} mins)\n"
                f"• Intercity Express Cab Fare: **₹{calculate_cab_fare(org_info['airport_distance_km'], 'uber_intercity'):.0f}**"
            )

        global_advice = ""
        if dst_global["country"] != "India":
            global_advice = (
                f"\n\n🌐 **Global Travel & Entry Guidance ({dst_global['city']}, {dst_global['country']})**:\n"
                f"• **Passport & Visa**: Ensure passport is valid for 6+ months. Check E-Visa / ESTA / Transit Visa requirements.\n"
                f"• **Airport Arrival Hub**: Flying into **{dst_global['airport']}**.\n"
                f"• **Local Airport Transfer**: Connected via **{results[0]['legs'][-1]['provider']}** direct to {dst_global['city']}.\n"
                f"• **Baggage Allowance**: Standard International Allowance is 25kg–30kg checked baggage + 7kg cabin baggage."
            )

        travel_date_raw = parsed.get("start_date") or datetime.now().strftime("%Y-%m-%d")
        try:
            dt_obj = datetime.strptime(travel_date_raw, "%Y-%m-%d")
            formatted_date = dt_obj.strftime("%d %b %Y (%A)")
        except Exception:
            formatted_date = travel_date_raw

        reply = (
            f"📅 **Travel Departure Date**: **{formatted_date}**\n\n"
            f"I have analyzed live multi-modal travel routes between **{origin}** and **{destination}** for **{formatted_date}** "
            f"focusing on your preferences: **{parsed['preferences']['optimize_by'].replace('_', ' ').title()}**.\n\n"
            f"I recommend a multi-modal itinerary: **{results[0]['legs'][0]['transport_type']} → "
            f"{results[0]['legs'][-1]['transport_type']}**, taking **{results[0]['total_duration']} hours** and costing "
            f"**₹{results[0]['total_price']:.0f}**."
            f"{cab_summary}"
            f"{global_advice}\n\n"
            f"*AI Recommendation Rationale:* {results[0]['ai_explanation']}\n\n"
            f"💡 *Want to search a different date? Ask me anytime e.g. 'Show flights for 25th August' or 'Search routes for tomorrow'!*"
        )
        
        follow_ups = [
            f"Show cheapest international flights from {origin} to {destination}",
            f"What is the visa policy for travelling to {destination}?",
            f"Add this international trip to my Itinerary Planner",
            f"What is the local weather forecast for {destination}?"
        ]
        
        return {
            "reply": reply,
            "follow_ups": follow_ups,
            "itineraries": results
        }

