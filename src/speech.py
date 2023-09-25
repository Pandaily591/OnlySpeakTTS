import os
import threading
import winsound
from rich.progress import track
from rich.progress import Progress
from rich.progress import TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
import torch
from colorama import Fore
import time
import re



generation_progress = None
generation_task = None
generating_thread = None
task_total = 0

def generate_progress_bar(total, num, out_of):
    global generation_task
    global generation_progress
    global task_total
    total=total+1
    task_total = total
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=20),
        MofNCompleteColumn(),
        TimeRemainingColumn(compact=True, elapsed_when_finished=True),
        refresh_per_second=30

    ) as progress:
        generation_progress = progress
        generation_task = progress.add_task(f"[green]Generating ({num}/{out_of})...", total=total)
        time.sleep(1)
        while not progress.finished:
            time.sleep(0.42)
            progress.update(generation_task, advance=1)
        




class Synthesizer:
    """This is the extended API, it works between tortoise-tts and the main program, all you need to do is:
    1. Instance this class
    2. call load() to specifically load the tts models into memory
    2. call new_voice() with your voice info to get usable voice data
    3. call synthesize() with your text and voice data"""
    def __init__(self) -> None:
        self.texts = []
        self.clips = []
        self.tracks = []
        self.playing = False
        self.stopped = True
        self.text_cleaner = TextCleaner()
        self.playing_thread=None
    def synthesize(self, sender, raw_text, voice, verbose, clean_text=False, split_text=False):
        """Take in the voice and raw text, split and prepare the text, then synthesize speech and add it to a buffer to be played."""
        global generation_progress
        global generation_task
        global generating_thread
        global task_total
        #   First, remove any hallucinations
        if len(raw_text)<2:return
        if clean_text:
            raw_text = self.text_cleaner.remove_hallucinations(text=raw_text)
            raw_text = self.text_cleaner.prepare_text(raw_text=raw_text)
        #   Then, split the text and make changes for pronunciation
        split, wordcount = self.text_cleaner.split(text=raw_text)
        #   Iterate through all the slices, add them to the buffer
        if len(split)==0 and len(raw_text)>1: self.texts.append(raw_text)
        while len(split)>0:
            i = split[0]
            split.pop(0)
            self.texts.append(i)

        #   Iterate through the buffer and generate speech for each slice, add clip paths to another buffer
        num=0
        out_of = len(self.texts)
        while len(self.texts)>0:#track(range(len(self.texts)), description="Generating..."):
            num+=1
            wordcount = len(self.texts[0].split(" "))
            print(Fore.WHITE+f"({sender}) "+Fore.RED+self.texts[0])
            generating_thread = threading.Thread(target=generate_progress_bar, name="GenerationProgress", args=[wordcount, num, out_of])
            generating_thread.daemon=True
            generating_thread.start()
            text = self.texts[0]
            self.texts.pop(0)
            if text.isspace(): continue
            if len(text)<3: continue
            #print("Generating: "+text)
            clip = self.model.generate_speech(text=text, voice=voice, word_count=len(text.split(" ")), verbose=verbose)
            try:
                generation_progress.update(generation_task, completed=task_total)
                generating_thread.join()
            except: pass
            self.clips.append(clip)
            
            #   restart the audio thread if it has stopped
            if self.stopped:
                self.stopped = False
                self.playing = True
                try:
                    if self.playing_thread:
                        self.playing_thread.join()
                        self.playing_thread=None
                except: pass
                self.playing_thread = threading.Thread(target=self.speak, name="AudioPlayingThread")
                self.playing_thread.daemon=True
                self.playing_thread.start()
    def speak(self):
        "Runs in a separate thread to play any clips that have been queued up."
        while len(self.clips)>0:
            current_clip=self.clips[0]
            self.clips.pop(0)
            self.tracks.append(current_clip)
            #print("Playing ({})".format(current_clip))
            winsound.PlaySound(current_clip, winsound.SND_NOSTOP)
            #print("Done Playing ({})".format(current_clip))
            #os.remove(current_clip)
        self.stopped = True
        if len(self.texts)==0:
            self.model.stitch_tracks(self.tracks)
            self.tracks.clear()

    

    def load(self):
        "Specifically load the tts models into memory."
        self.model = Model()
    def new_voice(self, voice_dir, voice_name, preset, diffusion_temperature, rate, load=False):
        "Prepare the voice data using the given parameters, return the voice data."
        if load:
            voice = self.load_voice(voice_path=os.path.join("voice_tensors", voice_name))
            if voice: return voice
        return self.model.prepare_voice(voice_dir, voice_name, preset, diffusion_temperature, rate)
    def save_voice(self, voice_path, voice):
        if not os.path.exists(voice_path):
            os.makedirs(voice_path)
        torch.save(voice[0], f"{voice_path}/Auto_Conditioning.pt")
        torch.save(voice[1], f"{voice_path}/Diffusion_Conditioning.pt")
        torch.save(voice[2], f"{voice_path}/Auto_Conds.pt")
        torch.save(voice[3], f"{voice_path}/Diffuser.pt")
        torch.save(voice[4], f"{voice_path}/Reference_Clips.pt")
    def load_voice(self, voice_path):
        voice = []
        for p in os.listdir(voice_path): print(Fore.GREEN+"Loaded "+p)
        if len(os.listdir(voice_path))<5: return None
        #if os.path.exists("wavs/test"):
        voice.append(torch.load(f"{voice_path}/Auto_Conditioning.pt"))
        voice.append(torch.load(f"{voice_path}/Diffusion_Conditioning.pt"))
        voice.append(torch.load(f"{voice_path}/Auto_Conds.pt"))
        voice.append(torch.load(f"{voice_path}/Diffuser.pt"))
        voice.append(torch.load(f"{voice_path}/Reference_Clips.pt"))
        voice.append("standard")
        return voice








