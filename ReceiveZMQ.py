###############################################################################
# Screen Cast
# This program receives images from multiple sources, tiles them and displays them.
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
#  pip3 install pyzmq
#  git clone https://github.com/jeffbass/imagezmq.git
# Using fileexplorer:
#  copy imagezmq/imagezmq.py to where you keep this code
###############################################################################

# import the necessary packages
from datetime import datetime
import numpy as np
import math 
import imagezmq
import imutils
import cv2

# initialize variables
frameDict = {}

# initialize ImageHub
imageHub = imagezmq.ImageHub()

# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()
 
# stores the estimated number of input streams, active checking period, and
# calculates the duration seconds to wait before making a check to
# see if a device was active
ESTIMATED_NUM_SENDERS = 2
ACTIVE_CHECK_PERIOD = 5
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_SENDERS * ACTIVE_CHECK_PERIOD
 
# assign montage width and height so we can view all incoming frames
# in a single "dashboard"
mW = 3840
mH = 2160

cv2.namedWindow("MEDDEV_NW", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("MEDDEV_NW",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

# start looping over all the frames
while True:
    # receive sender name and frame from the image send and acknowledge
    # the receipt
    (senderName, jpg_buffer) = imageHub.recv_jpg()
    imageHub.send_reply(b'OK')
    frame = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)

    # if a device is not in the last active dictionary then it means
    # that its a newly connected device
    if senderName not in lastActive.keys():
        print("[INFO] receiving data from {}...".format(senderName))

    # record the last active time for the device from which we just
    # received a frame
    lastActive[senderName] = datetime.now()

    # resize the frame to fit into display area
    # montage multiple frames
    numSenders   = len(lastActive)
    resizeFactor = math.ceil(math.sqrt(numSenders))
    frame        = imutils.resize(frame, width=int(mW/resizeFactor))

    # draw the sending device name on the frame
    cv2.putText(frame, senderName, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # update the new frame in the frame dictionary
    (h, w) = frame.shape[:2]  # first two dimensions
    frameDict[senderName] = frame

    # build a montage using images in the frame dictionary
    montages = imutils.build_montages(frameDict.values(), (w, h), (math.ceil(mW/w), math.ceil(mH/h)) )

    # display the montage(s) on the screen
    for (i, montage) in enumerate(montages):
        cv2.imshow("MEDDEV_NW", montage)

    # detect any kepresses
    key = cv2.waitKey(1) & 0xFF

    # if current time *minus* last time when the active device check
    # was made is greater than the threshold set then do a check
    if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
        # loop over all previously active devices
        for (senderName, ts) in list(lastActive.items()):
            # remove the sender from the last active and frame
            # dictionaries if the device hasn't been active recently
            if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
                print("[INFO] lost connection to {}".format(senderName))
                lastActive.pop(senderName)
                frameDict.pop(senderName)
        # set the last active check time as current time
        lastActiveCheck = datetime.now()

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
cv2.destroyAllWindows()
