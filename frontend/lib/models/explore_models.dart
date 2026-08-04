class AttractionStop {
  final String id;
  final String name;
  final String category;
  final double lat;
  final double lng;
  final String address;
  final int visitDurationMins;
  final double estimatedCost;
  final int travelTimeFromPrevMins;
  final String travelModeFromPrev;
  final String scheduledTime;
  final String aiReasoning;
  final int aiScore;
  final String imageUrl;
  final String description;
  final String historySummary;
  final List<String> facts;
  final String architecture;
  final String culturalImportance;
  final String entryFee;
  final String openingHours;
  final String bestVisitingTime;
  final String photoTips;
  final String safetyTips;
  final String accessibility;
  final Map<String, dynamic> nearbyAmenities;
  final Map<String, double> spendingEstimate;

  AttractionStop({
    required this.id,
    required this.name,
    required this.category,
    required this.lat,
    required this.lng,
    required this.address,
    required this.visitDurationMins,
    required this.estimatedCost,
    required this.travelTimeFromPrevMins,
    required this.travelModeFromPrev,
    required this.scheduledTime,
    required this.aiReasoning,
    required this.aiScore,
    required this.imageUrl,
    required this.description,
    required this.historySummary,
    required this.facts,
    required this.architecture,
    required this.culturalImportance,
    required this.entryFee,
    required this.openingHours,
    required this.bestVisitingTime,
    required this.photoTips,
    required this.safetyTips,
    required this.accessibility,
    required this.nearbyAmenities,
    required this.spendingEstimate,
  });

  factory AttractionStop.fromJson(Map<String, dynamic> json) {
    return AttractionStop(
      id: json['id'] ?? '',
      name: json['name'] ?? 'Attraction',
      category: json['category'] ?? 'Sightseeing',
      lat: (json['lat'] ?? 0.0).toDouble(),
      lng: (json['lng'] ?? 0.0).toDouble(),
      address: json['address'] ?? '',
      visitDurationMins: json['visit_duration_mins'] ?? 60,
      estimatedCost: (json['estimated_cost'] ?? 0.0).toDouble(),
      travelTimeFromPrevMins: json['travel_time_from_prev_mins'] ?? 15,
      travelModeFromPrev: json['travel_mode_from_prev'] ?? 'Walking',
      scheduledTime: json['scheduled_time'] ?? '10:00 AM',
      aiReasoning: json['ai_reasoning'] ?? 'Optimal timing and low morning crowd.',
      aiScore: json['ai_score'] ?? 95,
      imageUrl: json['image_url'] ?? '',
      description: json['description'] ?? '',
      historySummary: json['history_summary'] ?? '',
      facts: (json['facts'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      architecture: json['architecture'] ?? '',
      culturalImportance: json['cultural_importance'] ?? '',
      entryFee: json['entry_fee'] ?? 'Free',
      openingHours: json['opening_hours'] ?? '9:00 AM - 6:00 PM',
      bestVisitingTime: json['best_visiting_time'] ?? 'Morning',
      photoTips: json['photo_tips'] ?? '',
      safetyTips: json['safety_tips'] ?? '',
      accessibility: json['accessibility'] ?? 'Wheelchair Accessible',
      nearbyAmenities: (json['nearby_amenities'] as Map?)?.map((k, v) => MapEntry(k.toString(), v)) ?? {},
      spendingEstimate: (json['spending_estimate'] as Map?)?.map((k, v) => MapEntry(k.toString(), (v as num).toDouble())) ?? {},
    );
  }
}

class EmergencyLocation {
  final String id;
  final String name;
  final String category;
  final double lat;
  final double lng;
  final String address;
  final String phone;
  final double distanceKm;
  final bool open24h;

  EmergencyLocation({
    required this.id,
    required this.name,
    required this.category,
    required this.lat,
    required this.lng,
    required this.address,
    required this.phone,
    required this.distanceKm,
    required this.open24h,
  });

  factory EmergencyLocation.fromJson(Map<String, dynamic> json) {
    return EmergencyLocation(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      category: json['category'] ?? 'Emergency',
      lat: (json['lat'] ?? 0.0).toDouble(),
      lng: (json['lng'] ?? 0.0).toDouble(),
      address: json['address'] ?? '',
      phone: json['phone'] ?? '112',
      distanceKm: (json['distance_km'] ?? 0.0).toDouble(),
      open24h: json['open_24h'] ?? true,
    );
  }
}

class ExploreMission {
  final String id;
  final String title;
  final String icon;
  final String description;
  final String trailCategory;
  final double estimatedHours;
  final double estimatedCost;
  final int recommendedStopsCount;

  ExploreMission({
    required this.id,
    required this.title,
    required this.icon,
    required this.description,
    required this.trailCategory,
    required this.estimatedHours,
    required this.estimatedCost,
    required this.recommendedStopsCount,
  });

  factory ExploreMission.fromJson(Map<String, dynamic> json) {
    return ExploreMission(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      icon: json['icon'] ?? 'star',
      description: json['description'] ?? '',
      trailCategory: json['trail_category'] ?? 'General',
      estimatedHours: (json['estimated_hours'] ?? 4.0).toDouble(),
      estimatedCost: (json['estimated_cost'] ?? 500.0).toDouble(),
      recommendedStopsCount: json['recommended_stops_count'] ?? 4,
    );
  }
}

class ExploreItinerary {
  final String location;
  final double lat;
  final double lng;
  final int totalStops;
  final double totalHours;
  final double totalCost;
  final double remainingBudget;
  final List<AttractionStop> stops;
  final List<Map<String, dynamic>> timeBlockedSchedule;
  final List<String> multiTransportMix;
  final List<AttractionStop> hiddenGems;
  final List<Map<String, dynamic>> photoSpots;
  final List<Map<String, dynamic>> foodRecommendations;
  final List<Map<String, dynamic>> shoppingRecommendations;
  final bool waitingForApiCredentials;
  final String? apiCredentialsMessage;

  ExploreItinerary({
    required this.location,
    this.lat = 28.6139,
    this.lng = 77.2090,
    required this.totalStops,
    required this.totalHours,
    required this.totalCost,
    required this.remainingBudget,
    required this.stops,
    required this.timeBlockedSchedule,
    required this.multiTransportMix,
    required this.hiddenGems,
    required this.photoSpots,
    required this.foodRecommendations,
    required this.shoppingRecommendations,
    required this.waitingForApiCredentials,
    this.apiCredentialsMessage,
  });

  factory ExploreItinerary.fromJson(Map<String, dynamic> json) {
    return ExploreItinerary(
      location: json['location'] ?? 'Destination',
      lat: (json['lat'] ?? 28.6139).toDouble(),
      lng: (json['lng'] ?? 77.2090).toDouble(),
      totalStops: json['total_stops'] ?? 0,
      totalHours: (json['total_hours'] ?? 0.0).toDouble(),
      totalCost: (json['total_cost'] ?? 0.0).toDouble(),
      remainingBudget: (json['remaining_budget'] ?? 0.0).toDouble(),
      stops: (json['stops'] as List<dynamic>?)?.map((e) => AttractionStop.fromJson(e as Map<String, dynamic>)).toList() ?? [],
      timeBlockedSchedule: (json['time_blocked_schedule'] as List<dynamic>?)?.map((e) => Map<String, dynamic>.from(e as Map)).toList() ?? [],
      multiTransportMix: (json['multi_transport_mix'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      hiddenGems: (json['hidden_gems'] as List<dynamic>?)?.map((e) => AttractionStop.fromJson(e as Map<String, dynamic>)).toList() ?? [],
      photoSpots: (json['photo_spots'] as List<dynamic>?)?.map((e) => Map<String, dynamic>.from(e as Map)).toList() ?? [],
      foodRecommendations: (json['food_recommendations'] as List<dynamic>?)?.map((e) => Map<String, dynamic>.from(e as Map)).toList() ?? [],
      shoppingRecommendations: (json['shopping_recommendations'] as List<dynamic>?)?.map((e) => Map<String, dynamic>.from(e as Map)).toList() ?? [],
      waitingForApiCredentials: json['waiting_for_api_credentials'] ?? false,
      apiCredentialsMessage: json['api_credentials_message'],
    );
  }
}
