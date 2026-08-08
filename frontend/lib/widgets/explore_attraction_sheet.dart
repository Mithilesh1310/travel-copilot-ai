import 'package:flutter/material.dart';
import '../models/explore_models.dart';
import '../services/explore_api_service.dart';
import '../services/web_speech_service.dart';

class ExploreAttractionSheet extends StatefulWidget {
  final AttractionStop stop;
  final bool isDarkMode;
  final VoidCallback? onSkipStop;
  final Function(AttractionStop)? onStartNavigation;

  const ExploreAttractionSheet({
    super.key,
    required this.stop,
    required this.isDarkMode,
    this.onSkipStop,
    this.onStartNavigation,
  });

  @override
  State<ExploreAttractionSheet> createState() => _ExploreAttractionSheetState();
}

class _ExploreAttractionSheetState extends State<ExploreAttractionSheet> {
  bool _isPlayingVoiceGuide = false;
  Map<String, dynamic>? _voiceGuideData;

  @override
  void initState() {
    super.initState();
    _loadVoiceGuide();
  }

  void _loadVoiceGuide() async {
    final data = await ExploreApiService.fetchAudioGuide(
      attractionId: widget.stop.id,
      name: widget.stop.name,
    );
    if (mounted) {
      setState(() {
        _voiceGuideData = data;
      });
    }
  }

  void _toggleSpeech() {
    final script = _voiceGuideData?['script'] ?? widget.stop.description;
    final newState = !_isPlayingVoiceGuide;
    setState(() {
      _isPlayingVoiceGuide = newState;
    });

    if (!newState) {
      stopWebSpeech();
      return;
    }

    speakWebText(script);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;
    final bg = isDark ? const Color(0xFF111827) : Colors.white;
    final textColor = isDark ? Colors.white : const Color(0xFF0F172A);
    final subtextColor = isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B);
    final cardBg = isDark ? const Color(0xFF1F2937) : const Color(0xFFF8FAFC);
    final border = isDark ? const Color(0xFF374151) : const Color(0xFFE2E8F0);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        border: Border(top: BorderSide(color: border)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle bar
            Center(
              child: Container(
                width: 48,
                height: 5,
                decoration: BoxDecoration(
                  color: isDark ? const Color(0xFF374151) : const Color(0xFFCBD5E1),
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Header Title & AI Score Badge
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.stop.name,
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: textColor),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${widget.stop.category} • ${widget.stop.address}',
                        style: TextStyle(color: subtextColor, fontSize: 13),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF10B981).withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.star, color: Color(0xFF10B981), size: 16),
                      const SizedBox(width: 4),
                      Text(
                        '${widget.stop.aiScore}% Match',
                        style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // AI Reasoning Rationale
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF6366F1).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.25)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Color(0xFF6366F1), size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Why AI Selected This Attraction:',
                          style: TextStyle(color: Color(0xFF6366F1), fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          widget.stop.aiReasoning,
                          style: TextStyle(color: textColor, fontSize: 13, height: 1.4),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // AI Voice Tour Guide Player
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: cardBg,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.headphones, color: Color(0xFF8B5CF6), size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'AI Voice Tour Guide',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: textColor),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: Icon(
                          _isPlayingVoiceGuide ? Icons.pause_circle_filled : Icons.play_circle_fill,
                          color: const Color(0xFF6366F1),
                          size: 32,
                        ),
                        onPressed: _toggleSpeech,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _voiceGuideData?['script'] ?? 'Loading tour guide narration...',
                    style: TextStyle(color: subtextColor, fontSize: 12, height: 1.4, fontStyle: FontStyle.italic),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: (_voiceGuideData?['has_audio_credentials'] == true)
                          ? const Color(0xFF10B981).withValues(alpha: 0.15)
                          : Colors.purple.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      (_voiceGuideData?['has_audio_credentials'] == true)
                          ? '✨ ElevenLabs AI Voice Active'
                          : '🔊 Web AI Speech Engine Active',
                      style: TextStyle(
                        color: (_voiceGuideData?['has_audio_credentials'] == true)
                            ? const Color(0xFF10B981)
                            : Colors.purpleAccent,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Key Quick Details Grid
            Row(
              children: [
                Expanded(
                  child: _buildDetailStatBox('Entry Fee', widget.stop.entryFee, Icons.confirmation_number_outlined, isDark),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildDetailStatBox('Opening Hours', widget.stop.openingHours, Icons.access_time, isDark),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildDetailStatBox('Visit Time', '${widget.stop.visitDurationMins} Mins', Icons.timer_outlined, isDark),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Description & History
            Text('Historical Significance & Culture', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: textColor)),
            const SizedBox(height: 6),
            Text(
              widget.stop.description.isNotEmpty
                  ? widget.stop.description
                  : 'An iconic landmark renowned for historical heritage, cultural storytelling, and architectural splendor.',
              style: TextStyle(color: subtextColor, fontSize: 13, height: 1.5),
            ),
            const SizedBox(height: 20),

            // Photography Tips & Best Timing
            Text('📸 Photography & Golden Hour Advice', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: textColor)),
            const SizedBox(height: 6),
            Text(
              widget.stop.photoTips.isNotEmpty ? widget.stop.photoTips : 'Best lighting during golden hour (sunrise/sunset). Position yourself at the main courtyard.',
              style: TextStyle(color: subtextColor, fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 24),

            // Action Buttons
            Row(
              children: [
                if (widget.onSkipStop != null)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: widget.onSkipStop,
                      icon: const Icon(Icons.skip_next, size: 18),
                      label: const Text('Skip Attraction'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      ),
                    ),
                  ),
                if (widget.onSkipStop != null) const SizedBox(width: 14),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      widget.onStartNavigation?.call(widget.stop);
                    },
                    icon: const Icon(Icons.navigation, size: 18),
                    label: const Text('Start Live Navigation'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF6366F1),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailStatBox(String label, String value, IconData icon, bool isDark) {
    final bg = isDark ? const Color(0xFF1F2937) : const Color(0xFFF8FAFC);
    final border = isDark ? const Color(0xFF374151) : const Color(0xFFE2E8F0);
    final textColor = isDark ? Colors.white : const Color(0xFF0F172A);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 14, color: const Color(0xFF6366F1)),
              const SizedBox(width: 4),
              Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: textColor),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
