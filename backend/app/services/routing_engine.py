import heapq
from typing import List, Dict, Any, Tuple
import random

class RouterNode:
    def __init__(self, name: str, node_type: str):
        self.name = name
        self.type = node_type # "city", "airport", "station", "bus_stop"

class RouterEdge:
    def __init__(self, from_node: str, to_node: str, transport_type: str, provider: str, 
                 price: float, duration: float, departure_time: str, arrival_time: str, 
                 delay_prob: float, avg_delay: float, carbon: float, refundability: str = "Non-refundable"):
        self.from_node = from_node
        self.to_node = to_node
        self.transport_type = transport_type
        self.provider = provider
        self.price = price
        self.duration = duration
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.delay_prob = delay_prob
        self.avg_delay = avg_delay
        self.carbon = carbon
        self.refundability = refundability

# Hyper-local landmark distance database & calculator
HYPERLOCAL_LANDMARKS = {
    "psit": {
        "full_name": "PSIT Kanpur (Pranveer Singh Institute of Technology, Bhaunti)",
        "city": "Kanpur",
        "station_distance_km": 22.0,
        "station_time_hrs": 0.75,
        "airport_distance_km": 88.0,
        "airport_time_hrs": 1.75,
        "nearest_station": "Kanpur Central Station (CNB)",
        "nearest_airport": "Lucknow Airport (LKO)"
    },
    "iit kanpur": {
        "full_name": "IIT Kanpur Campus (Kalyanpur)",
        "city": "Kanpur",
        "station_distance_km": 16.0,
        "station_time_hrs": 0.55,
        "airport_distance_km": 82.0,
        "airport_time_hrs": 1.6,
        "nearest_station": "Kanpur Central Station (CNB)",
        "nearest_airport": "Lucknow Airport (LKO)"
    },
    "bhaunti": {
        "full_name": "Bhaunti Kanpur (NH19 Highway Gate)",
        "city": "Kanpur",
        "station_distance_km": 21.0,
        "station_time_hrs": 0.7,
        "airport_distance_km": 87.0,
        "airport_time_hrs": 1.7,
        "nearest_station": "Kanpur Central Station (CNB)",
        "nearest_airport": "Lucknow Airport (LKO)"
    },
    "whitefield": {
        "full_name": "Whitefield IT Park (Bangalore)",
        "city": "Bangalore",
        "station_distance_km": 23.0,
        "station_time_hrs": 0.8,
        "airport_distance_km": 38.0,
        "airport_time_hrs": 1.15,
        "nearest_station": "KSR Bengaluru Station (SBC)",
        "nearest_airport": "Kempegowda Int'l Airport (BLR)"
    },
    "electronic city": {
        "full_name": "Electronic City (Bangalore)",
        "city": "Bangalore",
        "station_distance_km": 20.0,
        "station_time_hrs": 0.75,
        "airport_distance_km": 52.0,
        "airport_time_hrs": 1.4,
        "nearest_station": "KSR Bengaluru Station (SBC)",
        "nearest_airport": "Kempegowda Int'l Airport (BLR)"
    },
    "janakpuri": {
        "full_name": "Janakpuri West (New Delhi)",
        "city": "Delhi",
        "station_distance_km": 17.0,
        "station_time_hrs": 0.5,
        "airport_distance_km": 14.0,
        "airport_time_hrs": 0.4,
        "nearest_station": "New Delhi Railway Station (NDLS)",
        "nearest_airport": "Indira Gandhi Int'l Airport (DEL)"
    },
    "connaught place": {
        "full_name": "Connaught Place (Central Delhi)",
        "city": "Delhi",
        "station_distance_km": 2.5,
        "station_time_hrs": 0.15,
        "airport_distance_km": 15.0,
        "airport_time_hrs": 0.45,
        "nearest_station": "New Delhi Railway Station (NDLS)",
        "nearest_airport": "Indira Gandhi Int'l Airport (DEL)"
    }
}

