# Author: Sara Fridovich-Keil (partners: Ben Cohen and Zach Stecker) 
# final project for COS 426: Computer Graphics
# execution in Terminal: python FastFingerFrame.py fingervideo.mov
# see readme for tips on good input videos

import cv2
import math
import numpy as np
import sys

sigma = 10 # how many pixels up and down to look
colorlines = [] # array of arrays, where each element is a frame and each subarray has red values across width
frames_elapsed = 0
threshold = 250 # this can change--just starting default value
transitions = [] # array where each entry is the transition x value for that frame
avg = 0
amplifyratio = 5
amplifiedTransitions = [] # transitions with amplified difference between transition and average
fourier = []
coefficients = []

# take rfft of amplified transitions to find pulse
def fourier():
	global coefficients
	global fourier
	global amplifiedTransitions

	fourier = np.fft.rfft(amplifiedTransitions)
	for coeff in np.nditer(fourier):
		coefficients.append(np.absolute(coeff))


# amplify difference between transitions and average
def amplifyTransitions():
	global avg
	global transitions
	global amplifiedTransitions
	global amplifyratio

	for transition in transitions:
		difference = transition - avg
		amplifiedDiff = difference * amplifyratio
		amplifiedTransitions.append(amplifiedDiff)

# get average transition point across all frames
def getAverageTransition():
	global transitions
	global frames_elapsed
	global avg

	for transition in transitions:
		avg += transition
	avg /= frames_elapsed	

# choose threshold appropriately
def chooseThreshold():
	global colorlines
	global threshold
	# global frames_elapsed

	mincol = 255
	for colorline in colorlines:
		curcol = colorline[0]
		if curcol < mincol:
			mincol = curcol

	threshold = mincol - 10		

# find transition point across the width in each frame, fill transitions array
def getTransitions():
	global transitions
	global colorlines
	global threshold

	for colorline in colorlines:
		transition = 0
		for x in range(0, len(colorline)):
			val = colorline[x]
			if val < threshold:
				transition = x
				break
		transitions.append(transition)		

# average across a swath of pixels horizontally
def getColorlines(frame):
	global sigma
	global colorlines

	height = frame.shape[0]
	width = frame.shape[1]

	ycenter = int(round(height/2))

	colorline = []
	for i in range(0, width):
		reds = [] # choose median of vertical strip
		for j in range(ycenter - sigma, ycenter + sigma):
			curcolor = frame[j, i]
			reds.append(curcolor[2])
		reds.sort()
		colorline.append(reds[int(round(len(reds)/2))])	

	colorlines.append(colorline)		

# Read in video and parse it into frames
videoname = sys.argv[1]
video = cv2.VideoCapture(videoname)
pos_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

frame_rate = int(math.ceil(video.get(cv2.cv.CV_CAP_PROP_FPS)))

while True:
	flag, frame = video.read()

	if flag:
		frames_elapsed += 1
		pos_frame = video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)
		getColorlines(frame)
	else:
		# frame not ready; try again	
		video.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)
		print "frame is not ready"
		cv2.waitKey(1000)

	if cv2.waitKey(10) == 27:
		break

	if video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)	== video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
		break

# print "done reading in video and finding colorlines"

# for frame in frames:
# 	getColorlines(frame)

# print "done finding colorlines"

# for item in colorlines[4]:
# 	print item

chooseThreshold()	

getTransitions()

# print "done getting transitions"

# for item in transitions:
# 	print item

getAverageTransition()

# print "done getting average transition"

amplifyTransitions()

# for item in amplifiedTransitions:
# 	print item

# print "done amplifying transitions"

duration = int(frames_elapsed/frame_rate)

# Fourier band-pass filtering limits
min_rate = 50
max_rate = 160
min_freq = int(math.floor(min_rate * duration / 60))
max_freq = int(math.ceil(max_rate * duration / 60))

fourier()

print "done with Fourier"

# for item in coefficients:
# 	print item

# print "threshold:", threshold	

# bandpass filter
biggest = -float("inf")
best = -1

end = min(max_freq+1, len(coefficients))
for i in range(min_freq, end):	
	magnitude = coefficients[i]
	if magnitude > biggest:
		biggest = magnitude
		best = i

pulse = 60 * best / duration 

print "pulse:", pulse


