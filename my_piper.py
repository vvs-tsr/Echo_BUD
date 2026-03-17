# piper_tts.py
# Known-working style + standalone test block
# Use your confirmed-good Eminem voice model

from piper.voice import PiperVoice
import wave
import os
import time

VOICES_DIR = "voices"
DEFAULT_VOICE = "en_US-eminem-medium.onnx"

_piper_voice = None       # cached voice object
_loaded_model_path = None # which model is currently loaded


def get_piper_voice(model_name: str = DEFAULT_VOICE) -> PiperVoice | None:
    """
    Load (or reload) a Piper voice by filename.
    Re-loads automatically when a different voice is requested.
    """
    global _piper_voice, _loaded_model_path

    model_path = os.path.join(VOICES_DIR, model_name)

    if _piper_voice is not None and _loaded_model_path == model_path:
        return _piper_voice  # already loaded, same model

    if not os.path.exists(model_path):
        print(f"ERROR: Piper voice model not found at {model_path}")
        print("  → Download from https://github.com/rhasspy/piper/releases")
        print(f"  → Place .onnx + .onnx.json in folder: {VOICES_DIR}/")
        return None

    print(f"Loading Piper TTS voice: {model_path} ...")
    try:
        _piper_voice = PiperVoice.load(model_path)
        _loaded_model_path = model_path
        print("Piper TTS model loaded successfully.")
    except Exception as e:
        print(f"Error loading Piper TTS model: {e}")
        _piper_voice = None
        _loaded_model_path = None

    return _piper_voice


def generate_tts_wav(text: str, output_filepath: str, model_name: str = DEFAULT_VOICE) -> bool:
    """
    Convert text → WAV file using Piper.
    Pass model_name to use a specific voice (filename only, e.g. 'en_US-trump-high.onnx').
    Returns True if file was written successfully.
    """
    voice = get_piper_voice(model_name)
    if voice is None:
        print("TTS model not loaded → cannot generate audio.")
        return False

    print(f"Generating TTS → {output_filepath}")
    print(f"  Text (first 60 chars): {text[:60]}{'...' if len(text)>60 else ''}")

    try:
        with wave.open(output_filepath, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        print(f"Audio saved successfully: {output_filepath}")
        print(f"  Size: {os.path.getsize(output_filepath):,} bytes")
        return True
    except Exception as e:
        print(f"Failed to generate WAV: {e}")
        return False


# ────────────────────────────────────────────────
# Standalone test / demo when running this file directly
# ────────────────────────────────────────────────
if __name__ == "__main__":
    print("═" * 50)
    print(" Piper TTS standalone test")
    print("═" * 50)

    # Pre-load model (shows loading messages)
    if not get_piper_voice():
        print("Cannot continue — model failed to load.")
    else:
        # You can change these test sentences
        test_sentences = [
            "This is a test. Jarvis is speaking with the Eminem voice.",
            "Hey , milan how is life at IIT kanpur? and How ia food at hall 10?" ,
            "Vishnu is awesome ",
            "Beep boop. Testing one two three. This voice has attitude.",
        ]

        OUTPUT_DIR = "tts_test_output"
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for i, sentence in enumerate(test_sentences, 1):
            filename = os.path.join(
                OUTPUT_DIR,
                f"test_{i}_{int(time.time())}.wav"
            )
            success = generate_tts_wav(sentence, filename)
            if success:
                print(f"   → Created: {os.path.basename(filename)}")
            print("-" * 60)

        print("\nAll tests finished.")
        print(f"Listen to the files in: ./{OUTPUT_DIR}/")
        print("You can now safely import and use generate_tts_wav() in other scripts.")