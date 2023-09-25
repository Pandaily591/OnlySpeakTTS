# This Fork

I've modified the API to expose a few more settings, as well as decreased the number of steps required to lower the inference times.
You won't be 'cloning' voices, but you will get something similar.

This fork also allows you to easily setup multiple speakers, and keep all the models in memory

#### Requirements
The models require 4.7GB of VRAM

Inference times are about 6-7 seconds on a 3090, it can be substantially longer if your GPU is being used for anything else. Keeping other models loaded won't affect inference times unless they are also inferencing.

There is a token limit, and a audio length limit. You will want to split longer texts.

You could play the audio generated while generating more, which practically generates audio in real time, though it will take a few seconds for the audio to start as it generates the first sentence.

## How do i use this?
There are 3 steps,
1. load the model into memory by storing 'api.TextToSpeech()' into a variable
2. create a voice by calling 'prepare_settings' in the api with the voice settings
3. use the variables given by 'prepare_settings' to generate speech by calling 'tts_with_preset' in the api with the settings and the text

Below is an example of utilizing the api in this fork:
```python
#Import the api and audio files
from OnlySpeak.tortoise import api
from OnlySpeak.tortoise.utils import audio

#Import torchaudio to save the audio tensor to a file
import torchaudio
#import winsound to play the audio file
import winsound
#import os to join paths
import os

#Load the models
tts = api.TextToSpeech()


# Takes in voice data, outputs a list of variables needed to generate audio; This is where you setup each individual voice
def prepare_voice(voice_dir, voice_name, preset="standard", diffusion_temperature=0.75, rate = 25500):
  clips_paths = os.path.join(voice_dir, voice_name)
  reference_clips = [audio.load_audio(clips_paths, p, rate) for p in os.listdir(clips_paths)]
  auto_conditioning, diffusion_conditioning, auto_conds, diffuser = tts.prepare_settings(voice_samples=reference_clips, 
      diffusion_temperature=diffusion_temperature, preset=preset)
  return [auto_conditioning, diffusion_conditioning, auto_conds, diffuser, reference_clips, preset]


# Generate speech with voice_data and text
def generate_speech(text, voice_data, tts):
  auto_conditioning = voice_data[0]
  diffusion_conditioning = voice_data[1]
  auto_conds = voice_data[2]
  diffuser = voice_data[3]
  reference_clips = voice_data[4]
  preset = voice_data[5]
  pcm_audio = tts.tts_with_preset(text, voice_samples=reference_clips, preset=preset,
      auto_conditioning = auto_conditioning, diffusion_conditioning = diffusion_conditioning, auto_conds = auto_conds, diffuser = diffuser)
  
  # Saves the sound to a file called test.wav in the current directory
  torchaudio.save(r"test.wav", pcm_audio.squeeze(0).cpu(), 27250)#26875)
  
  #If you need your sound processed
  #process_sound()
  
  # Play the sound file
  winsound.PlaySound('test.wav', winsound.SND_NOSTOP)
  


# Now call 'prepare_voice' to create a voice
# voice_dir = The directory your voice folders are in
# voice_name = The specific folder your voice files are in
# preset = 'fast' or 'standard'; 'fast' is just slightly faster, but has substantially lower quality
# Rate = the speed of the voice, increase/decreases pitch too, change this number according to your needs
# diffusion_temperature = How varied the expression can be, 0.75 is pretty good
narrator = prepare_voice(voice_dir=r"~\OnlySpeak\tortoise\voices", voice_name="tim_reynolds", preset = "standard", diffusion_temperature=0.75, rate = 24000)

while True:
  text = input("User: ")
  generate_speech(text, narrator)
```
This can be done in what is essentially realtime, as long as you seperate the text by speakers/sentences and generate while playing the audio.
Something to note is that the audio sampling rate is used twice here, when reading the audio clips and when saving the generated clips. You can change the rates at both these places to be different.
You can get an output voice that is significantly different by playing around with them.

If you want to process the sound, you may want to import numpy, wave, AudioSegment from pydub, and soundfile.
You will also want to start by converting the sound file, for some reason the format of the file isn't correct.

```python
import soundfile as sf
from pydub import AudioSegment
import os
import wave
import numpy as np
import winsound
import torchaudio

# Load the file and convert it to int16
def convert_sound(file_name):
        data, samplerate = sf.read(file_name)
        sf.write('test.wav', (data * 32767).astype(np.int16), samplerate)
        sound = wave.open(file_name, 'r')
        return sound

sound = convert_sound('test')
# Export the sound back to a wav file when you are done processing
sound.export(file_name, 'wav')
```

