#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 12:20:47 2023

@author: itqs
"""

import whisper

audio_file="trimmed_video.wav"

#https://github.com/openai/whisper/blob/main/README.md
model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio(audio_file)
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)
# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

def transcribe(audio_path):
    # pred_model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


yt_text = transcribe(audio_file)

from pprint import pprint
pprint(yt_text)

