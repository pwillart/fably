export LANG=en_US.UTF-8
# export OpenAI API key here

#"Bye! Come back soon!" -> bye.wav
#"Adios! Vuelve pronto!" -> bye_es.wav
#"I'm deleting all of the saved files." -> delete.wav
#"Voy a borrar todos los archivos guardados." -> delete_es.wav
#"Hi, I'm Ereezo! [pause] I LOVE telling stories!" -> hi.wav
#"Hola, Soy Erizo! [pause] Me encanta contár cuentos!" -> hi_es.wav
#"Hi! [pause] I'm Ereezo!" -> hi_short.wav
#"Hola! [pause] Soy Erizo!" -> hi_short_es.wav
#"Press my hand and tell me what story you'd like me to tell you." -> instructions.wav
#"Presiona mi mano y dime qué cuento te gustaría que te cuente." -> instructions_es.wav
#"Hmmm... Let me think about that..." -> let_me_think.wav
#"Hmmm... Déjame pensar en eso..." -> let_me_think_es.wav
#"Sorry! I don't understand that." -> sorry.wav
#"Lo siento, no entiendo eso." -> sorry_es.wav
#"What story would you like me to tell you." -> what_story.wav
#"Dime que cuento te gustaria que te cuente." -> what_story_es.wav
#"Hmmm... Something went wrong. Do you want to try again?" -> wrong.wav
#"Hmmm... algo salio mal. Quieres volver otra vez?" -> wrong_es.wav


curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Bye! [pause]",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output bye.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Adios! [pause]",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output bye_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "I am deleting all of the saved files.",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output delete.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Voy a borrar todos los archivos guardados.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output delete_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hi, I am Ereezo! [pause] I LOVE telling stories!",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output hi.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hola, Soy Erizo! [pause] Me encanta contár cuentos!",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output hi_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hi! [pause] I am Ereezo!",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output hi_short.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hola! [pause] Soy Erizo!",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output hi_short_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Press my hand and tell me what story you would like me to tell you.",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output instructions.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Presiona mi mano y dime qué cuento te gustaría que te cuente.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output instructions_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hmmm... Let me think about that...",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output let_me_think.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hmmm... Déjame pensar en eso...",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output let_me_think_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Sorry! I do not understand that.",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output sorry.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Lo siento, no entiendo eso.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output sorry_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "What story would you like me to tell you.",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output what_story.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Dime que cuento te gustaria que te cuente.",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output what_story_es.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hmmm. Something went wrong. [pause] Do you want to try again?",
    "voice": "nova",
    "response_format": "wav",
    "speed": 1
  }' \
  --output wrong.wav

curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "Hmmm... algo salio mal. [pause] Quieres volver otra vez?",
    "voice": "nova",
    "language": "es",
    "response_format": "wav",
    "speed": 1
  }' \
  --output wrong_es.wav