## What can i do with this?
You can run all replies from an LLM into this to provide voice feedback. Combine it with whisper and you can communicate with an LLM using just your voice.
You can again use a package like LangChain to give an LLM tools to perform actions, allowing you to perform actions during vocal conversations.

You can also use a package like Ebooklib to get chapters from ebooks (epubs) and convert them to audiobooks.
To do this, you would want to split the chapters into sentences and generate audio for them individually, then combine them.

Finally, you could use whisper to transcribe your voice to text, then back to any voice you want. If you want to have a voice chat in real time without using your voice, this might be as close as you can get right now.



Below is the original README:






# TorToiSe

Tortoise is a text-to-speech program built with the following priorities:

1. Strong multi-voice capabilities.
2. Highly realistic prosody and intonation.

This repo contains all the code needed to run Tortoise TTS in inference mode.

A (*very*) rough draft of the Tortoise paper is now available in doc format. I would definitely appreciate any comments, suggestions or reviews:
https://docs.google.com/document/d/13O_eyY65i6AkNrN_LdPhpUjGhyTNKYHvDrIvHnHe1GA

### Version history

#### v2.4; 2022/5/17
- Removed CVVP model. Found that it does not, in fact, make an appreciable difference in the output.
- Add better debugging support; existing tools now spit out debug files which can be used to reproduce bad runs.

#### v2.3; 2022/5/12
- New CLVP-large model for further improved decoding guidance.
- Improvements to read.py and do_tts.py (new options)

#### v2.2; 2022/5/5
- Added several new voices from the training set.
- Automated redaction. Wrap the text you want to use to prompt the model but not be spoken in brackets.
- Bug fixes

#### v2.1; 2022/5/2
- Added ability to produce totally random voices.
- Added ability to download voice conditioning latent via a script, and then use a user-provided conditioning latent.
- Added ability to use your own pretrained models.
- Refactored directory structures.
- Performance improvements & bug fixes.

## What's in a name?

I'm naming my speech-related repos after Mojave desert flora and fauna. Tortoise is a bit tongue in cheek: this model
is insanely slow. It leverages both an autoregressive decoder **and** a diffusion decoder; both known for their low
sampling rates. On a K80, expect to generate a medium sized sentence every 2 minutes.

## Demos

See [this page](http://nonint.com/static/tortoise_v2_examples.html) for a large list of example outputs.

Cool application of Tortoise+GPT-3 (not by me): https://twitter.com/lexman_ai

## Usage guide

### Colab

The original colab no longer works by a combination of Google's tendency to forward-break things and Python's package management system. I do not intend to keep fixing it so it has been removed. Apologies!

### Local Installation

If you want to use this on your own computer, you must have an NVIDIA GPU.

First, install pytorch using these instructions: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/).
On Windows, I **highly** recommend using the Conda installation path. I have been told that if you do not do this, you
will spend a lot of time chasing dependency problems.

Next, install TorToiSe and it's dependencies:

```shell
git clone https://github.com/neonbjb/tortoise-tts.git
cd tortoise-tts
python -m pip install -r ./requirements.txt
python setup.py install
```

If you are on windows, you will also need to install pysoundfile: `conda install -c conda-forge pysoundfile`

### do_tts.py

This script allows you to speak a single phrase with one or more voices.
```shell
python tortoise/do_tts.py --text "I'm going to speak this" --voice random --preset fast
```

### read.py

This script provides tools for reading large amounts of text.

```shell
python tortoise/read.py --textfile <your text to be read> --voice random
```

This will break up the textfile into sentences, and then convert them to speech one at a time. It will output a series
of spoken clips as they are generated. Once all the clips are generated, it will combine them into a single file and
output that as well.

Sometimes Tortoise screws up an output. You can re-generate any bad clips by re-running `read.py` with the --regenerate
argument.

### API

Tortoise can be used programmatically, like so:

```python
reference_clips = [utils.audio.load_audio(p, 22050) for p in clips_paths]
tts = api.TextToSpeech()
pcm_audio = tts.tts_with_preset("your text here", voice_samples=reference_clips, preset='fast')
```

## Voice customization guide

Tortoise was specifically trained to be a multi-speaker model. It accomplishes this by consulting reference clips.

These reference clips are recordings of a speaker that you provide to guide speech generation. These clips are used to determine many properties of the output, such as the pitch and tone of the voice, speaking speed, and even speaking defects like a lisp or stuttering. The reference clip is also used to determine non-voice related aspects of the audio output like volume, background noise, recording quality and reverb.

### Random voice

