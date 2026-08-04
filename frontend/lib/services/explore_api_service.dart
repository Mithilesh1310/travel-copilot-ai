import 'dart:convert';
import 'dart:developer' as developer;
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import '../models/explore_models.dart';

class ExploreApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/explore';

  static Future<Map<String, dynamic>> fetchApiStatus() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/status'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      developer.log('Error checking explore API status: $e');
    }
    return {
      'has_credentials': false,
      'message': 'Waiting for API Credentials.'
    };
  }

  static Future<List<ExploreMission>> fetchMissions() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/missions'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => ExploreMission.fromJson(json)).toList();
      }
    } catch (e) {
      developer.log('Error fetching explore missions: $e');
    }
    return [];
  }

  static Future<List<EmergencyLocation>> fetchEmergencyFacilities({
    required double lat,
    required double lng,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/emergency?lat=$lat&lng=$lng'),
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => EmergencyLocation.fromJson(json)).toList();
      }
    } catch (e) {
      developer.log('Error fetching emergency facilities: $e');
    }
    return [];
  }

  static Future<ExploreItinerary> planSightseeing({
    required String location,
    double? lat,
    double? lng,
    double availableHours = 6.0,
    double budget = 2000.0,
    List<String> interests = const [],
    Map<String, dynamic>? preferences,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/plan'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'location': location,
          'lat': lat,
          'lng': lng,
          'available_hours': availableHours,
          'budget': budget,
          'interests': interests,
          'preferences': preferences ?? {},
        }),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return ExploreItinerary.fromJson(data);
      }
    } catch (e) {
      developer.log('Error planning sightseeing itinerary: $e');
    }

    final coords = resolveCityCoordinates(location);
    final fallbackStops = generateFallbackStops(location, coords);

    return ExploreItinerary(
      location: location,
      lat: coords.latitude,
      lng: coords.longitude,
      totalStops: fallbackStops.length,
      totalHours: availableHours,
      totalCost: 0.0,
      remainingBudget: budget,
      stops: fallbackStops,
      timeBlockedSchedule: [],
      multiTransportMix: ['Walking', 'Metro', 'Cab'],
      hiddenGems: [],
      photoSpots: [],
      foodRecommendations: [],
      shoppingRecommendations: [],
      waitingForApiCredentials: false,
      apiCredentialsMessage: null,
    );
  }

  static LatLng resolveCityCoordinates(String location) {
    final loc = location.toLowerCase();
    if (loc.contains('mumbai') || loc.contains('bombay')) {
      return const LatLng(19.0760, 72.8777);
    } else if (loc.contains('kanpur')) {
      return const LatLng(26.4499, 80.3319);
    } else if (loc.contains('london')) {
      return const LatLng(51.5074, -0.1278);
    } else if (loc.contains('paris')) {
      return const LatLng(48.8566, 2.3522);
    } else if (loc.contains('new york')) {
      return const LatLng(40.7128, -74.0060);
    } else if (loc.contains('bangalore') || loc.contains('bengaluru')) {
      return const LatLng(12.9716, 77.5946);
    } else if (loc.contains('delhi')) {
      return const LatLng(28.6139, 77.2090);
    }
    return const LatLng(28.6139, 77.2090);
  }

  static Future<LatLng> resolveCityCoordinatesAsync(String location) async {
    final syncRes = resolveCityCoordinates(location);
    if (!location.toLowerCase().contains('delhi') && syncRes.latitude != 28.6139) {
      return syncRes;
    }

    try {
      final cleanQuery = Uri.encodeComponent(location.replaceAll(RegExp(r'\(.*\)'), '').trim());
      final response = await http.get(
        Uri.parse('https://nominatim.openstreetmap.org/search?q=$cleanQuery&format=json&limit=1'),
        headers: {'User-Agent': 'TravelCopilotAI/2.0'},
      );
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        if (data.isNotEmpty) {
          final double lat = double.parse(data[0]['lat'].toString());
          final double lng = double.parse(data[0]['lon'].toString());
          return LatLng(lat, lng);
        }
      }
    } catch (e) {
      developer.log('Nominatim web geocoding error: $e');
    }
    return const LatLng(28.6139, 77.2090);
  }

  static List<AttractionStop> generateFallbackStops(String location, LatLng coords) {
    final loc = location.toLowerCase();
    if (loc.contains('mumbai') || loc.contains('bombay')) {
      return [
        AttractionStop(
          id: 'mum_1',
          name: 'Gateway of India & Apollo Bunder',
          category: 'Historical Monument',
          lat: 18.9220,
          lng: 72.8347,
          address: 'Apollo Bandar, Colaba, Mumbai',
          visitDurationMins: 60,
          estimatedCost: 0.0,
          travelTimeFromPrevMins: 0,
          travelModeFromPrev: 'Walking',
          scheduledTime: '09:00 AM',
          aiReasoning: 'Iconic 26-meter basalt archway best visited early morning.',
          aiScore: 99,
          imageUrl: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f',
          description: '26-meter basalt arch overlooking the Arabian Sea.',
          historySummary: 'Erected in 1924, this landmark marked the ceremonial entrance to India.',
          facts: ['Indo-Saracenic Architecture', 'Overlooks Arabian Sea'],
          architecture: 'Indo-Saracenic revival',
          culturalImportance: 'Symbolic gateway to India',
          entryFee: 'Free Entry',
          openingHours: '24 Hours Open',
          bestVisitingTime: 'Early Morning',
          photoTips: 'Shoot facing the sea during morning sunlight.',
          safetyTips: 'Keep belongings secure.',
          accessibility: 'Wheelchair accessible.',
          nearbyAmenities: {'toilets': true, 'cafes': true},
          spendingEstimate: {'entry': 0.0},
        ),
        AttractionStop(
          id: 'mum_2',
          name: "Marine Drive & Queen's Necklace",
          category: 'Scenic Waterfront',
          lat: 18.9438,
          lng: 72.8234,
          address: 'Netaji Subhash Chandra Bose Road, Mumbai',
          visitDurationMins: 75,
          estimatedCost: 0.0,
          travelTimeFromPrevMins: 12,
          travelModeFromPrev: 'Cab',
          scheduledTime: '10:30 AM',
          aiReasoning: 'C-shaped boulevard offering sweeping sea views and Art Deco architecture.',
          aiScore: 97,
          imageUrl: 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66',
          description: "World-famous coastal promenade known as the Queen's Necklace.",
          historySummary: 'Reclaimed from the sea in 1920s.',
          facts: ['UNESCO World Heritage Art Deco Precinct'],
          architecture: 'Art Deco oceanfront',
          culturalImportance: 'Mumbai leisure sea front',
          entryFee: 'Free Promenade Access',
          openingHours: '24 Hours Open',
          bestVisitingTime: 'Morning or Sunset',
          photoTips: 'Capture the wide curved bay.',
          safetyTips: 'Use pedestrian zebra crossings.',
          accessibility: 'Wide level sidewalk.',
          nearbyAmenities: {'toilets': true, 'cafes': true},
          spendingEstimate: {'entry': 0.0},
        ),
      ];
    }
    return [
      AttractionStop(
        id: 'gen_1',
        name: 'Historic Central Plaza, $location',
        category: 'Historical Landmark',
        lat: coords.latitude + 0.005,
        lng: coords.longitude + 0.003,
        address: 'Central Sector, $location',
        visitDurationMins: 90,
        estimatedCost: 0.0,
        travelTimeFromPrevMins: 0,
        travelModeFromPrev: 'Walking',
        scheduledTime: '09:30 AM',
        aiReasoning: 'Optimal early morning timing with lowest crowd density.',
        aiScore: 98,
        imageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada',
        description: 'An iconic heritage landmark situated in the heart of $location.',
        historySummary: 'Constructed as a central civic hub.',
        facts: ['Top Rated Destination'],
        architecture: 'Classic Imperial Architecture',
        culturalImportance: 'Symbol of civic pride.',
        entryFee: 'Free Entry',
        openingHours: '09:00 AM - 06:00 PM',
        bestVisitingTime: 'Morning',
        photoTips: 'Shoot during morning light.',
        safetyTips: 'Keep valuables secure.',
        accessibility: 'Wheelchair Accessible.',
        nearbyAmenities: {'toilets': true, 'cafes': true},
        spendingEstimate: {'entry': 0.0},
      ),
    ];
  }

  static Future<Map<String, dynamic>> fetchAudioGuide({
    required String attractionId,
    required String name,
  }) async {
    try {
      final encodedName = Uri.encodeComponent(name);
      final response = await http.get(
        Uri.parse('$baseUrl/audio-guide/$attractionId?name=$encodedName'),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      developer.log('Error fetching audio guide: $e');
    }
    return {
      'has_audio_credentials': false,
      'script': 'Welcome to $name. Waiting for ElevenLabs API Credentials for voice playback.',
      'message': 'Waiting for API Credentials.'
    };
  }
}
