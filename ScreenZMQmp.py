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
import argparse
import socket
import time
import PIL
import mss
import mss.tools
from multiprocessing import Process, Queue

jpegQuality = 95
imageDifference = 50000
fpsMax = 15
resolution = 1080
monitor = 0

def grab(queue, monitor):
    # type: (Queue) -> None
    tickFrequency   = cv2.getTickFrequency()
    tickDeltaFrame  = tickFrequency/fpsMax # ticks between frames
    lastTime        = cv2.getTickCount()
    currentTime     = lastTime
    with mss.mss() as sct:
        while True:
            currentTime = cv2.getTickCount()
            if (currentTime - lastTime) >= tickDeltaFrame:
                lastTime = currentTime
                #e1 = cv2.getTickCount()
                queue.put(sct.grab(sct.monitors[monitor]))
                #e2 = cv2.getTickCount()
                #print((e2-e1)/tickFrequency)

if __name__ == "__main__":

    # initialize the ImageSender object with the socket address of the server
    #sender_0 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.10"))
    #sender_1 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.11"))
    #sender_2 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.12"))
    #sender_3 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.13"))

    # Start screen grab process
    queue = Queue()  # type: Queue
    Process(target=grab, args=(queue, monitor)).start()

    # get the host na=me,
    hostName = socket.gethostname()

    # initialize
    numFrames = 0
    lastFPSTime     = cv2.getTickCount()
    tickFrequency   = cv2.getTickFrequency()
    tickDeltaReport = tickFrequency*5      # ticks for 5 secs
    framePrevious   = np.array(queue.get())

    while True:
        # take a screenshot of the screen
        frame = np.array(queue.get())
        #while not queue.empty():
        #    queue.get()
        # frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # 7ms
        # is there enough change on the screen to warrant sending new image?
        frameDelta = cv2.absdiff(frame, framePrevious) # 25ms
        change = np.sum(frameDelta,dtype=np.int32) # 25ms
        if change > imageDifference:
            # we want to send new screen capture
            framePrevious = frame
            # save bandwidth 
            frameSmall = imutils.resize(frame, height=resolution)
            # compress data
            retCode, jpgBuffer = cv2.imencode(".jpg", frameSmall, [int(cv2.IMWRITE_JPEG_QUALITY), jpegQuality]) #5ms
            #sender_0.send_jpg(hostName, jpgBuffer) 
            #sender_1.send_jpg(hostName, jpg_buffer)
            #sender_2.send_jpg(hostName, jpg_buffer)
            #sender_3.send_jpg(hostName, jpg_buffer)
        numFrames += 1
        currentTime = cv2.getTickCount()
        if (currentTime - lastFPSTime) >= tickDeltaReport:
            lastFPSTime = currentTime
            # report frame rate
            print("FPS: {}".format(numFrames/5.0))
            numFrames = 0
        time.sleep(1.0/(2.0*fpsMax))
