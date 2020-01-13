###############################################################################
# Screen Cast
#
# Screen Capture https://www.pyimagesearch.com/2018/01/01/taking-screenshots-with-opencv-and-python/
# ImageZMQ: https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/
#
# Urs Utiznger
# 2020
###############################################################################
# Installation instructions:
# 
# In CMD shell:
#  pip3 install opencv-contrib-python
#  pip3 install imutils
#  pip3 install numpy
#  pip3 install pymsgbox
#  pip3 install PyTweening
#  pip3 install pyscreeze
#  pip3 install pygetwindow
#  pip3 install mouseinfo
#  pip3 install pillow
#  pip3 install pyautogui
#  pip3 install pyzmq
#  git clone https://github.com/jeffbass/imagezmq.git
#  -This shows where the site packages are installed
#  python3 -m site --user-site 
# Using fileexplorer:
#  copy imagezmq/imagezmq.py to where you keep this code
###############################################################################

import imutils
import numpy as np
import pyautogui
import cv2
import imagezmq
import argparse
import socket
import time

jpegQuality = 95
imageDifference = 10000
fpsMax = 15
resolution = 1080

# initialize the ImageSender object with the socket address of the server
sender_0 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.10"))
#sender_1 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.11"))
#sender_2 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.12"))
#sender_3 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.13"))

# get the host name,
hostName = socket.gethostname()
framePrevious = pyautogui.screenshot()

lastTime        = cv2.getTickCount()
tickDeltaFrame  = cv2.getTickFrequency()/fpsMax # ticks between frames
tickDeltaReport = cv2.getTickFrequency()*5      # ticks for 5 secs
numFrames = 0

while True:
    currentTime = cv2.getTickCount()
    if (currentTime - lastTime) >= tickDeltaFrame:
        lastTime = currentTime
        # take a screenshot of the screen and store it in memory
        frame = pyautogui.screenshot()
        # is there enough change on the screen to warrant sending new image?
        frameDelta = cv2.absdiff(frame, framePrevious)
        change = np.sum(frameDelta,dtype=np.int32)
        if change > imageDifference:
            # we want to send new screen capture
            framePrevious = frame
            # convert the PIL/Pillow image to an OpenCV compatible NumPy array
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            # save bandwidth 
            frameSmall = imutils.resize(frame, height=resolution)
            # compress data
            retCode, jpgBuffer = cv2.imencode(".jpg", frameSmall, [int(cv2.IMWRITE_JPEG_QUALITY), jpegQuality])
            sender_0.send_jpg(hostName, jpgBuffer) 
            # sender_1.send_jpg(hostName, jpg_buffer)
            # sender_2.send_jpg(hostName, jpg_buffer)
            # sender_3.send_jpg(hostName, jpg_buffer)
            numFrames += 1
    if (currentTime - lastTime) >= tickDeltaReport:
        # report frame rate
        print("FPS: {}".format(numFrames/5.0))
        numFrames = 0
    time.sleep(1.0/(2.0*fpsMax))
