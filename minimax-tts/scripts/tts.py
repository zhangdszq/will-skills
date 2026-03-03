#!/usr/bin/env python3
"""MiniMax TTS - Convert text to speech using MiniMax API."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def load_env():
    """Load .env from ~/.vk-cowork/.env (AI Team config), then fallback to cwd/.env and ~/.env."""
    env_paths = [
        os.path.expanduser("~/.vk-cowork/.env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.expanduser("~/.env"),
    ]
    env = {}
    for path in env_paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        k = key.strip()
                        if k not in env:  # first-wins: vk-cowork takes priority
                            env[k] = value.strip().strip('"').strip("'")
    return env


def tts(text, output_path, voice_id=None, speed=1.0, emotion=None, model="speech-02-hd"):
    env = load_env()

    api_key = os.environ.get("MINIMAX_TTS_API_KEY") or env.get("MINIMAX_TTS_API_KEY")
    group_id = os.environ.get("MINIMAX_TTS_GROUP_ID") or env.get("MINIMAX_TTS_GROUP_ID")
    default_voice = os.environ.get("MINIMAX_TTS_VOICE_ID") or env.get("MINIMAX_TTS_VOICE_ID", "Chinese (Mandarin)_Soft_Girl")

    if not api_key:
        print("Error: MINIMAX_TTS_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not group_id:
        print("Error: MINIMAX_TTS_GROUP_ID not set", file=sys.stderr)
        sys.exit(1)

    voice_id = voice_id or default_voice
    url = f"https://api.minimax.io/v1/t2a_v2?GroupId={group_id}"

    payload = {
        "model": model,
        "text": text,
        "voice_id": voice_id,
        "speed": speed,
        "format": "mp3",
        "audio_sample_rate": 32000,
        "bitrate": 128000,
    }
    if emotion:
        payload["emotion"] = emotion

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

    status = result.get("base_resp", {})
    if status.get("status_code", 0) != 0:
        print(f"API Error: {status.get('status_msg')}", file=sys.stderr)
        sys.exit(1)

    audio_hex = result.get("data", {}).get("audio", "")
    if not audio_hex:
        print("Error: No audio data in response", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    audio_bytes = bytes.fromhex(audio_hex)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    size_kb = len(audio_bytes) / 1024
    print(f"✅ Saved to {output_path} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="MiniMax Text-to-Speech")
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument("output", help="Output MP3 file path")
    parser.add_argument("--voice", help="Voice ID (default: from env MINIMAX_TTS_VOICE_ID)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed 0.5-2.0 (default: 1.0)")
    parser.add_argument("--emotion", help="Emotion: happy/sad/angry/fearful/disgusted/surprised/neutral")
    parser.add_argument("--model", default="speech-02-hd", help="Model (default: speech-02-hd)")
    args = parser.parse_args()

    tts(
        text=args.text,
        output_path=args.output,
        voice_id=args.voice,
        speed=args.speed,
        emotion=args.emotion,
        model=args.model,
    )


if __name__ == "__main__":
    main()
