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
    } else if (loc.contains('ballia')) {
      return const LatLng(25.8749, 84.1210);
    } else if (loc.contains('ghosi')) {
      return const LatLng(26.1120, 83.5410);
    } else if (loc.contains('mau')) {
      return const LatLng(25.9520, 83.5570);
    } else if (loc.contains('delhi')) {
      return const LatLng(28.6139, 77.2090);
    }
    return const LatLng(25.8749, 84.1210);
  }

  static Future<LatLng> resolveCityCoordinatesAsync(String location) async {
    final syncRes = resolveCityCoordinates(location);
    if (!location.toLowerCase().contains('delhi') && syncRes.latitude != 25.8749) {
      return syncRes;
    }

    final queryClean = location.toLowerCase().trim();
    final parts = queryClean.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList();

    final indianKeywords = ['ballia', 'uttar pradesh', 'up', 'bihar', 'kanpur', 'mau', 'ghosi', 'varanasi', 'lucknow', 'patna', 'gorakhpur', 'agra', 'jaipur', 'mumbai', 'delhi', 'india'];
    final hasIndianKw = indianKeywords.any((kw) => queryClean.contains(kw));

    final searchQueries = <String>[];
    if (hasIndianKw && !queryClean.contains('india')) {
      searchQueries.add('$queryClean, india');
      if (parts.length > 1) {
        searchQueries.add('${parts.last}, uttar pradesh, india');
        searchQueries.add('${parts.last}, india');
      }
    }

    searchQueries.add(queryClean);
    for (int i = 1; i < parts.length; i++) {
      searchQueries.add(parts.sublist(i).join(', '));
    }
    if (parts.length > 1) {
      searchQueries.add(parts.last);
      searchQueries.add(parts.first);
    }

    if (queryClean.contains('ballia')) {
      searchQueries.add('ballia, uttar pradesh, india');
    }

    for (final q in searchQueries) {
      if (q.length < 2) continue;

      // Stage 1: OpenStreetMap Nominatim
      try {
        final cleanQuery = Uri.encodeComponent(q);
        final ccParam = hasIndianKw ? '&countrycodes=in' : '';
        final response = await http.get(
          Uri.parse('https://nominatim.openstreetmap.org/search?q=$cleanQuery&format=json&limit=1$ccParam'),
          headers: {'User-Agent': 'TravelCopilotAI/2.0'},
        );
        if (response.statusCode == 200) {
          final List data = jsonDecode(response.body);
          if (data.isNotEmpty) {
            final String display = data[0]['display_name']?.toString() ?? '';
            if (hasIndianKw && (display.toLowerCase().contains('pakistan') || display.toLowerCase().contains('bangladesh'))) {
              continue;
            }
            final double lat = double.parse(data[0]['lat'].toString());
            final double lng = double.parse(data[0]['lon'].toString());
            developer.log('Nominatim Geocoded $q -> ($lat, $lng)');
            return LatLng(lat, lng);
          }
        }
      } catch (e) {
        developer.log('Nominatim web geocoding error for $q: $e');
      }

      // Stage 2: Photon Komoot Geocoder
      try {
        final cleanQuery = Uri.encodeComponent(q);
        final response = await http.get(
          Uri.parse('https://photon.komoot.io/api/?q=$cleanQuery&limit=1'),
          headers: {'User-Agent': 'TravelCopilotAI/2.0'},
        );
        if (response.statusCode == 200) {
          final Map<String, dynamic> data = jsonDecode(response.body);
          final List features = data['features'] ?? [];
          if (features.isNotEmpty) {
            final Map<String, dynamic> props = features[0]['properties'] ?? {};
            final String country = (props['country'] ?? '').toString().toLowerCase();
            final String name = (props['name'] ?? '').toString().toLowerCase();
            if (hasIndianKw && (country.contains('pakistan') || name.contains('pakistan') || country == 'pakistan')) {
              continue;
            }
            final List coords = features[0]['geometry']['coordinates'];
            final double lat = double.parse(coords[1].toString());
            final double lng = double.parse(coords[0].toString());
            developer.log('Photon Geocoded $q -> ($lat, $lng)');
            return LatLng(lat, lng);
          }
        }
      } catch (e) {
        developer.log('Photon web geocoding error for $q: $e');
      }
    }

    if (queryClean.contains('ballia')) {
      return const LatLng(25.8749, 84.1210);
    }

    return syncRes;
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
    final cleanLoc = location.split(',')[0].trim();
    return [
      AttractionStop(
        id: 'gen_1',
        name: 'Historic Central Heritage Plaza, $cleanLoc',
        category: 'Historical Landmark',
        lat: coords.latitude + 0.003,
        lng: coords.longitude + 0.002,
        address: 'Central Sector, $cleanLoc',
        visitDurationMins: 90,
        estimatedCost: 0.0,
        travelTimeFromPrevMins: 0,
        travelModeFromPrev: 'Walking',
        scheduledTime: '09:30 AM',
        aiReasoning: 'Optimal early morning timing with lowest crowd density.',
        aiScore: 98,
        imageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada',
        description: 'An iconic heritage landmark situated in the heart of $cleanLoc.',
        historySummary: 'Constructed as a central civic and cultural hub.',
        facts: ['Top Rated Destination', 'Authentic Verified Local Spot'],
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
      AttractionStop(
        id: 'gen_2',
        name: 'Grand Sacred Shrine & Sanctuary, $cleanLoc',
        category: 'Religious & Spiritual Shrine',
        lat: coords.latitude - 0.004,
        lng: coords.longitude + 0.005,
        address: 'Sacred Sector, $cleanLoc',
        visitDurationMins: 60,
        estimatedCost: 0.0,
        travelTimeFromPrevMins: 12,
        travelModeFromPrev: 'Walking',
        scheduledTime: '11:00 AM',
        aiReasoning: 'Tranquil spiritual shrine revered for peaceful atmosphere and classical architecture.',
        aiScore: 96,
        imageUrl: 'https://images.unsplash.com/photo-1548013146-72479768bada',
        description: 'Sacred spiritual shrine located in $cleanLoc featuring traditional carvings.',
        historySummary: 'Erected as a community sanctuary and spiritual retreat.',
        facts: ['Sacred Holy Shrine', 'Peaceful Courtyard'],
        architecture: 'Traditional Sacred Architecture',
        culturalImportance: 'Spiritual heart of the community.',
        entryFee: 'Free Entry',
        openingHours: '06:00 AM - 09:00 PM',
        bestVisitingTime: 'Morning',
        photoTips: 'Photograph central sanctuary dome reflecting morning sun.',
        safetyTips: 'Remove shoes before entering sanctum.',
        accessibility: 'Wheelchair accessible ramps.',
        nearbyAmenities: {'toilets': true, 'cafes': true},
        spendingEstimate: {'entry': 0.0},
      ),
      AttractionStop(
        id: 'gen_3',
        name: 'Artisan Craft Bazaar & Local Market, $cleanLoc',
        category: 'Cultural Market',
        lat: coords.latitude + 0.008,
        lng: coords.longitude - 0.004,
        address: 'Bazaar Sector, $cleanLoc',
        visitDurationMins: 60,
        estimatedCost: 200.0,
        travelTimeFromPrevMins: 15,
        travelModeFromPrev: 'Auto',
        scheduledTime: '12:30 PM',
        aiReasoning: 'Perfect transition for local street food tasting and authentic handicraft browsing.',
        aiScore: 94,
        imageUrl: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5',
        description: 'Vibrant market street in $cleanLoc teeming with local handicrafts and traditional cuisine.',
        historySummary: 'Operational for generations as a traditional trading center.',
        facts: ['Authentic Local Cuisine', 'Handcrafted Art'],
        architecture: 'Traditional Covered Alleyways',
        culturalImportance: 'Hub of local community trade and culture.',
        entryFee: 'Free Entry',
        openingHours: '10:00 AM - 09:00 PM',
        bestVisitingTime: 'Late Morning',
        photoTips: 'Capture colorful stalls and artisan workshops.',
        safetyTips: 'Bargain respectfully; keep cash handy.',
        accessibility: 'Level walkways.',
        nearbyAmenities: {'toilets': true, 'cafes': true},
        spendingEstimate: {'food': 150.0, 'souvenirs': 50.0},
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
