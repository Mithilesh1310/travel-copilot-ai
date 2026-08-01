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

def generate_graph(origin: str, destination: str) -> Tuple[Dict[str, RouterNode], Dict[str, List[RouterEdge]]]:
    """
    Dynamically generates a travel connection graph between origin and destination,
    supporting exact pickup locations (e.g. PSIT Kanpur), flights, trains, buses, local cabs, and metro transfers.
    """
    nodes = {}
    edges = {}

    org = origin.strip().title()
    dst = destination.strip().title()
    
    org_info = resolve_hyperlocal_info(origin)
    dst_info = resolve_hyperlocal_info(destination)

    # Predefined nearby hubs mapping for major Indian cities to keep it highly realistic
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

    def get_city_hubs(city_name: str):
        if city_name in nearby_hubs:
            return nearby_hubs[city_name]
        return {
            "airport": f"{city_name} Airport ({city_name[:3].upper()}L)",
            "airport_code": f"{city_name[:3].upper()}L",
            "station": f"{city_name} Station ({city_name[:3].upper()}S)",
            "station_code": f"{city_name[:3].upper()}S",
            "has_local_airport": True
        }

    org_hubs = get_city_hubs(org_info["city"])
    dst_hubs = get_city_hubs(dst_info["city"])

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

    # 2. Add hyper-local exact cab fare connections
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
        add_edge(RouterEdge(org, org_hubs["airport"], "Bus", "UPSRTC Express", 250, 2.5, "07:30", "10:00", 0.15, 20.0, 18.0, "Non-refundable"))

    # Destination Airport -> Destination
    add_edge(RouterEdge(dst_hubs["airport"], dst, "Cab", "Uber/Ola", 750, 1.0, "15:00", "16:00", 0.10, 10.0, 30.0, "Refundable"))
    add_edge(RouterEdge(dst_hubs["airport"], dst, "Metro", "Local Metro", 60, 0.9, "15:10", "16:04", 0.02, 2.0, 2.7, "Refundable"))

    # Destination Station -> Destination
    add_edge(RouterEdge(dst_hubs["station"], dst, "Cab", "Auto Rickshaw / Taxi", 150, 0.4, "12:00", "12:24", 0.05, 5.0, 8.0, "Refundable"))
    add_edge(RouterEdge(dst_hubs["station"], dst, "Metro", "Local Metro", 30, 0.3, "12:00", "12:18", 0.01, 1.0, 0.9, "Refundable"))

    # 3. Add Long Distance Travel options
    
    # 3. Add Long Distance Travel options via Live Travel API Service
    from .live_travel_api import live_travel_service

    # Live Flights (Airport -> Airport)
    live_flights = live_travel_service.fetch_live_flights(org, dst)
    for f in live_flights:
        add_edge(RouterEdge(
            org_hubs["airport"], dst_hubs["airport"],
            "Flight", f["provider"],
            f["price"], 2.2, f["departure_time"], f["arrival_time"],
            f["delay_prob"], f["avg_delay"], f.get("carbon", 130.0),
            "Refundable" if "Air India" in f["provider"] else "Non-refundable"
        ))

    # Connecting Flights via DEL
    if org_hubs["airport_code"] != "DEL" and dst_hubs["airport_code"] != "DEL":
        add_edge(RouterEdge(
            org_hubs["airport"], connecting_airport,
            "Flight", "IndiGo 6E-6101",
            3000, 1.2, "10:00", "11:12",
            0.05, 8.0, 90.0, "Non-refundable"
        ))
        add_edge(RouterEdge(
            connecting_airport, dst_hubs["airport"],
            "Flight", "IndiGo 6E-2401",
            3500, 2.0, "13:30", "15:30",
            0.09, 14.0, 160.0, "Non-refundable"
        ))

    # Live Trains (Station -> Station)
    live_trains = live_travel_service.fetch_live_trains(org, dst)
    for t in live_trains:
        add_edge(RouterEdge(
            org_hubs["station"], dst_hubs["station"],
            "Train", f"{t['provider']} ({t.get('seat_class', 'Sleeper')})",
            t["price"], t.get("duration", 12.0), t["departure_time"], t["arrival_time"],
            t["delay_prob"], t["avg_delay"], t.get("carbon", 40.0),
            "Refundable"
        ))

    # Intercity Direct Buses (Origin -> Destination)
    add_edge(RouterEdge(
        org, dst,
        "Bus", "KSRTC / Zingbus Sleeper",
        1200, 14.0, "18:00", "08:00",
        0.20, 30.0, 75.0, "Partial Refund"
    ))

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
