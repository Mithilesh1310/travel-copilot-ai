import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/main.dart';
import 'package:frontend/models/travel_models.dart';
import 'package:frontend/services/api_service.dart';

void main() {
  testWidgets('AI Travel Copilot App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const AiTravelCopilotApp());

    // Verify that title text is present
    expect(find.text('AI Travel Copilot'), findsOneWidget);
  });

  test('Itinerary model JSON deserialization test', () {
    final jsonMap = {
      'id': 101,
      'type': 'Best Value',
      'total_price': 4850.0,
      'total_duration': 4.5,
      'carbon_footprint': 140.0,
      'reliability_score': 94.5,
      'delay_probability': 0.08,
      'average_delay': 10.0,
      'ai_explanation': 'Optimal hybrid route',
      'legs': [
        {
          'transport_type': 'Cab',
          'provider': 'Uber',
          'origin': 'Kanpur',
          'destination': 'Lucknow Airport',
          'departure_time': '08:00',
          'arrival_time': '09:30',
          'price': 650.0,
          'duration': 1.5,
          'delay_probability': 0.05,
          'average_delay': 5.0,
          'refundability': 'Refundable',
          'seat_class': 'Standard',
          'carbon_footprint': 18.0,
          'hidden_costs': '{"base_fare": 550, "taxes": 100}'
        }
      ]
    };

    final itinerary = Itinerary.fromJson(jsonMap);

    expect(itinerary.id, 101);
    expect(itinerary.type, 'Best Value');
    expect(itinerary.totalPrice, 4850.0);
    expect(itinerary.legs.length, 1);
    expect(itinerary.legs.first.provider, 'Uber');
  });

  test('ApiService mock fallback search test', () async {
    final results = await ApiService.searchTrips(
      origin: 'Kanpur',
      destination: 'Bangalore',
      startDate: '2026-10-15',
      budget: 5000,
    );

    expect(results.isNotEmpty, true);
    expect(results.first.legs.length, greaterThan(0));
  });
}

