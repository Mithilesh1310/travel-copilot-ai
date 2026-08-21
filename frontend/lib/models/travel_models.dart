import 'dart:convert';

class ItineraryLeg {
  final int? id;
  final String transportType;
  final String provider;
  final String origin;
  final String destination;
  final String departureTime;
  final String arrivalTime;
  final double price;
  final double duration;
  final double delayProbability;
  final double averageDelay;
  final String refundability;
  final String seatClass;
  final double carbonFootprint;
  final String? bookingLink;
  final Map<String, dynamic> hiddenCosts;

  ItineraryLeg({
    this.id,
    required this.transportType,
    required this.provider,
    required this.origin,
    required this.destination,
    required this.departureTime,
    required this.arrivalTime,
    required this.price,
    required this.duration,
    required this.delayProbability,
    required this.averageDelay,
    required this.refundability,
    required this.seatClass,
    required this.carbonFootprint,
    this.bookingLink,
    required this.hiddenCosts,
  });

  factory ItineraryLeg.fromJson(Map<String, dynamic> json) {
    Map<String, dynamic> parsedCosts = {};
    if (json['hidden_costs'] != null) {
      if (json['hidden_costs'] is String) {
        try {
          parsedCosts = jsonDecode(json['hidden_costs']);
        } catch (_) {
          parsedCosts = {};
        }
      } else if (json['hidden_costs'] is Map) {
        parsedCosts = Map<String, dynamic>.from(json['hidden_costs']);
      }
    }

    return ItineraryLeg(
      id: json['id'],
      transportType: json['transport_type'] ?? 'Transport',
      provider: json['provider'] ?? 'Service Provider',
      origin: json['origin'] ?? '',
      destination: json['destination'] ?? '',
      departureTime: json['departure_time'] ?? '',
      arrivalTime: json['arrival_time'] ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      duration: (json['duration'] as num?)?.toDouble() ?? 0.0,
      delayProbability: (json['delay_probability'] as num?)?.toDouble() ?? 0.0,
      averageDelay: (json['average_delay'] as num?)?.toDouble() ?? 0.0,
      refundability: json['refundability'] ?? 'Non-refundable',
      seatClass: json['seat_class'] ?? 'Standard',
      carbonFootprint: (json['carbon_footprint'] as num?)?.toDouble() ?? 0.0,
      bookingLink: json['booking_link'],
      hiddenCosts: parsedCosts,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'transport_type': transportType,
        'provider': provider,
        'origin': origin,
        'destination': destination,
        'departure_time': departureTime,
        'arrival_time': arrivalTime,
        'price': price,
        'duration': duration,
        'delay_probability': delayProbability,
        'average_delay': averageDelay,
        'refundability': refundability,
        'seat_class': seatClass,
        'carbon_footprint': carbonFootprint,
        'booking_link': bookingLink,
        'hidden_costs': jsonEncode(hiddenCosts),
      };
}

class PricePrediction {
  final String indicator;
  final int confidence;
  final String explanation;
  final List<double> historicalTrend;

  PricePrediction({
    required this.indicator,
    required this.confidence,
    required this.explanation,
    required this.historicalTrend,
  });