I've included a feature which randomly generates a voice. These voices don't actually exist and will be random every time you run
it. The results are quite fascinating and I recommend you play around with it!

You can use the random voice by passing in 'random' as the voice name. Tortoise will take care of the rest.

For the those in the ML space: this is created by projecting a random vector onto the voice conditioning latent space.

### Provided voices

This repo comes with several pre-packaged voices. Voices prepended with "train_" came from the training set and perform
far better than the others. If your goal is high quality speech, I recommend you pick one of them. If you want to see
what Tortoise can do for zero-shot mimicking, take a look at the others.

### Adding a new voice

To add new voices to Tortoise, you will need to do the following:

1. Gather audio clips of your speaker(s). Good sources are YouTube interviews (you can use youtube-dl to fetch the audio), audiobooks or podcasts. Guidelines for good clips are in the next section.
2. Cut your clips into ~10 second segments. You want at least 3 clips. More is better, but I only experimented with up to 5 in my testing.
3. Save the clips as a WAV file with floating point format and a 22,050 sample rate.
4. Create a subdirectory in voices/
5. Put your clips in that subdirectory.
6. Run tortoise utilities with --voice=<your_subdirectory_name>.

### Picking good reference clips

As mentioned above, your reference clips have a profound impact on the output of Tortoise. Following are some tips for picking
good clips:

1. Avoid clips with background music, noise or reverb. These clips were removed from the training dataset. Tortoise is unlikely to do well with them.
2. Avoid speeches. These generally have distortion caused by the amplification system.
3. Avoid clips from phone calls.
4. Avoid clips that have excessive stuttering, stammering or words like "uh" or "like" in them.
5. Try to find clips that are spoken in such a way as you wish your output to sound like. For example, if you want to hear your target voice read an audiobook, try to find clips of them reading a book.
6. The text being spoken in the clips does not matter, but diverse text does seem to perform better.

## Advanced Usage

### Generation settings

