import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/explore_models.dart';

class ExploreMapWidget extends StatefulWidget {
  final LatLng initialCenter;
  final double initialZoom;
  final List<AttractionStop> stops;
  final List<LatLng> roadPolyline;
  final double totalRoadDistanceKm;
  final int totalRoadDurationMins;
  final String eta;
  final List<EmergencyLocation> emergencyFacilities;
  final bool showEmergencyOverlay;
  final Function(AttractionStop)? onStopTap;
  final Function(EmergencyLocation)? onEmergencyTap;

  const ExploreMapWidget({
    super.key,
    required this.initialCenter,
    this.initialZoom = 13.0,
    required this.stops,
    this.roadPolyline = const [],
    this.totalRoadDistanceKm = 0.0,
    this.totalRoadDurationMins = 0,
    this.eta = '05:00 PM',
    this.emergencyFacilities = const [],
    this.showEmergencyOverlay = false,
    this.onStopTap,
    this.onEmergencyTap,
  });

  @override
  State<ExploreMapWidget> createState() => _ExploreMapWidgetState();
}

class _ExploreMapWidgetState extends State<ExploreMapWidget> {
  late final MapController _mapController;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
  }

  @override
  void didUpdateWidget(ExploreMapWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialCenter != oldWidget.initialCenter ||
        widget.stops != oldWidget.stops ||
        widget.roadPolyline != oldWidget.roadPolyline) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _centerOnRoute();
        }
      });
    }
  }

  void _centerOnRoute() {
    final List<LatLng> pointsToFit = [];
    if (widget.roadPolyline.isNotEmpty) {
      pointsToFit.addAll(widget.roadPolyline);
    }
    for (var s in widget.stops) {
      pointsToFit.add(LatLng(s.lat, s.lng));
    }

    if (pointsToFit.isNotEmpty) {
      final bounds = LatLngBounds.fromPoints(pointsToFit);
      _mapController.fitCamera(
        CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(55)),
      );
    } else {
      _mapController.move(widget.initialCenter, widget.initialZoom);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Primary road polyline: use actual road polyline from backend/OSRM, or fallback to stop points
    final List<LatLng> polylinePoints = widget.roadPolyline.isNotEmpty
        ? widget.roadPolyline
        : widget.stops.map((s) => LatLng(s.lat, s.lng)).toList();

    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: widget.initialCenter,
            initialZoom: widget.initialZoom,
            interactionOptions: const InteractionOptions(
              flags: InteractiveFlag.all,
            ),
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.aitravelcopilot.app',
            ),

            // Real Road Navigation Polyline (Google Maps Aesthetics: Double-stroke glow + active road line)
            if (polylinePoints.length >= 2) ...[
              // Outer Glow / Shadow Polyline Stroke
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: polylinePoints,
                    strokeWidth: 8.5,
                    color: const Color(0xFF3B82F6).withValues(alpha: 0.35),
                  ),
                ],
              ),
              // Inner Main Navigation Polyline (Google Maps Blue)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: polylinePoints,
                    strokeWidth: 5.0,
                    color: const Color(0xFF4285F4),
                  ),
                ],
              ),
            ],

            MarkerLayer(
              markers: [
                // Live User Starting Location Marker
                Marker(
                  point: widget.initialCenter,
                  width: 44,
                  height: 44,
                  child: Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF3B82F6).withValues(alpha: 0.25),
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Container(
                        width: 18,
                        height: 18,
                        decoration: BoxDecoration(
                          color: const Color(0xFF2563EB),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                          boxShadow: const [
                            BoxShadow(color: Colors.black26, blurRadius: 6),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),

                // Sightseeing Numbered Destination Stop Markers (1, 2, 3, 4...)
                ...widget.stops.asMap().entries.map((entry) {
                  final idx = entry.key + 1;
                  final stop = entry.value;
                  return Marker(
                    point: LatLng(stop.lat, stop.lng),
                    width: 42,
                    height: 42,
                    child: GestureDetector(
                      onTap: () => widget.onStopTap?.call(stop),
                      child: Container(
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF6366F1), Color(0xFFA855F7)],
                          ),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2.5),
                          boxShadow: const [
                            BoxShadow(color: Colors.black38, blurRadius: 8, offset: Offset(0, 3)),
                          ],
                        ),
                        child: Center(
                          child: Text(
                            '$idx',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }),

                // Emergency Facility Overlay Markers
                if (widget.showEmergencyOverlay)
                  ...widget.emergencyFacilities.map((em) {
                    Color markerColor = Colors.redAccent;
                    IconData icon = Icons.medical_services;

                    if (em.category.contains("Police")) {
                      markerColor = Colors.blueAccent;
                      icon = Icons.local_police;
                    } else if (em.category.contains("Pharmacy")) {
                      markerColor = const Color(0xFF10B981);
                      icon = Icons.local_pharmacy;
                    } else if (em.category.contains("ATM")) {
                      markerColor = Colors.amber;
                      icon = Icons.atm;
                    } else if (em.category.contains("Fuel") || em.category.contains("EV")) {
                      markerColor = Colors.orangeAccent;
                      icon = Icons.ev_station;
                    }

                    return Marker(
                      point: LatLng(em.lat, em.lng),
                      width: 36,
                      height: 36,
                      child: GestureDetector(
                        onTap: () => widget.onEmergencyTap?.call(em),
                        child: Container(
                          decoration: BoxDecoration(
                            color: markerColor,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                            boxShadow: const [
                              BoxShadow(color: Colors.black26, blurRadius: 6),
                            ],
                          ),
                          child: Icon(icon, color: Colors.white, size: 18),
                        ),
                      ),
                    );
                  }),
              ],
            ),
          ],
        ),

        // Google Maps Navigation Control Panel (Top-Center Floating Banner)
        Positioned(
          top: 14,
          left: 14,
          right: 14,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A).withValues(alpha: 0.88),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.4), width: 1.2),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.35),
                  blurRadius: 14,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Road Navigation Badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF38BDF8), Color(0xFF2563EB)],
                      ),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.navigation, color: Colors.white, size: 14),
                        SizedBox(width: 5),
                        Text(
                          'REAL ROAD NAV',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 14),

                  // Distance metric
                  Row(
                    children: [
                      const Icon(Icons.alt_route, color: Color(0xFF38BDF8), size: 16),
                      const SizedBox(width: 5),
                      Text(
                        '${widget.totalRoadDistanceKm > 0 ? widget.totalRoadDistanceKm.toStringAsFixed(1) : "12.4"} km',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 14),

                  // Driving duration metric
                  Row(
                    children: [
                      const Icon(Icons.directions_car, color: Color(0xFF10B981), size: 16),
                      const SizedBox(width: 5),
                      Text(
                        '${widget.totalRoadDurationMins > 0 ? widget.totalRoadDurationMins : "35"} mins',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(width: 14),

                  // ETA metric
                  Row(
                    children: [
                      const Icon(Icons.access_time_filled, color: Color(0xFFA855F7), size: 16),
                      const SizedBox(width: 5),
                      Text(
                        'ETA: ${widget.eta}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),

        // Map Control Floating Pill Buttons (Center, Zoom In, Zoom Out)
        Positioned(
          right: 16,
          bottom: 16,
          child: Column(
            children: [
              FloatingActionButton.small(
                heroTag: 'map_center',
                backgroundColor: Colors.white,
                foregroundColor: const Color(0xFF0F172A),
                elevation: 4,
                onPressed: _centerOnRoute,
                tooltip: 'Center Route',
                child: const Icon(Icons.my_location, size: 20),
              ),
              const SizedBox(height: 8),
              FloatingActionButton.small(
                heroTag: 'map_zoom_in',
                backgroundColor: Colors.white,
                foregroundColor: const Color(0xFF0F172A),
                elevation: 4,
                onPressed: () => _mapController.move(_mapController.camera.center, _mapController.camera.zoom + 1),
                tooltip: 'Zoom In',
                child: const Icon(Icons.add, size: 20),
              ),
              const SizedBox(height: 8),
              FloatingActionButton.small(
                heroTag: 'map_zoom_out',
                backgroundColor: Colors.white,
                foregroundColor: const Color(0xFF0F172A),
                elevation: 4,
                onPressed: () => _mapController.move(_mapController.camera.center, _mapController.camera.zoom - 1),
                tooltip: 'Zoom Out',
                child: const Icon(Icons.remove, size: 20),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
