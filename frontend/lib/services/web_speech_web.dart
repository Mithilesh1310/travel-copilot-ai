// Web implementation using dart:html
import 'dart:html' as html;

void speakWebText(String text) {
  try {
    html.window.speechSynthesis?.cancel();
    final utterance = html.SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.lang = 'en-US';
    html.window.speechSynthesis?.speak(utterance);
  } catch (_) {}
}

void stopWebSpeech() {
  try {
    html.window.speechSynthesis?.cancel();
  } catch (_) {}
}
