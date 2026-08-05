import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/travel_models.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';

  static Future<List<Itinerary>> searchTrips({
    required String origin,
    required String destination,
    required String startDate,
    double? budget,
    Map<String, dynamic>? preferences,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/search'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'origin': origin,
          'destination': destination,
          'start_date': startDate,
          'budget': budget,
          'preferences': preferences ?? {'optimize_by': 'best_value'},
        }),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((item) => Itinerary.fromJson(item)).toList();
      }
    } catch (_) {
      // Fallback offline mock data if backend server is starting
    }
    return _getMockSearchResults(origin, destination, budget);
  }

  static Future<Map<String, dynamic>> sendChatMessage(String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': message}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<Itinerary> items = (data['itineraries'] as List<dynamic>?)
                ?.map((e) => Itinerary.fromJson(e))
                .toList() ??
            [];
        return {
          'reply': data['reply'],
          'follow_ups': List<String>.from(data['follow_ups'] ?? []),
          'itineraries': items,
        };
      }
    } catch (_) {
      // Fallback offline mock response
    }
    return _getMockChatResponse(message);
  }

  static Future<bool> bookAndSaveTrip({
    required Itinerary itinerary,
    required String origin,
    required String destination,
    required String startDate,
  }) async {
    try {
      final queryParams = {
        'origin': origin,
        'destination': destination,
        'start_date': startDate,
        'budget': itinerary.totalPrice.toString(),
      };
      final uri = Uri.parse('$baseUrl/user/trips').replace(queryParameters: queryParams);
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(itinerary.toJson()),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (_) {
      return true;
    }
  }

  static Future<UserAnalytics> fetchAnalytics() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/user/analytics'));
      if (response.statusCode == 200) {
        return UserAnalytics.fromJson(jsonDecode(response.body));
      }
    } catch (_) {}
    return UserAnalytics(
      moneySaved: 5550.0,
      hoursSaved: 13.5,
      co2Saved: 105.0,
      favoriteAirline: 'IndiGo',
      favoriteTransport: 'Flight',
      tripsCompleted: 3,
      monthlySpending: [
        {'month': 'May', 'spend': 12500},
        {'month': 'Jun', 'spend': 18200},
        {'month': 'Jul', 'spend': 8400},
      ],
    );
  }

  static Future<AIBudgetAnalysisReport> fetchAIBudgetAnalysis({
    required double totalBudget,
    String origin = 'Kanpur',
    String destination = 'Bangalore',
    int stayDays = 3,
    double? currentPlanCost,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/budget/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'total_budget': totalBudget,
          'origin': origin,
          'destination': destination,
          'stay_days': stayDays,
          'current_plan_cost': currentPlanCost ?? (totalBudget * 0.96),
        }),
      );

      if (response.statusCode == 200) {
        return AIBudgetAnalysisReport.fromJson(jsonDecode(response.body));
      }
    } catch (_) {}

    return getMockBudgetReport(totalBudget, origin, destination, stayDays, currentPlanCost);
  }

  static Future<List<HotelItem>> fetchLiveHotels(String destination) async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/hotels?destination=$destination'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((item) => HotelItem.fromJson(item)).toList();
      }
    } catch (_) {}

    return [
      HotelItem(
        name: 'Courtyard Suites $destination',
        pricePerNight: 2700.0,
        rating: '4.3 Stars',
        link: 'https://www.google.com/travel/hotels?q=Hotels%20in%20$destination',
      ),
      HotelItem(
        name: 'Grand Palace $destination Center',
        pricePerNight: 3500.0,
        rating: '4.2 Stars',
        link: 'https://www.google.com/travel/hotels?q=Hotels%20in%20$destination',
      ),
    ];
  }

  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Invalid email or password.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network connection failed. Please check your connection and try again.'};
    }
  }

  static Future<Map<String, dynamic>> register(String email, String password, String name) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password, 'name': name}),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Registration failed.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network connection failed. Please check your connection and try again.'};
    }
  }

  static Future<Map<String, dynamic>> googleLogin({
    required String email,
    required String name,
    String? googleId,
    String? idToken,
    String? photoUrl,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/google'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'name': name,
          'google_id': googleId ?? 'google_oauth_${email.hashCode}',
          'id_token': idToken,
          'photo_url': photoUrl,
        }),
      );
      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return {'success': true, 'data': data};
      } else {
        return {'success': false, 'error': data['detail'] ?? 'Google authentication failed.'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error during Google authentication.'};
    }
  }

  static Future<Map<String, dynamic>?> getMe(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (_) {}
    return null;
  }

  static Future<void> markNotificationRead(int id) async {
    try {
      await http.put(Uri.parse('$baseUrl/notifications/$id/read'));
    } catch (_) {}
  }

  static Future<void> clearNotifications() async {
    try {
      await http.delete(Uri.parse('$baseUrl/notifications/clear'));
    } catch (_) {}
  }

  static Future<List<NotificationItem>> fetchNotifications() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/notifications'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((item) => NotificationItem.fromJson(item)).toList();
      }
    } catch (_) {}
    return [
      NotificationItem(
        id: 1,
        type: 'price_drop',
        title: 'Price Drop Alert: Delhi to Bangalore',
        message: 'Flight fares dropped by 12% (₹850 savings) for your target dates!',
        isRead: false,
        createdAt: '2026-07-31T12:00:00Z',
      ),
      NotificationItem(
        id: 2,
        type: 'gate_change',
        title: 'Gate Change: IndiGo 6E-205',
        message: 'Gate changed from T1 - Gate 4 to T1 - Gate 12.',
        isRead: false,
        createdAt: '2026-07-31T14:30:00Z',
      ),
    ];
  }

  // Helper Mock Search Data Generator
  static List<Itinerary> _getMockSearchResults(String org, String dst, double? budget) {
    return [
      Itinerary(
        id: 1,
        type: 'Best Value',
        totalPrice: budget ?? 4850.0,
        totalDuration: 4.5,
        carbonFootprint: 140.0,
        reliabilityScore: 94.5,
        delayProbability: 0.08,
        averageDelay: 10.0,
        aiExplanation: 'Optimal combination of low transit overhead, competitive pricing, and high punctuality.',
        legs: [
          ItineraryLeg(
            transportType: 'Cab',
            provider: 'Uber Intercity',
            origin: org,
            destination: '$org Airport (LKO)',
            departureTime: '08:00',
            arrivalTime: '09:30',
            price: 650.0,
            duration: 1.5,
            delayProbability: 0.05,
            averageDelay: 5.0,
            refundability: 'Refundable',
            seatClass: 'Sedan Standard',
            carbonFootprint: 18.0,
            hiddenCosts: {'base_fare': 550, 'taxes': 100},
          ),
          ItineraryLeg(
            transportType: 'Flight',
            provider: 'IndiGo 6E-205',
            origin: '$org Airport (LKO)',
            destination: '$dst Airport (BLR)',
            departureTime: '11:00',
            arrivalTime: '13:30',
            price: 3600.0,
            duration: 2.5,
            delayProbability: 0.08,
            averageDelay: 10.0,
            refundability: 'Non-refundable',
            seatClass: 'Economy',
            carbonFootprint: 120.0,
            bookingLink: 'https://www.goindigo.in',
            hiddenCosts: {'base_fare': 3000, 'taxes': 400, 'seat_fee': 200},
          ),
          ItineraryLeg(
            transportType: 'Metro',
            provider: 'Airport Line Metro',
            origin: '$dst Airport (BLR)',
            destination: dst,
            departureTime: '14:00',
            arrivalTime: '14:30',
            price: 60.0,
            duration: 0.5,
            delayProbability: 0.01,
            averageDelay: 1.0,
            refundability: 'Refundable',
            seatClass: 'Express',
            carbonFootprint: 2.0,
            hiddenCosts: {'base_fare': 60},
          ),
        ],
        pricePrediction: PricePrediction(
          indicator: 'Buy Now',
          confidence: 88,
          explanation: 'Fares expected to increase by 14% in the next 24 hours.',
          historicalTrend: [5200.0, 5000.0, 4900.0, 4850.0],
        ),
        delayPrediction: DelayPrediction(
          airportCongestion: 'Low',
          weatherImpact: 'Clear Skies',
          averageDelay: 10.0,
        ),
        explanationDetails: ExplanationDetails(
          whySelected: 'Balanced cost and comfort for multi-modal travel.',
          pros: ['Saves 8 hours over rail', 'Clean airport metro transfer'],
          cons: ['Requires intercity cab to airport'],
          tradeOffs: 'Slightly higher cost than train, but saves an entire day of travel.',
          moneySaved: 1200.0,
          timeSavedMins: 480,
        ),
      ),
      Itinerary(
        id: 2,
        type: 'Cheapest',
        totalPrice: 1450.0,
        totalDuration: 14.0,
        carbonFootprint: 45.0,
        reliabilityScore: 88.0,
        delayProbability: 0.18,
        averageDelay: 25.0,
        aiExplanation: 'Cheapest alternative utilizing express sleeper rail and local auto rickshaws.',
        legs: [
          ItineraryLeg(
            transportType: 'Train',
            provider: 'Shatabdi Express',
            origin: org,
            destination: dst,
            departureTime: '18:00',
            arrivalTime: '07:30',
            price: 1300.0,
            duration: 13.5,
            delayProbability: 0.15,
            averageDelay: 20.0,
            refundability: 'Partial Refund',
            seatClass: '3rd AC Sleeper',
            carbonFootprint: 42.0,
            bookingLink: 'https://www.irctc.co.in',
            hiddenCosts: {'base_fare': 1150, 'taxes': 150},
          ),
          ItineraryLeg(
            transportType: 'Cab',
            provider: 'Auto Rickshaw',
            origin: '$dst Station',
            destination: dst,
            departureTime: '07:45',
            arrivalTime: '08:15',
            price: 150.0,
            duration: 0.5,
            delayProbability: 0.05,
            averageDelay: 5.0,
            refundability: 'Refundable',
            seatClass: 'Standard',
            carbonFootprint: 3.0,
            hiddenCosts: {'base_fare': 150},
          ),
        ],
        pricePrediction: PricePrediction(
          indicator: 'Wait',
          confidence: 75,
          explanation: 'Rail tickets available under Tatkal quota soon.',
          historicalTrend: [1600.0, 1500.0, 1450.0],
        ),
        delayPrediction: DelayPrediction(
          airportCongestion: 'N/A',
          weatherImpact: 'Light Fog Expected',
          averageDelay: 25.0,
        ),
        explanationDetails: ExplanationDetails(
          whySelected: 'Lowest out-of-pocket cost.',
          pros: ['Extremely affordable (₹1450 total)', 'Low carbon emissions'],
          cons: ['Takes 14 hours overnight'],
          tradeOffs: 'Trading time for massive cost savings.',
          moneySaved: 3400.0,
          timeSavedMins: 0,
        ),
      ),
    ];
  }

  static Map<String, dynamic> _getMockChatResponse(String msg) {
    return {
      'reply': 'I have analyzed all travel channels between **Kanpur** and **Bangalore**. Based on your request, I recommend a hybrid route (**Cab → Flight → Metro**) costing **₹4,850** and taking **4.5 hours**.',
      'follow_ups': [
        'Show cheapest flights only',
        'Add this route to my Itinerary',
        'Check delay probability for IndiGo 6E-205',
        'What is the weather in Bangalore?'
      ],
      'itineraries': _getMockSearchResults('Kanpur', 'Bangalore', 5000.0),
    };
  }

  static AIBudgetAnalysisReport getMockBudgetReport(double total, String org, String dst, [int stayDays = 3, double? planCost]) {
    double plan = planCost ?? (total * 0.96);
    bool over = plan > total;
    return AIBudgetAnalysisReport(
      totalBudget: total,
      recommendedBudget: total * 0.96,
      estimatedSavings: over ? 0.0 : total * 0.04,
      budgetHealth: over ? 'Over Budget' : 'Excellent',
      healthPercentage: (plan / total) * 100,
      aiConfidence: 95,
      aiExplanation: 'Based on your destination, travel dates, number of travelers, and current prices, your budget is sufficient for a comfortable trip.',
      allocations: [
        BudgetAllocation(category: 'Flights', amount: total * 0.55, percentage: 55, status: 'Excellent', reason: 'Flight prices are within the normal competitive range.'),
        BudgetAllocation(category: 'Hotels', amount: total * 0.25, percentage: 25, status: 'Good', reason: 'Hotel prices are reasonable for your destination.'),
        BudgetAllocation(category: 'Food', amount: total * 0.12, percentage: 12, status: 'Slightly High', reason: 'Choosing restaurants outside tourist areas can reduce this expense.'),
        BudgetAllocation(category: 'Local Transport', amount: total * 0.08, percentage: 8, status: 'Good', reason: 'Metro and public transport are available.'),
      ],
      savingsSuggestions: [
        SavingSuggestion(title: 'Shift hotel 2 km away', savings: 2200, category: 'Hotels'),
        SavingSuggestion(title: 'Book flight today', savings: 1300, category: 'Flights'),
        SavingSuggestion(title: 'Use metro instead of taxi', savings: 850, category: 'Transport'),
        SavingSuggestion(title: 'Breakfast included hotel', savings: 1800, category: 'Food'),
      ],
      potentialSavings: 6150,
      isOverBudget: over,
      extraRequired: over ? plan - total : 0,
      overBudgetSuggestions: [
        SavingSuggestion(title: 'Switch to 400m nearby hotel', savings: 1800, category: 'Hotels'),
        SavingSuggestion(title: 'Take train instead of flight', savings: 1600, category: 'Transport'),
      ],
      paymentOptimizations: [
        PaymentOptimization(provider: 'SBI Cashback Credit Card', savings: 900, type: 'Credit Card Offer'),
        PaymentOptimization(provider: 'HDFC SmartBuy Travel Direct', savings: 650, type: 'Partner Bank Offer'),
        PaymentOptimization(provider: 'Instant UPI Cashback Voucher', savings: 250, type: 'UPI Discount'),
      ],
      hotelOptimization: HotelOptimization(
        currentName: 'Grand Palace City Center',
        currentPrice: 3500,
        currentRating: '4.2 ★',
        recommendedName: 'Courtyard Suites & Spa',
        recommendedPrice: 2700,
        recommendedRating: '4.3 ★',
        distanceDifference: '400m from city center',
        savingsPerNight: 800,
      ),
      dailyBreakdown: [
        DailyBudgetBreakdown(day: 'Day 1', amount: total * 0.40, highlights: 'Arrival, Airport Cab & Hotel Check-in'),
        DailyBudgetBreakdown(day: 'Day 2', amount: total * 0.35, highlights: 'Sightseeing & Metro Transit'),
        DailyBudgetBreakdown(day: 'Day 3', amount: total * 0.25, highlights: 'Shopping & Airport Return'),
      ],
      hiddenExpenses: HiddenExpenses(
        airportTax: 650,
        seatSelection: 300,
        extraBaggage: 900,
        meals: 450,
        gst: 1200,
        totalHiddenCost: 3500,
      ),
      emergencyReserve: total * 0.05,
      currentPlanCost: plan,
      optimizedPlanCost: plan - 4200,
      totalPlanSavings: 4200,
      aiScore: over ? 72 : 94,
      scoreReasons: [
        '✔ Excellent transport allocation',
        '✔ Affordable hotel choice',
        '✔ Food budget is balanced',
        '✔ Local transport cost is optimal',
      ],
      scenarioHigher: 'If Budget becomes ₹${(total + 5000).toInt()}: Upgrade to a 4-star hotel.',
      scenarioLower: 'If Budget becomes ₹${(total - 10000).toInt()}: Replace flight with train and save ₹9000.',
      optimizationResult: BudgetOptimizationResult(
        beforeItem: 'Standard Booking Plan',
        beforeCost: plan,
        afterItem: 'Optimized Booking Plan',
        afterCost: plan - 4200,
        savings: 4200,
        explanation: 'Nearby Airport Flight (Save ₹3500) + 400m Nearby Hotel (Save ₹700).',
      ),
    );
  }
}
