# OnlySpeakTTS
 
This is a TTS server that uses a private fork of tortoise to keep generation times and VRAM usage low.
If you play the audio while generating, you can get very close to real-time.

You will need to provide your own audio clips.
Store them in 'Tortoise/tortoise/voices/{voice_name}'
you will want 2-3x 10 second clips, if it doesn't come out perfect, play around with the parameters.
If you don't mind mix n' matching, you can include a few other clips that provide accent and dynamic range.


You may be able to get more emotion if you add a 'angry' or 'happy' clip to the mix, then generate different voices for each emotion. As long as you can tell what emotion to use, you can quickly swap between them.

# System Requirements
Generations can use up to 5 Gigs of VRAM, and I average about 7-8 second generation times for full sentences on an RTX 3090, 3-4 seconds for shorter sentences.
The 'fast' preset is slightly faster. Quality isn't bad, it's just not as smooth.

I Experience no slow-down in generations while running games like Minecraft. I did experience an increase in generation times by 100%~ while maxing my graphics card, playing games like Generation Zero.

I Never tested generating speech while inferencing on a text-generation model at the same time, but I assume it will result in slower generation times for both.
It's perfectly okay to keep the models loaded into VRAM and go back and forth, though.

# What Can This Do?
Assuming you use the server.py script, all inputs will automatically be seperated into segments that are within tortoise's max range.

You also have the option to save the generated voice tensors to files, and load from them later. This ensures that voices are consistent, instead of relying on randomly generated latents each time.

You can load voices from files in a second or less, using mutliple voices is perfectly viable.


# How do i use this?
Tortoise-tts has it's own way it wants to be used, but I completely messed up the api.py script in this fork and didn't feel like fixing it.

For this fork, just use the server.py script and send http POST requests to port 7332
You can check the client.py script to see how these post requests should be formatted, what commands you can use, and how to use them.

You can:
 1. Generate a new voice
 2. Redo the previous generation if you got a bad one (becuase it's random)
 3. Save the current voice to files that can be loaded later
 4. Send a message to be spoken


In addition to the requirments for Tortoise, the server.py, client.py, and speech.py also have a few:

colorama, 
requests, 
soundfile, 
wave, 
pydub, 
threading, 
winsound, 
rich



# Installation
You can create a venv, a conda env, or whatever. The original installation instructions for Tortoise still apply, but you may need to manually install setuptools before using the setup.py script
```
pip install setuptools
```


# Example Video


https://github.com/Pandaily591/OnlySpeakTTS/assets/100230993/b9a2b08c-0202-43f4-b94b-7dd45e4d60c0


# Cloning Voices


https://github.com/Pandaily591/OnlySpeakTTS/assets/100230993/18fe525b-fb57-408d-8ede-0a15f3753734

This clip of laura croft uses around 5 diffusion iterations, that give it the poor quality to match the original voice. Alternatively, I could have used 7-12 diffusion iterations which would have given a much clearer voice for almost no extra generation time.










# Links
I uploaded a longer example to youtube (the Lara Croft voice in this video is old):

https://www.youtube.com/watch?v=XV87AE22a6M



The Tortoise Repo:

https://github.com/neonbjb/tortoise-tts
