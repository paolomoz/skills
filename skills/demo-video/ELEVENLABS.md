# ElevenLabs TTS Reference

## Voice Selection

- Generate 2-3 voice samples of act 1 script before committing to a voice. Let user compare.
- Store the chosen voice ID in the build script. When changing voice, delete ALL `audio/act*.mp3` files and ALL `segments/*.mp4` files to force full regeneration. Cached audio from a previous voice will silently persist otherwise.

## Speed Parameter

Range 0.7-1.2, default 1.0. If user wants faster/slower delivery, adjust via the `speed` field in the API request JSON (not voice_settings).

## Script Pacing

Target ~2.5 words/second for natural narration pace. For a 15s video segment, aim for ~37 words. Generate TTS and check actual duration — ElevenLabs varies by voice and content.

## API Endpoints

### List voices
```bash
curl -H "xi-api-key: $KEY" https://api.elevenlabs.io/v1/voices
```

### Generate speech
```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -H "xi-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"text": "...", "model_id": "eleven_multilingual_v2",
       "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.15}}'
```

## Recommended Voices for Product Demos

| Voice | ID | Style |
|-------|----|-------|
| Eric | `cjVigY5qzO86Huf0OWal` | Smooth, trustworthy |
| Daniel | `onwK4e9ZLuTAKqWW03F9` | Steady broadcaster |
| Brian | `nPczCjzI2devNBz1zQrb` | Deep, resonant |
| George | `JBFqnCBsd6RMkjVDRZzb` | Warm storyteller |
