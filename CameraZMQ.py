###############################################################################
# Camera Cast
#
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
#  git clone https://github.com/jeffbass/imagezmq.git
#  -This shows where the site packages are installed
#  python3 -m site --user-site 
# Using fileexplorer:
#  copy imagezmq/imagezmq to site package directory/imagezmq
###############################################################################

import imutils
import cv2
import imagezmq
import socket
import time

jpegQuality = 95        # compression quality
imageDifference = 10000 # threshold sum of absolute difference between images
fpsMax = 15             # maximum number of frames sent per second
resolution = 1080       # vertical resolution

lastTime        = cv2.getTickCount()
tickDeltaFrame  = cv2.getTickFrequency()/fpsMax # ticks between frames
tickDeltaReport = cv2.getTickFrequency()*5      # ticks for 5 secs
numFrames = 0

# initialize the ImageSender object with the socket address of the server
sender_0 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.10"))
#sender_1 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.11"))
#sender_2 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.12"))
#sender_3 = imagezmq.ImageSender(connect_to="tcp://{}:5555".format("192.168.8.13"))

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
hostName = socket.gethostname() + "_Camera"
vs = imutils.VideoStream(src=0).start()
time.sleep(2.0)

while True:
    currentTime = cv2.getTickCount()
    if (currentTime - lastTime) >= tickDeltaFrame:
        # read the frame from the camera and send it to the server
        frame = vs.read()
        # save bandwidth 
        frameSmall = imutils.resize(frame, height=resolution)
        # compress data
        retCode, jpgBuffer = cv2.imencode(".jpg", frameSmall, [int(cv2.IMWRITE_JPEG_QUALITY), jpegQuality])
        sender_0.send_jpg(hostName, jpgBuffer) 
        # sender_1.send_jpg(hostName, jpgBuffer) 
        # sender_2.send_jpg(hostName, jpgBuffer) 
        # sender_3.send_jpg(hostName, jpgBuffer)
        numFrames += 1

    if (currentTime - lastTime) >= tickDeltaReport:
        # report frame rate
        print("FPS: {}".format(numFrames/5.0))
        numFrames = 0

    time.sleep(1.0/(2.0*fpsMax))
