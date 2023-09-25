# OnlySpeakTTS
 
This is a TTS server that uses a private fork of tortoise to keep generation times and VRAM usage low.
If you play the audio while generating, you can get very close to real-time.

# System Requirements
Generations can use up to 5 Gigs of VRAM, and I average about 7-8 second generation times for full sentences on an RTX 3090, 3-4 seconds for shorter sentences

I Experience no slow-down in generations while running games like Minecraft. I did experience an increase in generation times by 100%~ while maxing my graphics card, playing games like Generation Zero.

I Never tested generating speech while inferencing on a text-generation model at the same time, but I assume it will result in slower generation times for both.

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



# Example Video

https://github.com/Pandaily591/OnlySpeakTTS/assets/100230993/3a81e7b0-d4fd-4555-ab3b-448739a86da3



# Links
I uploaded a longer example to youtube:

https://www.youtube.com/watch?v=XV87AE22a6M



The Tortoise Repo:

https://github.com/neonbjb/tortoise-tts