class TextCleaner:
    def __init__(self) -> None:
        pass
    def remove_hallucinations(self, text):
        try:
            text = text.split("#")[0]
        except:
            pass
        return text
    def prepare_text(self, raw_text):
        "Replace anything that tortoise can't pronounce"
        start = raw_text[:3]

        #   Remove 'erm' and leading ','; these are kind of like hallucinations
        if start == "erm":
            raw_text=raw_text[3:]
        if raw_text[0]==",": raw_text=raw_text[1:]
        if raw_text[0]==" ": raw_text=raw_text[1:]
        if raw_text[0]==",": raw_text=raw_text[1:]
        
        #   Tortoise does NOT like '....'
        #try: raw_text=raw_text.replace("....", "")
        #except: pass
        #try: raw_text=raw_text.replace("...", ",")
        #except: pass
        #   It screws up with these too
        try: raw_text=raw_text.replace("i.e.", "that is,")
        except: pass
        try: raw_text=raw_text.replace("e.g.", "for example,")
        except: pass

        #   tts doesn't like special characters
        raw_text=raw_text.replace("*", " times ")
        raw_text=raw_text.replace("+", " plus ")
        raw_text=raw_text.replace("%", " percent")
        raw_text=raw_text.replace("°F", " degrees fahrenheit")
        raw_text=raw_text.replace("°C", " degrees celsius")
        raw_text=raw_text.replace("°", " degrees")
        raw_text=raw_text.replace(";", ",")

        #   We check for sentences in general
        #raw_text=raw_text.replace("!", ".")
        #raw_text=raw_text.replace("?", ".")

        return raw_text
    

    def split(self, text):
        texts = []

        #if text[-1] == ".": pass
        #else: text=text+". "
        
        #   First, we seperate the sentences
        sentences = text.split(". ")
        if len(sentences)==0: texts.append(text)
        while len(sentences)>0:
            sentence = sentences[0]
            sentences.pop(0)
            split = sentence.split(" ")
            if len(split)<=30:
                #   If the next sentence got cutoff, then attach it to the last text
                if len(split)>2:
                    texts.append(sentence)
                else:
                    seg = ''.join([str(x+" ") for x in split])
                    try:
                        texts[-1] = texts[-1]+". "+seg
                    except: pass
            else:
                #   Continue splitting at the 20 word mark
                while len(split)>0:
                    split1 = split[:18]
                    seg1 = ''.join([str(x+" ") for x in split1])
                    if len(split[:18])<10:
                        texts[-1] = texts[-1]+seg1
                        split.clear()
                    else:
                        texts.append(seg1)
                        split = split[18:]
        
        #   Some final stuff, like adding a '.'
        texts2 = []
        wordcount = 0
        while len(texts)>0:
            text = texts[0]
            texts.pop(0)
            wordcount += len(text.split(" "))
            #   Remove parenthesis in each line
            while '(' in text:
                first=text.split("(")[0]
                last = text.split(")")[1]
                text=first+" "+last
            while ')' in text:
                text = text.split(")")[1]
            if len(text)>2:
                text = text+"."
                texts2.append(text)
            #print(text)


        return texts2, wordcount