def resolve_hyperlocal_info(location_str: str) -> Dict[str, Any]:
    loc_lower = location_str.strip().lower()
    for key, data in HYPERLOCAL_LANDMARKS.items():
        if key in loc_lower:
            return data
    
    city_name = location_str.strip().title()
    return {
        "full_name": location_str.strip().title(),
        "city": city_name,
        "station_distance_km": 12.0,
        "station_time_hrs": 0.45,
        "airport_distance_km": 28.0,
        "airport_time_hrs": 0.8,
        "nearest_station": f"{city_name} Station",
        "nearest_airport": f"{city_name} Airport"
    }

def calculate_cab_fare(distance_km: float, cab_type: str = "uber_go") -> float:
    if cab_type == "uber_auto":
        fare = 30.0 + (distance_km * 12.0)
    elif cab_type == "uber_intercity":
        fare = 150.0 + (distance_km * 14.0)
    else:
        fare = 50.0 + (distance_km * 16.0)
    return round(fare, 0)

from .live_travel_api import GLOBAL_AIRPORTS, live_travel_service

def resolve_global_city(city_name: str) -> Dict[str, Any]:
    city_lower = city_name.strip().lower()
    for key, data in GLOBAL_AIRPORTS.items():
        if key in city_lower or city_lower in key:
            return data
    
    clean_code = "".join([c for c in city_lower if c.isalnum()])[:3].upper() or "XYZ"
    is_indian = any(ind in city_lower for ind in ["kanpur", "delhi", "mumbai", "bangalore", "bengaluru", "lucknow", "chennai", "kolkata", "hyderabad", "jaipur", "goa", "pune", "ahmedabad", "varanasi"])
    return {
        "code": clean_code,
        "airport": f"{city_name.strip().title()} Int'l Airport ({clean_code})",
        "city": city_name.strip().title(),
        "country": "India" if is_indian else "International"
    }