Tortoise is primarily an autoregressive decoder model combined with a diffusion model. Both of these have a lot of knobs
that can be turned that I've abstracted away for the sake of ease of use. I did this by generating thousands of clips using
various permutations of the settings and using a metric for voice realism and intelligibility to measure their effects. I've
set the defaults to the best overall settings I was able to find. For specific use-cases, it might be effective to play with
these settings (and it's very likely that I missed something!)

These settings are not available in the normal scripts packaged with Tortoise. They are available, however, in the API. See
```api.tts``` for a full list.

### Prompt engineering

Some people have discovered that it is possible to do prompt engineering with Tortoise! For example, you can evoke emotion
by including things like "I am really sad," before your text. I've built an automated redaction system that you can use to
take advantage of this. It works by attempting to redact any text in the prompt surrounded by brackets. For example, the
prompt "\[I am really sad,\] Please feed me." will only speak the words "Please feed me" (with a sad tonality).

### Playing with the voice latent

Tortoise ingests reference clips by feeding them through individually through a small submodel that produces a point latent,
then taking the mean of all of the produced latents. The experimentation I have done has indicated that these point latents
are quite expressive, affecting everything from tone to speaking rate to speech abnormalities.

This lends itself to some neat tricks. For example, you can combine feed two different voices to tortoise and it will output
what it thinks the "average" of those two voices sounds like.

#### Generating conditioning latents from voices

Use the script `get_conditioning_latents.py` to extract conditioning latents for a voice you have installed. This script
will dump the latents to a .pth pickle file. The file will contain a single tuple, (autoregressive_latent, diffusion_latent).

Alternatively, use the api.TextToSpeech.get_conditioning_latents() to fetch the latents.

#### Using raw conditioning latents to generate speech

After you've played with them, you can use them to generate speech by creating a subdirectory in voices/ with a single
".pth" file containing the pickled conditioning latents as a tuple (autoregressive_latent, diffusion_latent).

### Send me feedback!

Probabilistic models like Tortoise are best thought of as an "augmented search" - in this case, through the space of possible
utterances of a specific string of text. The impact of community involvement in perusing these spaces (such as is being done with
GPT-3 or CLIP) has really surprised me. If you find something neat that you can do with Tortoise that isn't documented here,
please report it to me! I would be glad to publish it to this page.

## Tortoise-detect

Out of concerns that this model might be misused, I've built a classifier that tells the likelihood that an audio clip
came from Tortoise.

This classifier can be run on any computer, usage is as follows:

```commandline
python tortoise/is_this_from_tortoise.py --clip=<path_to_suspicious_audio_file>
```

This model has 100% accuracy on the contents of the results/ and voices/ folders in this repo. Still, treat this classifier
as a "strong signal". Classifiers can be fooled and it is likewise not impossible for this classifier to exhibit false
positives.

## Model architecture

Tortoise TTS is inspired by OpenAI's DALLE, applied to speech data and using a better decoder. It is made up of 5 separate
models that work together. I've assembled a write-up of the system architecture here:
[https://nonint.com/2022/04/25/tortoise-architectural-design-doc/](https://nonint.com/2022/04/25/tortoise-architectural-design-doc/)

## Training

These models were trained on my "homelab" server with 8 RTX 3090s over the course of several months. They were trained on a dataset consisting of
~50k hours of speech data, most of which was transcribed by [ocotillo](http://www.github.com/neonbjb/ocotillo). Training was done on my own
[DLAS](https://github.com/neonbjb/DL-Art-School) trainer.

I currently do not have plans to release the training configurations or methodology. See the next section..

## Ethical Considerations

Tortoise v2 works considerably better than I had planned. When I began hearing some of the outputs of the last few versions, I began
wondering whether or not I had an ethically unsound project on my hands. The ways in which a voice-cloning text-to-speech system
could be misused are many. It doesn't take much creativity to think up how.

After some thought, I have decided to go forward with releasing this. Following are the reasons for this choice:

1. It is primarily good at reading books and speaking poetry. Other forms of speech do not work well.
2. It was trained on a dataset which does not have the voices of public figures. While it will attempt to mimic these voices if they are provided as references, it does not do so in such a way that most humans would be fooled.
3. The above points could likely be resolved by scaling up the model and the dataset. For this reason, I am currently withholding details on how I trained the model, pending community feedback.
4. I am releasing a separate classifier model which will tell you whether a given audio clip was generated by Tortoise or not. See `tortoise-detect` above.
5. If I, a tinkerer with a BS in computer science with a ~$15k computer can build this, then any motivated corporation or state can as well. I would prefer that it be in the open and everyone know the kinds of things ML can do.

### Diversity

The diversity expressed by ML models is strongly tied to the datasets they were trained on.

Tortoise was trained primarily on a dataset consisting of audiobooks. I made no effort to
balance diversity in this dataset. For this reason, Tortoise will be particularly poor at generating the voices of minorities
or of people who speak with strong accents.

## Looking forward

Tortoise v2 is about as good as I think I can do in the TTS world with the resources I have access to. A phenomenon that happens when
training very large models is that as parameter count increases, the communication bandwidth needed to support distributed training
of the model increases multiplicatively. On enterprise-grade hardware, this is not an issue: GPUs are attached together with
exceptionally wide buses that can accommodate this bandwidth. I cannot afford enterprise hardware, though, so I am stuck.

I want to mention here
that I think Tortoise could be a **lot** better. The three major components of Tortoise are either vanilla Transformer Encoder stacks
or Decoder stacks. Both of these types of models have a rich experimental history with scaling in the NLP realm. I see no reason
to believe that the same is not true of TTS.

The largest model in Tortoise v2 is considerably smaller than GPT-2 large. It is 20x smaller that the original DALLE transformer.
Imagine what a TTS model trained at or near GPT-3 or DALLE scale could achieve.

If you are an ethical organization with computational resources to spare interested in seeing what this model could do
if properly scaled out, please reach out to me! I would love to collaborate on this.

## Acknowledgements

This project has garnered more praise than I expected. I am standing on the shoulders of giants, though, and I want to
credit a few of the amazing folks in the community that have helped make this happen:

- Hugging Face, who wrote the GPT model and the generate API used by Tortoise, and who hosts the model weights.
- [Ramesh et al](https://arxiv.org/pdf/2102.12092.pdf) who authored the DALLE paper, which is the inspiration behind Tortoise.
- [Nichol and Dhariwal](https://arxiv.org/pdf/2102.09672.pdf) who authored the (revision of) the code that drives the diffusion model.
- [Jang et al](https://arxiv.org/pdf/2106.07889.pdf) who developed and open-sourced univnet, the vocoder this repo uses.
- [Kim and Jung](https://github.com/mindslab-ai/univnet) who implemented univnet pytorch model.
- [lucidrains](https://github.com/lucidrains) who writes awesome open source pytorch models, many of which are used here.
- [Patrick von Platen](https://huggingface.co/patrickvonplaten) whose guides on setting up wav2vec were invaluable to building my dataset.

## Notice

Tortoise was built entirely by me using my own hardware. My employer was not involved in any facet of Tortoise's development.

If you use this repo or the ideas therein for your research, please cite it! A bibtex entree can be found in the right pane on GitHub.
