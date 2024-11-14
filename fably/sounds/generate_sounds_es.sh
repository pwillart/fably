#!/bin/bash
export LANG=en_US.UTF-8
# export open ai api key here

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Adiós.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output bye_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Voy a borrar todos los archivos guardados.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output delete_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hola, soy Fably, tu compañera de cuentos.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output hi_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hola, soy Fably.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output hi_short_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Presiona mi mano y dime que cuento te gustaria que te cuente.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output instructions_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Lo siento, no entiendo eso.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output sorry_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Dime que cuento te gustaria que te cuente.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output what_story_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hmmm... algo salio mal. Quieres volver otra vez?",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 0.8
  }' \
  --output wrong_es.wav
