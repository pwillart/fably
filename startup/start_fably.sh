#!/bin/bash

sudo chmod -R a+rw /dev/snd

echo "Wait for a microphone to be available"
while ! arecord -l 2>&1 | grep -q 'card [0-9]'; do
    sleep 1
done
echo "Microphone is available"

amixer -q set Master 65%

echo "Activate Python virtual environment..."
# shellcheck disable=SC2164
cd /home/pwillart
source /home/pwillart/.venv/bin/activate

echo "Run Fably continuously..."
# shellcheck disable=SC2164
cd fably

# Run Fably in a constant loop (using the default APIs)
fably --loop
#fably --loop --debug

# Use this command to talk to APIs running on your own machine.
# See https://github.com/stefanom/fably/blob/main/servers/README.md for more information on running APIs locally.
# fably --loop --stt-url=http://mygpu.local:5000/v1 --llm-url=http://mygpu.local:11434/v1 --llm-model=llama3:latest --tts-url=http://mygpu.local:5001/v1
