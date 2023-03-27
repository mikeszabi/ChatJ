#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 13:36:53 2023

@author: szabi
"""

import vlc
 
media = vlc.MediaPlayer("trimmed_video.mp4")
 
media.play()