def generate_graph(origin: str, destination: str) -> Tuple[Dict[str, RouterNode], Dict[str, List[RouterEdge]]]:
    """
    Dynamically generates a global multi-modal travel connection graph between origin and destination,
    supporting exact pickup locations (e.g. PSIT Kanpur), international flights, trains, buses, local cabs, and metro transfers.
    """
    nodes = {}
    edges = {}

    org = origin.strip().title()
    dst = destination.strip().title()
    
    org_info = resolve_hyperlocal_info(origin)
    dst_info = resolve_hyperlocal_info(destination)

    org_global = resolve_global_city(org_info["city"])
    dst_global = resolve_global_city(dst_info["city"])

    is_international = org_global["country"].lower() != dst_global["country"].lower()

    # Predefined nearby hubs mapping for major Indian cities
    nearby_hubs = {
        "Kanpur": {
            "airport": "Lucknow Airport (LKO)",
            "airport_code": "LKO",
            "station": "Kanpur Central Station (CNB)",
            "station_code": "CNB",
            "has_local_airport": False
        },
        "Lucknow": {
            "airport": "Lucknow Airport (LKO)",
            "airport_code": "LKO",
            "station": "Lucknow Charbagh (LJN)",
            "station_code": "LJN",
            "has_local_airport": True
        },
        "Bangalore": {
            "airport": "Kempegowda Int'l Airport (BLR)",
            "airport_code": "BLR",
            "station": "KSR Bengaluru Station (SBC)",
            "station_code": "SBC",
            "has_local_airport": True
        },
        "Delhi": {
            "airport": "Indira Gandhi Int'l Airport (DEL)",
            "airport_code": "DEL",
            "station": "New Delhi Railway Station (NDLS)",
            "station_code": "NDLS",
            "has_local_airport": True
        },
        "Mumbai": {
            "airport": "Chhatrapati Shivaji Airport (BOM)",
            "airport_code": "BOM",
            "station": "Mumbai Chatrapati Shivaji Terminus (CSMT)",
            "station_code": "CSMT",
            "has_local_airport": True
        },
        "Jaipur": {
            "airport": "Jaipur Airport (JAI)",
            "airport_code": "JAI",
            "station": "Jaipur Junction (JP)",
            "station_code": "JP",
            "has_local_airport": True
        }
    }

    def get_city_hubs(city_name: str, global_info: Dict[str, Any]):
        if city_name in nearby_hubs:
            return nearby_hubs[city_name]
        return {
            "airport": global_info["airport"],
            "airport_code": global_info["code"],
            "station": f"{city_name} Central Station",
            "station_code": f"{global_info['code']}S",
            "has_local_airport": True
        }

    org_hubs = get_city_hubs(org_info["city"], org_global)
    dst_hubs = get_city_hubs(dst_info["city"], dst_global)

    # 1. Define Nodes
    nodes[org] = RouterNode(org, "city")
    nodes[dst] = RouterNode(dst, "city")
    
    # Origin Station and Hubs
    nodes[org_hubs["station"]] = RouterNode(org_hubs["station"], "station")
    nodes[org_hubs["airport"]] = RouterNode(org_hubs["airport"], "airport")
    
    # Destination Station and Hubs
    nodes[dst_hubs["station"]] = RouterNode(dst_hubs["station"], "station")
    nodes[dst_hubs["airport"]] = RouterNode(dst_hubs["airport"], "airport")

    connecting_airport = "Indira Gandhi Int'l Airport (DEL)"
    if org_hubs["airport_code"] != "DEL" and dst_hubs["airport_code"] != "DEL":
        nodes[connecting_airport] = RouterNode(connecting_airport, "airport")

    for name in nodes:
        edges[name] = []

    def add_edge(edge: RouterEdge):
        edges[edge.from_node].append(edge)

    # 2. Add hyper-local exact cab fare connections at origin
    station_cab_fare = calculate_cab_fare(org_info["station_distance_km"], "uber_go")
    station_auto_fare = calculate_cab_fare(org_info["station_distance_km"], "uber_auto")
    airport_cab_fare = calculate_cab_fare(org_info["airport_distance_km"], "uber_intercity" if not org_hubs["has_local_airport"] else "uber_go")
    
    # Origin -> Station
    add_edge(RouterEdge(
        org, org_hubs["station"],
        "Cab", f"Uber Go ({org_info['station_distance_km']} km)",
        station_cab_fare, org_info["station_time_hrs"], "08:00", "08:45",
        0.05, 5.0, 10.0, "Refundable"
    ))
    add_edge(RouterEdge(
        org, org_hubs["station"],
        "Auto", f"Uber Auto / Ola ({org_info['station_distance_km']} km)",
        station_auto_fare, org_info["station_time_hrs"] + 0.1, "08:05", "08:55",
        0.05, 5.0, 5.0, "Refundable"
    ))

    # Origin -> Airport
    if org_hubs["has_local_airport"]:
        add_edge(RouterEdge(
            org, org_hubs["airport"],
            "Cab", f"Uber Go ({org_info['airport_distance_km']} km)",
            airport_cab_fare, org_info["airport_time_hrs"], "09:00", "09:48",
            0.08, 8.0, 24.0, "Refundable"
        ))
    else:
        # e.g., PSIT Kanpur to Lucknow Airport (Intercity cab ~88 km)
        add_edge(RouterEdge(
            org, org_hubs["airport"],
            "Cab", f"Uber Intercity ({org_info['airport_distance_km']} km via NH19)",
            airport_cab_fare, org_info["airport_time_hrs"], "08:00", "09:45",
            0.10, 10.0, 55.0, "Refundable"
        ))
        add_edge(RouterEdge(org, org_hubs["airport"], "Bus", "Airport Express Shuttle", 250, 2.5, "07:30", "10:00", 0.15, 20.0, 18.0, "Non-refundable"))

    # Destination Airport -> Destination (International or Domestic Local Transit)
    if is_international:
        dst_country = dst_global["country"].lower()
        if "usa" in dst_country or "york" in dst.lower() or "america" in dst.lower():
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Subway", "JFK AirTrain & NYC Subway", 650, 0.75, "18:00", "18:45", 0.02, 2.0, 1.5, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "NYC Yellow Taxi / Uber", 2800, 0.85, "18:00", "18:50", 0.05, 5.0, 15.0, "Refundable"))
        elif "uk" in dst_country or "london" in dst.lower() or "england" in dst.lower():
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Heathrow Express & Tube", 1300, 0.5, "18:00", "18:30", 0.01, 1.0, 1.2, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "London Black Cab / Uber", 3200, 0.7, "18:00", "18:42", 0.05, 5.0, 14.0, "Refundable"))
        elif "uae" in dst_country or "dubai" in dst.lower():
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Dubai Metro Red Line", 180, 0.4, "18:00", "18:24", 0.01, 1.0, 0.8, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Dubai RTA Taxi / Uber", 1200, 0.5, "18:00", "18:30", 0.03, 3.0, 8.0, "Refundable"))
        elif "singapore" in dst_country or "singapore" in dst.lower():
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Changi Airport MRT Line", 175, 0.45, "18:00", "18:27", 0.01, 1.0, 0.9, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Grab / Singapore Taxi", 1400, 0.5, "18:00", "18:30", 0.02, 2.0, 9.0, "Refundable"))
        elif "japan" in dst_country or "tokyo" in dst.lower():
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Train", "Narita Express (N'EX)", 1400, 0.9, "18:00", "18:54", 0.01, 1.0, 2.0, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Tokyo Japan Taxi / Uber", 4500, 1.1, "18:00", "19:06", 0.03, 3.0, 16.0, "Refundable"))
        else:
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Airport Express Rail / Metro", 450, 0.6, "18:00", "18:36", 0.02, 2.0, 1.5, "Refundable"))
            add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Airport Shuttle / Uber Taxi", 1800, 0.75, "18:00", "18:45", 0.04, 4.0, 10.0, "Refundable"))
    else:
        # Domestic Destination Airport -> Destination
        add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Uber/Ola", 750, 1.0, "15:00", "16:00", 0.10, 10.0, 30.0, "Refundable"))
        add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Local Metro", 60, 0.9, "15:10", "16:04", 0.02, 2.0, 2.7, "Refundable"))

        # Destination Station -> Destination (Domestic Only)
        add_edge(RouterEdge(dst_hubs["station"], dst, "Cab", "Auto Rickshaw / Taxi", 150, 0.4, "12:00", "12:24", 0.05, 5.0, 8.0, "Refundable"))
        add_edge(RouterEdge(dst_hubs["station"], dst, "Metro", "Local Metro", 30, 0.3, "12:00", "12:18", 0.01, 1.0, 0.9, "Refundable"))

    # 3. Add Long Distance Flights (International or Domestic)
    if is_international:
        dst_country = dst_global["country"].lower()
        dst_name = dst.lower()
        if "usa" in dst_country or "york" in dst_name or "america" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Air India AI-101 (Direct Long-Haul)", 64000, 15.0, "02:00", "07:30", 0.08, 12.0, 480.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Emirates EK-201 (via Dubai DXB)", 54000, 16.5, "04:15", "14:45", 0.05, 8.0, 420.0, "Non-refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Qatar Airways QR-701 (via Doha DOH)", 52000, 17.0, "03:30", "14:30", 0.06, 9.0, 410.0, "Non-refundable"))
        elif "uk" in dst_country or "london" in dst_name or "england" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "British Airways BA-142 (Direct)", 44000, 9.0, "08:15", "12:45", 0.05, 7.0, 310.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Air India AI-115 (Direct)", 41000, 9.5, "06:45", "11:45", 0.09, 15.0, 320.0, "Non-refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Virgin Atlantic VS-301", 46000, 9.2, "10:30", "15:12", 0.04, 6.0, 305.0, "Refundable"))
        elif "uae" in dst_country or "dubai" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Emirates EK-501 (Non-Stop)", 18500, 3.5, "09:15", "11:15", 0.04, 5.0, 140.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "IndiGo 6E-1401 (Non-Stop)", 14200, 4.0, "16:20", "18:50", 0.06, 9.0, 130.0, "Non-refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "FlyDubai FZ-431", 15800, 3.8, "12:00", "14:18", 0.05, 7.0, 135.0, "Refundable"))
        elif "singapore" in dst_country or "singapore" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Singapore Airlines SQ-423 (Non-Stop)", 24000, 5.5, "23:00", "07:00", 0.03, 4.0, 190.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "IndiGo 6E-53 (Non-Stop)", 16500, 5.8, "14:10", "22:28", 0.06, 10.0, 180.0, "Non-refundable"))
        elif "thailand" in dst_country or "bangkok" in dst_name or "bali" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Thai Airways TG-316", 18000, 4.0, "00:15", "05:45", 0.04, 6.0, 150.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "AirAsia X D7-182", 14500, 4.5, "11:20", "17:20", 0.07, 12.0, 145.0, "Non-refundable"))
        elif "japan" in dst_country or "tokyo" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "ANA All Nippon Airways NH-830", 48000, 8.0, "20:15", "06:45", 0.03, 5.0, 290.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Japan Airlines JL-740", 52000, 8.5, "19:00", "05:30", 0.04, 6.0, 300.0, "Refundable"))
        elif "australia" in dst_country or "sydney" in dst_name:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Qantas QF-68 (Direct Long-Haul)", 56000, 12.0, "18:30", "10:00", 0.05, 8.0, 410.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", "Singapore Airlines SQ-211 (via SIN)", 62000, 14.5, "14:00", "08:00", 0.04, 6.0, 430.0, "Refundable"))
        else:
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", f"Global Intercontinental Air ({dst_global['code']})", 38000, 10.0, "06:00", "16:00", 0.06, 10.0, 350.0, "Refundable"))
            add_edge(RouterEdge(org_hubs["airport"], dst_hubs["airport"], "Flight", f"World Connect Airways ({dst_global['code']})", 42000, 12.0, "10:00", "22:00", 0.08, 14.0, 380.0, "Non-refundable"))
        
        # Connecting International Flight via DEL
        if org_hubs["airport_code"] != "DEL":
            add_edge(RouterEdge(org_hubs["airport"], connecting_airport, "Flight", "IndiGo 6E-6101 (Domestic Transfer)", 3000, 1.2, "10:00", "11:12", 0.05, 8.0, 90.0, "Non-refundable"))
            add_edge(RouterEdge(connecting_airport, dst_hubs["airport"], "Flight", f"Emirates / Air India Int'l ({dst_global['code']})", 48000, 11.0, "14:00", "23:00", 0.07, 10.0, 360.0, "Refundable"))
    else:
        # Domestic Flight Options
        live_flights = live_travel_service.fetch_live_flights(org, dst)
        for f in live_flights:
            add_edge(RouterEdge(
                org_hubs["airport"], dst_hubs["airport"],
                "Flight", f["provider"],
                f["price"], 2.2, f["departure_time"], f["arrival_time"],
                f["delay_prob"], f["avg_delay"], f.get("carbon", 130.0),
                "Refundable" if "Air India" in f["provider"] else "Non-refundable"
            ))

        if org_hubs["airport_code"] != "DEL" and dst_hubs["airport_code"] != "DEL":
            add_edge(RouterEdge(org_hubs["airport"], connecting_airport, "Flight", "IndiGo 6E-6101", 3000, 1.2, "10:00", "11:12", 0.05, 8.0, 90.0, "Non-refundable"))
            add_edge(RouterEdge(connecting_airport, dst_hubs["airport"], "Flight", "IndiGo 6E-2401", 3500, 2.0, "13:30", "15:30", 0.09, 14.0, 160.0, "Non-refundable"))

        # DOMESTIC ONLY: Add Live Trains (Station -> Station)
        live_trains = live_travel_service.fetch_live_trains(org, dst)
        for t in live_trains:
            add_edge(RouterEdge(
                org_hubs["station"], dst_hubs["station"],
                "Train", f"{t['provider']} ({t.get('seat_class', 'Sleeper')})",
                t["price"], t.get("duration", 12.0), t["departure_time"], t["arrival_time"],
                t["delay_prob"], t["avg_delay"], t.get("carbon", 40.0),
                "Refundable"
            ))

        # DOMESTIC ONLY: Intercity Direct Buses (Origin -> Destination)
        add_edge(RouterEdge(
            org, dst,
            "Bus", "KSRTC / Zingbus Sleeper",
            1200, 14.0, "18:00", "08:00",
            0.20, 30.0, 75.0, "Partial Refund"
        ))

    return nodes, edges

    return nodes, edges

