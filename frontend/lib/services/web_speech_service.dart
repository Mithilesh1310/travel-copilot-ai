// Conditional export for Web vs non-Web speech synthesis
export 'web_speech_stub.dart'
    if (dart.library.html) 'web_speech_web.dart';
