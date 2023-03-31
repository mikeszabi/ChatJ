#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 11:45:36 2023

@author: itqs
"""

from google.cloud import speech
import os
import io

#setting Google credential
os.environ['GOOGLE_APPLICATION_CREDENTIALS']= 'deep-timer-340817-2dd7c298f444.json'
# create client instance 
# client = speech.SpeechClient()

# #the path of your audio file
# file_name = "trimmed_video.wav"
# with io.open(file_name, "rb") as audio_file:
#     content = audio_file.read()
#     audio = speech.RecognitionAudio(content=content)
    
# config = speech.RecognitionConfig(
#     encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#     enable_automatic_punctuation=True,
#     audio_channel_count=2,
#     language_code="hu",
# )

# Sends the request to google to transcribe the audio
# response = client.recognize(request={"config": config, "audio": audio})

# Reads the response
# for result in response.results:
#     print("Transcript: {}".format(result.alternatives[0].transcript))

def speech_to_text(
    config: speech.RecognitionConfig,
    audio: speech.RecognitionAudio,
) -> speech.RecognizeResponse:
    client = speech.SpeechClient()

    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)

    return response


def print_response(response: speech.RecognizeResponse):
    for result in response.results:
        print_result(result)


# def print_result(result: speech.SpeechRecognitionResult):
#     best_alternative = result.alternatives[0]
#     print("-" * 80)
#     print(f"language_code: {result.language_code}")
#     print(f"transcript:    {best_alternative.transcript}")
#     print(f"confidence:    {best_alternative.confidence:.0%}")
    
    
config = speech.RecognitionConfig(
    language_code="hu",
    enable_automatic_punctuation=True,
    audio_channel_count=2,
    enable_word_time_offsets=True,
)
file_name = "trimmed_video.wav"
with io.open(file_name, "rb") as audio_file:
    content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

response = speech_to_text(config, audio)
print_response(response)


def print_result(result: speech.SpeechRecognitionResult):
    best_alternative = result.alternatives[0]
    print("-" * 80)
    print(f"language_code: {result.language_code}")
    print(f"transcript:    {best_alternative.transcript}")
    print(f"confidence:    {best_alternative.confidence:.0%}")
    print("-" * 80)
    for word in best_alternative.words:
        start_s = word.start_time.total_seconds()
        end_s = word.end_time.total_seconds()
        print(f"{start_s:>7.3f} | {end_s:>7.3f} | {word.word}")


# response = speech_to_text(config, audio)
        
print_response(response)
      
# def transcribe_gcs_with_word_time_offsets(audio):
#     """Transcribe the given audio  asynchronously and output the word time
#     offsets."""

#     client = speech.SpeechClient()

#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         language_code="hu",
#         enable_word_time_offsets=True,
#         enable_automatic_punctuation=True,
#         audio_channel_count=2,
#     )

#     operation = client.long_running_recognize(config=config, audio=audio)

#     print("Waiting for operation to complete...")
#     result = operation.result(timeout=90)

#     for result in result.results:
#         alternative = result.alternatives[0]
#         print("Transcript: {}".format(alternative.transcript))
#         print("Confidence: {}".format(alternative.confidence))

#         for word_info in alternative.words:
#             word = word_info.word
#             start_time = word_info.start_time
#             end_time = word_info.end_time

#             print(
#                 f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
#             )

# transcribe_gcs_with_word_time_offsets(audio)