  factory PricePrediction.fromJson(Map<String, dynamic> json) {
    return PricePrediction(
      indicator: json['indicator'] ?? 'Buy Now',
      confidence: json['confidence'] ?? 80,
      explanation: json['explanation'] ?? 'Stable prices expected.',
      historicalTrend: (json['historical_trend'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [4500.0, 4400.0, 4300.0, 4200.0, 4100.0, 4000.0],
    );
  }
}

class DelayPrediction {
  final String airportCongestion;
  final String weatherImpact;
  final double averageDelay;

  DelayPrediction({
    required this.airportCongestion,
    required this.weatherImpact,
    required this.averageDelay,
  });

  factory DelayPrediction.fromJson(Map<String, dynamic> json) {
    return DelayPrediction(
      airportCongestion: json['airport_congestion'] ?? 'Low',
      weatherImpact: json['weather_impact'] ?? 'Clear',
      averageDelay: (json['average_delay'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ExplanationDetails {
  final String whySelected;
  final List<String> pros;
  final List<String> cons;
  final String tradeOffs;
  final double moneySaved;
  final int timeSavedMins;

  ExplanationDetails({
    required this.whySelected,
    required this.pros,
    required this.cons,
    required this.tradeOffs,
    required this.moneySaved,
    required this.timeSavedMins,
  });

  factory ExplanationDetails.fromJson(Map<String, dynamic> json) {
    return ExplanationDetails(
      whySelected: json['why_selected'] ?? '',
      pros: (json['pros'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      cons: (json['cons'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      tradeOffs: json['trade_offs'] ?? '',
      moneySaved: (json['money_saved'] as num?)?.toDouble() ?? 0.0,
      timeSavedMins: json['time_saved_mins'] ?? 0,
    );
  }
}

class Itinerary {
  final int? id;
  final String type;
  final double totalPrice;
  final double totalDuration;
  final double carbonFootprint;
  final double reliabilityScore;
  final double delayProbability;
  final double averageDelay;
  final double comfortScore;
  final String? aiExplanation;
  final List<ItineraryLeg> legs;
  final bool isSaved;
  final PricePrediction? pricePrediction;
  final DelayPrediction? delayPrediction;
  final ExplanationDetails? explanationDetails;

  Itinerary({
    this.id,
    required this.type,
    required this.totalPrice,
    required this.totalDuration,
    required this.carbonFootprint,
    required this.reliabilityScore,
    required this.delayProbability,
    required this.averageDelay,
    this.comfortScore = 8.5,
    this.aiExplanation,
    required this.legs,
    this.isSaved = false,
    this.pricePrediction,
    this.delayPrediction,
    this.explanationDetails,
  });

  factory Itinerary.fromJson(Map<String, dynamic> json) {
    return Itinerary(
      id: json['id'],
      type: json['type'] ?? 'Recommendation',
      totalPrice: (json['total_price'] as num?)?.toDouble() ?? 0.0,
      totalDuration: (json['total_duration'] as num?)?.toDouble() ?? 0.0,
      carbonFootprint: (json['carbon_footprint'] as num?)?.toDouble() ?? 0.0,
      reliabilityScore: (json['reliability_score'] as num?)?.toDouble() ?? 95.0,
      delayProbability: (json['delay_probability'] as num?)?.toDouble() ?? 0.0,
      averageDelay: (json['average_delay'] as num?)?.toDouble() ?? 0.0,
      comfortScore: (json['comfort_score'] as num?)?.toDouble() ?? 8.5,
      aiExplanation: json['ai_explanation'],
      legs: (json['legs'] as List<dynamic>?)
              ?.map((e) => ItineraryLeg.fromJson(e))
              .toList() ??
          [],
      isSaved: json['is_saved'] ?? false,
      pricePrediction: json['price_prediction'] != null
          ? PricePrediction.fromJson(json['price_prediction'])
          : null,
      delayPrediction: json['delay_prediction'] != null
          ? DelayPrediction.fromJson(json['delay_prediction'])
          : null,
      explanationDetails: json['explanation_details'] != null
          ? ExplanationDetails.fromJson(json['explanation_details'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'total_price': totalPrice,
        'total_duration': totalDuration,
        'carbon_footprint': carbonFootprint,
        'reliability_score': reliabilityScore,
        'delay_probability': delayProbability,
        'average_delay': averageDelay,
        'ai_explanation': aiExplanation,
        'legs': legs.map((l) => l.toJson()).toList(),
        'is_saved': isSaved,
      };
}

class ChatMessage {
  final String text;
  final bool isBot;
  final List<String> followUps;
  final List<Itinerary> itineraries;
  final DateTime timestamp;

  ChatMessage({
    required this.text,
    required this.isBot,
    this.followUps = const [],
    this.itineraries = const [],
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class UserAnalytics {
  final double moneySaved;
  final double hoursSaved;
  final double co2Saved;
  final String favoriteAirline;
  final String favoriteTransport;
  final int tripsCompleted;
  final List<Map<String, dynamic>> monthlySpending;

  UserAnalytics({
    required this.moneySaved,
    required this.hoursSaved,
    required this.co2Saved,
    required this.favoriteAirline,
    required this.favoriteTransport,
    required this.tripsCompleted,
    required this.monthlySpending,
  });

  factory UserAnalytics.fromJson(Map<String, dynamic> json) {
    return UserAnalytics(
      moneySaved: (json['money_saved'] as num?)?.toDouble() ?? 0.0,
      hoursSaved: (json['hours_saved'] as num?)?.toDouble() ?? 0.0,
      co2Saved: (json['co2_saved'] as num?)?.toDouble() ?? 0.0,
      favoriteAirline: json['favorite_airline'] ?? 'IndiGo',
      favoriteTransport: json['favorite_transport'] ?? 'Flight',
      tripsCompleted: json['trips_completed'] ?? 0,
      monthlySpending: (json['monthly_spending'] as List<dynamic>?)
              ?.map((e) => Map<String, dynamic>.from(e))
              .toList() ??
          [],
    );
  }
}

class NotificationItem {
  final int id;
  final String type;
  final String title;
  final String message;
  final bool isRead;
  final String createdAt;

  NotificationItem({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.isRead,
    required this.createdAt,
  });

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      id: json['id'],
      type: json['type'],
      title: json['title'],
      message: json['message'],
      isRead: json['is_read'],
      createdAt: json['created_at'],
    );
  }
}

class BudgetAllocation {
  final String category;
  final double amount;
  final double percentage;
  final String status;
  final String reason;

  BudgetAllocation({
    required this.category,
    required this.amount,
    required this.percentage,
    required this.status,
    required this.reason,
  });

  factory BudgetAllocation.fromJson(Map<String, dynamic> json) {
    return BudgetAllocation(
      category: json['category'] ?? 'Category',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      percentage: (json['percentage'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] ?? 'Good',
      reason: json['reason'] ?? '',
    );
  }
}

class SavingSuggestion {
  final String title;
  final double savings;
  final String category;

  SavingSuggestion({
    required this.title,
    required this.savings,
    required this.category,
  });

  factory SavingSuggestion.fromJson(Map<String, dynamic> json) {
    return SavingSuggestion(
      title: json['title'] ?? '',
      savings: (json['savings'] as num?)?.toDouble() ?? 0.0,
      category: json['category'] ?? 'General',
    );
  }
}

class PaymentOptimization {
  final String provider;
  final double savings;
  final String type;

  PaymentOptimization({
    required this.provider,
    required this.savings,
    required this.type,
  });

  factory PaymentOptimization.fromJson(Map<String, dynamic> json) {
    return PaymentOptimization(
      provider: json['provider'] ?? '',
      savings: (json['savings'] as num?)?.toDouble() ?? 0.0,
      type: json['type'] ?? 'Offer',
    );
  }
}

class HotelItem {
  final String name;
  final double pricePerNight;
  final String rating;
  final String link;

  HotelItem({
    required this.name,
    required this.pricePerNight,
    required this.rating,
    required this.link,
  });

  factory HotelItem.fromJson(Map<String, dynamic> json) {
    return HotelItem(
      name: json['name'] ?? 'Hotel',
      pricePerNight: (json['price_per_night'] as num?)?.toDouble() ?? 2500.0,
      rating: json['rating'] ?? '4.2 Stars',
      link: json['link'] ?? 'https://www.google.com/travel/hotels',
    );
  }
}

class HotelOptimization {
  final String currentName;
  final double currentPrice;
  final String currentRating;
  final String recommendedName;
  final double recommendedPrice;
  final String recommendedRating;
  final String distanceDifference;
  final double savingsPerNight;

  HotelOptimization({
    required this.currentName,
    required this.currentPrice,
    required this.currentRating,
    required this.recommendedName,
    required this.recommendedPrice,
    required this.recommendedRating,
    required this.distanceDifference,
    required this.savingsPerNight,
  });

  factory HotelOptimization.fromJson(Map<String, dynamic> json) {
    return HotelOptimization(
      currentName: json['current_name'] ?? 'Current Hotel',
      currentPrice: (json['current_price'] as num?)?.toDouble() ?? 3500.0,
      currentRating: json['current_rating'] ?? '4.2 ★',
      recommendedName: json['recommended_name'] ?? 'Recommended Hotel',
      recommendedPrice: (json['recommended_price'] as num?)?.toDouble() ?? 2700.0,
      recommendedRating: json['recommended_rating'] ?? '4.3 ★',
      distanceDifference: json['distance_difference'] ?? '400m',
      savingsPerNight: (json['savings_per_night'] as num?)?.toDouble() ?? 800.0,
    );
  }
}

class DailyBudgetBreakdown {
  final String day;
  final double amount;
  final String highlights;

  DailyBudgetBreakdown({
    required this.day,
    required this.amount,
    required this.highlights,
  });

  factory DailyBudgetBreakdown.fromJson(Map<String, dynamic> json) {
    return DailyBudgetBreakdown(
      day: json['day'] ?? 'Day',
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      highlights: json['highlights'] ?? '',
    );
  }
}

class HiddenExpenses {
  final double airportTax;
  final double seatSelection;
  final double extraBaggage;
  final double meals;
  final double gst;
  final double totalHiddenCost;

  HiddenExpenses({
    required this.airportTax,
    required this.seatSelection,
    required this.extraBaggage,
    required this.meals,
    required this.gst,
    required this.totalHiddenCost,
  });

  factory HiddenExpenses.fromJson(Map<String, dynamic> json) {
    return HiddenExpenses(
      airportTax: (json['airport_tax'] as num?)?.toDouble() ?? 650.0,
      seatSelection: (json['seat_selection'] as num?)?.toDouble() ?? 300.0,
      extraBaggage: (json['extra_baggage'] as num?)?.toDouble() ?? 900.0,
      meals: (json['meals'] as num?)?.toDouble() ?? 450.0,
      gst: (json['gst'] as num?)?.toDouble() ?? 1200.0,
      totalHiddenCost: (json['total_hidden_cost'] as num?)?.toDouble() ?? 3500.0,
    );
  }
}

class BudgetOptimizationResult {
  final String beforeItem;
  final double beforeCost;
  final String afterItem;
  final double afterCost;
  final double savings;
  final String explanation;

  BudgetOptimizationResult({
    required this.beforeItem,
    required this.beforeCost,
    required this.afterItem,
    required this.afterCost,
    required this.savings,
    required this.explanation,
  });

  factory BudgetOptimizationResult.fromJson(Map<String, dynamic> json) {
    return BudgetOptimizationResult(
      beforeItem: json['before_item'] ?? 'Standard Booking',
      beforeCost: (json['before_cost'] as num?)?.toDouble() ?? 45000.0,
      afterItem: json['after_item'] ?? 'Optimized Booking',
      afterCost: (json['after_cost'] as num?)?.toDouble() ?? 40800.0,
      savings: (json['savings'] as num?)?.toDouble() ?? 4200.0,
      explanation: json['explanation'] ?? '',
    );
  }
}

class ExactDestinationInfo {
  final String exactName;
  final String formattedAddress;
  final double lat;
  final double lng;
  final String city;

  ExactDestinationInfo({
    required this.exactName,
    required this.formattedAddress,
    required this.lat,
    required this.lng,
    required this.city,
  });

  factory ExactDestinationInfo.fromJson(Map<String, dynamic> json) {
    return ExactDestinationInfo(
      exactName: json['exact_name'] ?? json['name'] ?? 'Destination',
      formattedAddress: json['formatted_address'] ?? json['address'] ?? '',
      lat: (json['lat'] as num?)?.toDouble() ?? 26.8467,
      lng: (json['lng'] as num?)?.toDouble() ?? 80.9467,
      city: json['city'] ?? 'Destination City',
    );
  }
}

class RecommendedHotelItem {
  final String id;
  final String name;
  final double lat;
  final double lng;
  final String distanceKm;
  final String rating;
  final double pricePerNight;
  final double totalStayCost;
  final String aiReason;
  final String bookingLink;

  RecommendedHotelItem({
    required this.id,
    required this.name,
    required this.lat,
    required this.lng,
    required this.distanceKm,
    required this.rating,
    required this.pricePerNight,
    required this.totalStayCost,
    required this.aiReason,
    required this.bookingLink,
  });

  factory RecommendedHotelItem.fromJson(Map<String, dynamic> json) {
    return RecommendedHotelItem(
      id: json['id'] ?? 'hotel_${DateTime.now().millisecondsSinceEpoch}',
      name: json['name'] ?? 'Recommended Hotel',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lng: (json['lng'] as num?)?.toDouble() ?? 0.0,
      distanceKm: json['distance_km'] ?? json['distance'] ?? '1.2 km',
      rating: json['rating']?.toString() ?? '4.2',
      pricePerNight: (json['price_per_night'] as num?)?.toDouble() ?? 2500.0,
      totalStayCost: (json['total_stay_cost'] as num?)?.toDouble() ?? 7500.0,
      aiReason: json['ai_reason'] ?? json['reason'] ?? 'Recommended for your budget',
      bookingLink: json['booking_link'] ?? '',
    );
  }
}

class RecommendedPlaceItem {
  final String id;
  final String name;
  final String category;
  final double lat;
  final double lng;
  final String distanceKm;
  final double estimatedCost;
  final String visitDuration;
  final String aiReason;

  RecommendedPlaceItem({
    required this.id,
    required this.name,
    required this.category,
    required this.lat,
    required this.lng,
    required this.distanceKm,
    required this.estimatedCost,
    required this.visitDuration,
    required this.aiReason,
  });

  factory RecommendedPlaceItem.fromJson(Map<String, dynamic> json) {
    return RecommendedPlaceItem(
      id: json['id'] ?? 'place_${DateTime.now().millisecondsSinceEpoch}',
      name: json['name'] ?? 'Attraction Spot',
      category: json['category'] ?? 'Sightseeing',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lng: (json['lng'] as num?)?.toDouble() ?? 0.0,
      distanceKm: json['distance_km'] ?? '2.0 km',
      estimatedCost: (json['estimated_cost'] as num?)?.toDouble() ?? 0.0,
      visitDuration: json['visit_duration'] ?? '1-2 hrs',
      aiReason: json['ai_reason'] ?? 'Must-visit place near destination',
    );
  }
}

class JourneyRouteStopItem {
  final String id;
  final String name;
  final String category;
  final double lat;
  final double lng;
  final String distanceFromOrigin;
  final String aiReason;

  JourneyRouteStopItem({
    required this.id,
    required this.name,
    required this.category,
    required this.lat,
    required this.lng,
    required this.distanceFromOrigin,
    required this.aiReason,
  });

  factory JourneyRouteStopItem.fromJson(Map<String, dynamic> json) {
    return JourneyRouteStopItem(
      id: json['id'] ?? 'stop_${DateTime.now().millisecondsSinceEpoch}',
      name: json['name'] ?? 'Route Stop',
      category: json['category'] ?? 'Scenic Stop',
      lat: (json['lat'] as num?)?.toDouble() ?? 0.0,
      lng: (json['lng'] as num?)?.toDouble() ?? 0.0,
      distanceFromOrigin: json['distance_from_origin'] ?? '50 km',
      aiReason: json['ai_reason'] ?? 'Recommended travel break point',
    );
  }
}

class AIBudgetAnalysisReport {
  final double totalBudget;
  final double recommendedBudget;
  final double estimatedSavings;
  final String budgetHealth;
  final double healthPercentage;
  final int aiConfidence;
  final String aiExplanation;
  final List<BudgetAllocation> allocations;
  final List<SavingSuggestion> savingsSuggestions;
  final double potentialSavings;
  final bool isOverBudget;
  final double extraRequired;
  final List<SavingSuggestion> overBudgetSuggestions;
  final List<PaymentOptimization> paymentOptimizations;
  final HotelOptimization hotelOptimization;
  final List<DailyBudgetBreakdown> dailyBreakdown;
  final HiddenExpenses hiddenExpenses;
  final double emergencyReserve;
  final double currentPlanCost;
  final double optimizedPlanCost;
  final double totalPlanSavings;
  final int aiScore;
  final List<String> scoreReasons;
  final String scenarioHigher;
  final String scenarioLower;
  final BudgetOptimizationResult? optimizationResult;
  final ExactDestinationInfo? exactDestination;
  final String aiDestinationSummary;
  final List<RecommendedHotelItem> recommendedHotelsList;
  final List<RecommendedPlaceItem> placesToVisitList;
  final List<JourneyRouteStopItem> journeyRouteStops;

  AIBudgetAnalysisReport({
    required this.totalBudget,
    required this.recommendedBudget,
    required this.estimatedSavings,
    required this.budgetHealth,
    required this.healthPercentage,
    required this.aiConfidence,
    required this.aiExplanation,
    required this.allocations,
    required this.savingsSuggestions,
    required this.potentialSavings,
    required this.isOverBudget,
    required this.extraRequired,
    required this.overBudgetSuggestions,
    required this.paymentOptimizations,
    required this.hotelOptimization,
    required this.dailyBreakdown,
    required this.hiddenExpenses,
    required this.emergencyReserve,
    required this.currentPlanCost,
    required this.optimizedPlanCost,
    required this.totalPlanSavings,
    required this.aiScore,
    required this.scoreReasons,
    required this.scenarioHigher,
    required this.scenarioLower,
    this.optimizationResult,
    this.exactDestination,
    this.aiDestinationSummary = '',
    this.recommendedHotelsList = const [],
    this.placesToVisitList = const [],
    this.journeyRouteStops = const [],
  });

  factory AIBudgetAnalysisReport.fromJson(Map<String, dynamic> json) {
    return AIBudgetAnalysisReport(
      totalBudget: (json['total_budget'] as num?)?.toDouble() ?? 45000.0,
      recommendedBudget: (json['recommended_budget'] as num?)?.toDouble() ?? 43200.0,
      estimatedSavings: (json['estimated_savings'] as num?)?.toDouble() ?? 1800.0,
      budgetHealth: json['budget_health'] ?? 'Excellent',
      healthPercentage: (json['health_percentage'] as num?)?.toDouble() ?? 96.0,
      aiConfidence: json['ai_confidence'] ?? 95,
      aiExplanation: json['ai_explanation'] ?? '',
      allocations: (json['allocations'] as List<dynamic>?)
              ?.map((e) => BudgetAllocation.fromJson(e))
              .toList() ??
          [],
      savingsSuggestions: (json['savings_suggestions'] as List<dynamic>?)
              ?.map((e) => SavingSuggestion.fromJson(e))
              .toList() ??
          [],
      potentialSavings: (json['potential_savings'] as num?)?.toDouble() ?? 6150.0,
      isOverBudget: json['is_over_budget'] ?? false,
      extraRequired: (json['extra_required'] as num?)?.toDouble() ?? 0.0,
      overBudgetSuggestions: (json['over_budget_suggestions'] as List<dynamic>?)
              ?.map((e) => SavingSuggestion.fromJson(e))
              .toList() ??
          [],
      paymentOptimizations: (json['payment_optimizations'] as List<dynamic>?)
              ?.map((e) => PaymentOptimization.fromJson(e))
              .toList() ??
          [],
      hotelOptimization: HotelOptimization.fromJson(json['hotel_optimization'] ?? {}),
      dailyBreakdown: (json['daily_breakdown'] as List<dynamic>?)
              ?.map((e) => DailyBudgetBreakdown.fromJson(e))
              .toList() ??
          [],
      hiddenExpenses: HiddenExpenses.fromJson(json['hidden_expenses'] ?? {}),
      emergencyReserve: (json['emergency_reserve'] as num?)?.toDouble() ?? 2250.0,
      currentPlanCost: (json['current_plan_cost'] as num?)?.toDouble() ?? 43200.0,
      optimizedPlanCost: (json['optimized_plan_cost'] as num?)?.toDouble() ?? 39000.0,
      totalPlanSavings: (json['total_plan_savings'] as num?)?.toDouble() ?? 4200.0,
      aiScore: json['ai_score'] ?? 94,
      scoreReasons: (json['score_reasons'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      scenarioHigher: json['optimization_scenario_higher'] ?? '',
      scenarioLower: json['optimization_scenario_lower'] ?? '',
      optimizationResult: json['optimization_result'] != null
          ? BudgetOptimizationResult.fromJson(json['optimization_result'])
          : null,
      exactDestination: json['exact_destination'] != null
          ? ExactDestinationInfo.fromJson(json['exact_destination'])
          : null,
      aiDestinationSummary: json['ai_destination_summary'] ?? '',
      recommendedHotelsList: (json['recommended_hotels'] as List<dynamic>?)
              ?.map((e) => RecommendedHotelItem.fromJson(e))
              .toList() ??
          [],
      placesToVisitList: (json['places_to_visit'] as List<dynamic>?)
              ?.map((e) => RecommendedPlaceItem.fromJson(e))
              .toList() ??
          [],
      journeyRouteStops: (json['route_stops'] as List<dynamic>?)
              ?.map((e) => JourneyRouteStopItem.fromJson(e))
              .toList() ??
          [],
    );
  }
}
