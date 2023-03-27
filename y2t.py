# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import ffmpeg
# import requests
import os
# import openai
# import pytube
import whisper
from pytube import YouTube
import torch
import gc

torch.cuda.empty_cache()
gc.collect()


def download_video_mp4(youtube_url):
  # Create a YouTube object
  yt = YouTube(youtube_url)
  
  # Get the video with the highest resolution and file size
  video = yt.streams.filter(progressive=True, 
                            file_extension='mp4').order_by('resolution').desc().first()
  # Download the video to the current working directory
  video.download()
  
  print('Video downloaded!')
  return 1

download_video_mp4("https://www.youtube.com/watch?v=KHnhKfrJJv8")

input_file=os.listdir()[1]
output_file="trimmed_video.mp4"

def trim(input_file, output_file, start=30, end=60):
    if os.path.exists(output_file):
        os.remove(output_file)
    input_stream = ffmpeg.input(input_file)

    vid = (
        input_stream.video
        .trim(start=start, end=end)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        input_stream.audio
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    joined = ffmpeg.concat(vid, aud, v=1, a=1).node
    output = ffmpeg.output(joined[0], joined[1], output_file)
    output.run()

trim(input_file,output_file,start=100,end=120)

probe_res=probe=ffmpeg.probe(output_file)


def create_audio_file(video_filename):
  # Use ffmpeg to extract the audio track from the video and create an .mp4 audio file
  audio_filename = video_filename.replace(".mp4", ".mp3")
  stream = ffmpeg.input(video_filename)
  stream = ffmpeg.output(stream, audio_filename)
  ffmpeg.run(stream)
  return audio_filename

create_audio_file("trimmed_video.mp4")

#https://github.com/openai/whisper/blob/main/README.md
model = whisper.load_model("medium")

def transcribe(audio_path):
    # pred_model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

audio_file="trimmed_video.mp3"

yt_text = transcribe(audio_file)

from pprint import pprint
pprint(yt_text)


