import src.speech as speech
import os

HOST = "localhost"
PORT = 7332


voice = None
synthesizer = speech.Synthesizer()



CURRENT_VOICE = ""
LOADED_VOICE = None

#   Remember the last parameters for 'REDO'
LAST_NAME = None
LAST_PRESET = None
LAST_TEMP = None
LAST_RATE = None


def load_tts():
    print("LOADING TTS")
    synthesizer.load()


if __name__ == "__main__":
    #   Load the model
    load_tts()



import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from flask import Flask, request
app = Flask(__name__)
@app.route('/', methods=['POST'])
def result():
    global CURRENT_VOICE
    global LOADED_VOICE
    global LAST_NAME 
    global LAST_PRESET
    global LAST_TEMP
    global LAST_RATE
    global synthesizer
    if "MESSAGE" in request.form:
        #   Change the voice to a different one in the voice_tensors folder
        if "VOICE" in request.form:
            if request.form["VOICE"] != CURRENT_VOICE:
                print("CHANGING VOICE...")
                CURRENT_VOICE = request.form["VOICE"]
                LOADED_VOICE = synthesizer.load_voice(os.path.join("voice_tensors", CURRENT_VOICE))
        synthesizer.synthesize(sender=CURRENT_VOICE, raw_text=request.form["MESSAGE"], clean_text=request.form["VOICE"], voice=LOADED_VOICE, verbose=False)

    else:
        print(request.form)
        #   Save voice tensors
        if "SAVE" in request.form:
            print("SAVING VOICE...")
            synthesizer.save_voice(voice_path=os.path.join("voice_tensors", CURRENT_VOICE), voice=LOADED_VOICE)
            print("DONE!")
            return 'DONE'
        #   Generate new tensors with the given clips and parameters
        if "NEW" in request.form:
            #   Hopefully, the client sent the following information
            voice_data = {}
            voice_data["name"] = request.form["name"]
            voice_data["preset"] = request.form["preset"]
            voice_data["temp"] = float(request.form["temp"])
            voice_data["rate"] = int(request.form["rate"])
            print("GENERATING VOICE...")
            LOADED_VOICE = synthesizer.new_voice(voice_dir=r"Tortoise\tortoise\voices", 
                                                voice_name=voice_data["name"], 
                                                preset=voice_data["preset"], 
                                                diffusion_temperature=voice_data["temp"], 
                                                rate=voice_data["rate"])
            CURRENT_VOICE = voice_data["name"]
            LAST_NAME = request.form["name"]
            LAST_PRESET = request.form["preset"]
            LAST_TEMP = float(request.form["temp"])
            LAST_RATE = int(request.form["rate"])
            print("DONE!")
            return 'DONE'
        #   Retry generation with the same parameters
        if "REDO" in request.form:
            print("REDO...")
            LOADED_VOICE = synthesizer.new_voice(voice_dir=r"Tortoise\tortoise\voices", 
                                                voice_name=LAST_NAME, 
                                                preset=LAST_PRESET, 
                                                diffusion_temperature=LAST_TEMP, 
                                                rate=LAST_RATE)
            print("DONE!")
            return 'DONE'
        print("No Function Found!")
    return 'DONE' # response to your request.
app.run(debug=False, port=PORT)












