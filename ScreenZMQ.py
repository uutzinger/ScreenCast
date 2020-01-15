###############################################################################
# Screen Cast
# This program captures desktop screen and sends it to multiple receivers for display
# It is based on examples found here:
# Screen Capture https://www.pyimagesearch.com/2018/01/01/taking-screenshots-with-opencv-and-python/
# ImageZMQ: https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/
#
# This code is freeware: no supprt, no warranty, no liability
# Urs Utiznger
# 2020
###############################################################################
# Installation instructions:
# 
# In CMD shell:
#  pip3 install opencv-contrib-python
#  pip3 install imutils
#  pip3 install numpy
#  pip3 install pillow
#  pip3 install mss
#  pip3 install pyzmq
#  git clone https://github.com/jeffbass/imagezmq.git
#  -This shows where the site packages are installed
#  python3 -m site --user-site 
# Using fileexplorer:
#  copy imagezmq/imagezmq.py to where you keep this code
###############################################################################

import imutils
import numpy as np
import cv2
import imagezmq
import socket
import time
# from mss.windows import MSS as mss
from PIL import ImageGrab

jpegQuality = 95
imageDifference = 50000
fpsMax = 15
resolution = 1080
monitor = 0
FPS = True

# sct =  mss()

# initialize the ImageSender object with the socket address of the server
sender_0 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.10"))
sender_1 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.11"))
sender_2 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.12"))
sender_3 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.13"))

# Start screen grab process

# get the host na=me,
hostName = socket.gethostname()

# initialize
numFrames = 0
lastFPSTime     = cv2.getTickCount()
tickFrequency   = cv2.getTickFrequency()
tickDeltaReport = tickFrequency*5      # ticks for 5 secs
tickDeltaFrame  = tickFrequency/fpsMax # ticks between frames


framePrevious   = np.array(ImageGrab.grab(), dtype=np.uint8)
lastTime        = cv2.getTickCount()
currentTime     = lastTime

while True:
    # take a screenshot of the screen
    currentTime = cv2.getTickCount()
    if (currentTime - lastTime) >= tickDeltaFrame:
        lastTime = currentTime
        # frame=sct.grab(sct.monitors[monitor])
        screen = ImageGrab.grab() #200ms 
        frame = np.array(screen, dtype=np.uint8) # 70ms
        frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # 7ms
        # is there enough change on the screen to warrant sending new image?
        frameDelta = cv2.absdiff(frame, framePrevious) # 25ms
        # e1 = cv2.getTickCount()
        change = sum(cv2.sumElems(frameDelta)) # 25ms
        # print((cv2.getTickCount()-e1)/tickFrequency)        
        if change > imageDifference:
            # we want to send new screen capture
            framePrevious = frame
            # save bandwidth 
            frameSmall = imutils.resize(frame, height=resolution) # 6ms
            # print((cv2.getTickCount()-e1)/tickFrequency)
            # compress data
            _, jpgBuffer = cv2.imencode(".jpg", frameSmall, 
                                        [int(cv2.IMWRITE_JPEG_QUALITY), jpegQuality]) #5ms
            sender_0.send_jpg(hostName, jpgBuffer) 
            sender_1.send_jpg(hostName, jpgBuffer)
            sender_2.send_jpg(hostName, jpgBuffer)
            sender_3.send_jpg(hostName, jpgBuffer)
    numFrames += 1
    currentTime = cv2.getTickCount()

    if ((currentTime - lastFPSTime) >= tickDeltaReport) and FPS:
        lastFPSTime = currentTime
        # report frame rate
        print("FPS: {}".format(numFrames/5.0))
        numFrames = 0
        
    time.sleep(1.0/(2.0*fpsMax))