from Tortoise.tortoise import api
from Tortoise.tortoise.utils import audio
import soundfile as sf
import wave
import numpy as np
from pydub import AudioSegment
import torchaudio

class Model():
    """Communicates with the tortoise API, allows for cleaner code in the synthesize class."""
    def __init__(self) -> None:
        self.load_model()
    
    def load_model(self):
        self.tts = api.TextToSpeech()

    def prepare_voice(self, voice_dir, voice_name, preset, diffusion_temperature, rate):
        clips_paths = os.path.join(voice_dir, voice_name)
        reference_clips = [audio.load_audio(clips_paths, p, rate) for p in os.listdir(clips_paths)]
        auto_conditioning, diffusion_conditioning, auto_conds, diffuser = self.tts.prepare_settings(voice_samples=reference_clips, 
            diffusion_temperature=diffusion_temperature, preset=preset)
        return [auto_conditioning, diffusion_conditioning, auto_conds, diffuser, reference_clips, preset]


    def generate_speech(self, text, voice, word_count, verbose):#, voice_data, save_rate=25500):
        voice_data = voice
        save_rate = 27550
        auto_conditioning = voice_data[0]
        diffusion_conditioning = voice_data[1]
        auto_conds = voice_data[2]
        diffuser = voice_data[3]
        reference_clips = voice_data[4]
        preset = voice_data[5]
        pcm_audio = self.tts.tts_with_preset(text, voice_samples=reference_clips, preset=preset,
            auto_conditioning = auto_conditioning, diffusion_conditioning = diffusion_conditioning, auto_conds = auto_conds, diffuser = diffuser,
            word_count=word_count, verbose=verbose)
    
        # Saves the sound to a file called test.wav in the current directory
        
        if not os.path.exists("audio"):
            os.makedirs("audio")
        if not os.path.exists("audio/wavs"):
            os.makedirs("audio/wavs")
        new_path = ""
        i = 0
        while os.path.exists("audio/wavs/test%s.wav" % i):
            i += 1
        torchaudio.save(r"audio/wavs/test{}.wav".format(i), pcm_audio.squeeze(0).cpu(), save_rate)
    
        #If you need your sound processed
        self.process_sound(r"audio/wavs/test{}.wav".format(i))
        return r"audio/wavs/test{}.wav".format(i)

    def process_sound(self, clip):
        def convert_sound():
            data, samplerate = sf.read(clip)
            sf.write(clip, (data * 32767).astype(np.int16), samplerate)
            sound = wave.open(clip, 'r')
            #print("Converted sound file!")
        
        def trim_sound(sound):
            def detect_leading_silence(sound, silence_threshold=-45.0, chunk_size=5):
                trim_ms = 0 # ms
                assert chunk_size > 0 # to avoid infinite loop
                while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
                    trim_ms += chunk_size
                return trim_ms
            start_trim = detect_leading_silence(sound)
            end_trim = detect_leading_silence(sound.reverse())
            if end_trim-300 < len(sound):
                end_trim-=300
            duration = len(sound)    
            trimmed_sound = sound[0:duration-end_trim]
            return trimmed_sound
        
        try:
            sound = wave.open(clip, 'r')
        except:
            convert_sound()
        
        trimmed_sound = trim_sound(AudioSegment.from_file(clip, format="wav"))
        trimmed_sound.export(clip, 'wav')

    def stitch_tracks(self, segments):
        'Merge multiple audio tracks'
        tracks = []
        for i in segments:
            #print(i)
            tracks.append(AudioSegment.from_file(i, format="wav"))
            os.remove(i)
        audio_track = tracks[0]
        for i in tracks[1:]:
            audio_track+=i
        #track = tracks[0] + tracks[1]
        file_handle = audio_track.export("audio/clip.wav", format="wav")
        #winsound.PlaySound(path, winsound.SND_NOSTOP)
        if file_handle is not None:
            return file_handle
        else:
            return None



  
