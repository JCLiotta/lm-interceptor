# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from io import BytesIO
import RPi.GPIO as GPIO ## Import GPIO library
import smbus
import time

# Setup bus for I2C
bus = smbus.SMBus(1)

# This is the address we setup in the Arduino Program
address = 0x04

def writeNumber(value):
	try:
		bus.write_byte(address, value)
	except:
		#print("Caught Exception")
		go = 1
	return -1

LEFT_WHEEL = 1
RIGHT_WHEEL = 2
BOTH_WHEELS = 3
STOP_WHEELS = 4

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

pts = deque(maxlen=20)

# Declare and initialize x,y
(x, y) = (0, 0)
radius = 0
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

# keep looping
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image
	image = frame.array 
	
	# blur the frame and convert it to the HSV
	# color space
	blurred = cv2.GaussianBlur(image, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	
 
	# construct a mask for the color, then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(image, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(image, center, 5, (0, 0, 255), -1)
			
			if x <= 212:
				writeNumber(LEFT_WHEEL)
			elif x >= 424:
				writeNumber(RIGHT_WHEEL)
			elif x > 212 and x < 424:
				writeNumber(BOTH_WHEELS)

		else:
			writeNumber(STOP_WHEELS)
			
	else:
		writeNumber(STOP_WHEELS)
			
	# update the points queue
	pts.appendleft(center)
	
	# loop over the set of tracked points
	for i in xrange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
 
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(8 / float(i + 1)) * 2.5)
		cv2.line(image, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# Draw lines
	cv2.line(image, (212,0), (212,480), (255,255,255), 1)
	cv2.line(image, (424,0), (424,480), (255,255,255), 1)
	
	# Display x,y coordinates
	cv2.putText(image, "x: {}, y: {}".format(x, y),
	(5, 470), cv2.FONT_HERSHEY_SIMPLEX,
	0.35, (0, 0, 255), 1)
	
	cv2.putText(image, "radius: {}".format(radius),
	(325, 470), cv2.FONT_HERSHEY_SIMPLEX,
	0.35, (0, 0, 255), 1)
	
	# show the frame to our screen
	cv2.imshow("Frame", image)
	
	# Display the mask
	cv2.imshow("Mask", mask)
	
	# Display the blur
	#cv2.imshow("Blur", blurred)
	
	# Display the hsv
	cv2.imshow("HSV", hsv)
	
	# NOTE: Comment out to end dispying of mask and camera
	key = cv2.waitKey(1) & 0xFF
	
    # clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	# NOTE: Comment out to end dispying of mask and camera
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		writeNumber(STOP_WHEELS)
		break
	
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
