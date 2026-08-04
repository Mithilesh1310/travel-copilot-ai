import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/explore_models.dart';

class ExploreMapWidget extends StatefulWidget {
  final LatLng initialCenter;
  final double initialZoom;
  final List<AttractionStop> stops;
  final List<EmergencyLocation> emergencyFacilities;
  final bool showEmergencyOverlay;
  final Function(AttractionStop)? onStopTap;
  final Function(EmergencyLocation)? onEmergencyTap;

  const ExploreMapWidget({
    super.key,
    required this.initialCenter,
    this.initialZoom = 13.0,
    required this.stops,
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
    if (widget.initialCenter != oldWidget.initialCenter || widget.stops != oldWidget.stops) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _centerOnRoute();
        }
      });
    }
  }

  void _centerOnRoute() {
    if (widget.stops.isNotEmpty) {
      final bounds = LatLngBounds.fromPoints(
        widget.stops.map((s) => LatLng(s.lat, s.lng)).toList(),
      );
      _mapController.fitCamera(
        CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(50)),
      );
    } else {
      _mapController.move(widget.initialCenter, widget.initialZoom);
    }
  }

  @override
  Widget build(BuildContext context) {
    final routePoints = widget.stops.map((s) => LatLng(s.lat, s.lng)).toList();

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
            if (routePoints.length >= 2)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: routePoints,
                    strokeWidth: 4.5,
                    color: const Color(0xFF6366F1),
                  ),
                ],
              ),
            MarkerLayer(
              markers: [
                // Live User Location Marker
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

                // Sightseeing Numbered Stop Markers
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

        // Map Control Floating Pill Buttons
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