def find_routes_dijkstra(origin: str, destination: str, optimize_by: str = "best_value", max_routes: int = 5) -> List[List[RouterEdge]]:
    """
    Finds multiple paths using modified Dijkstra search on the transport graph.
    optimize_by can be: "cheapest", "fastest", "best_value", "eco_friendly", "lowest_risk"
    """
    origin_title = origin.strip().title()
    dest_title = destination.strip().title()
    
    nodes, edges = generate_graph(origin_title, dest_title)
    
    # Weight formulas based on preference
    def get_edge_weight(edge: RouterEdge) -> float:
        if optimize_by == "cheapest":
            return edge.price
        elif optimize_by == "fastest":
            return edge.duration
        elif optimize_by == "eco_friendly":
            return edge.carbon
        elif optimize_by == "lowest_risk":
            # high delay prob is bad
            return edge.delay_prob * 100 + edge.avg_delay
        else: # "best_value"
            # Normalize price and time: price + duration * 1000 + delay_risk * 50
            return edge.price + (edge.duration * 600) + (edge.delay_prob * 1200)

    # Use Yen's algorithm / K-shortest paths or path-branching heuristic to find multiple unique paths
    # For our simple transport graph, we can find paths by performing DFS/BFS or tracking visited paths in a priority queue.
    # Let's use a path-based Search Queue to retrieve all valid topological paths from origin to destination without infinite loops.
    
    valid_paths = []
    # Queue: (cumulative_weight, counter, current_node, path_edges)
    counter = 0
    queue = [(0.0, counter, origin_title, [])]
    
    while queue and len(valid_paths) < max_routes * 3:
        weight, _, curr, path = heapq.heappop(queue)
        
        if curr == dest_title:
            valid_paths.append((weight, path))
            continue
            
        # Avoid visiting same node twice in same path
        visited_nodes = {edge.from_node for edge in path}
        visited_nodes.add(curr)
        
        for edge in edges.get(curr, []):
            if edge.to_node not in visited_nodes:
                new_weight = weight + get_edge_weight(edge)
                counter += 1
                heapq.heappush(queue, (new_weight, counter, edge.to_node, path + [edge]))
                
    # Sort and filter unique paths (by list of edge descriptions to avoid clones)
    unique_paths = []
    seen_route_signatures = set()
    
    for weight, path in valid_paths:
        signature = "+".join([f"{e.transport_type}::{e.provider}" for e in path])
        if signature not in seen_route_signatures:
            seen_route_signatures.add(signature)
            unique_paths.append(path)
            
    return unique_paths[:max_routes]
