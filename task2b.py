import cv2
import numpy as np

img = cv2.imread('yellow_detect.jpeg', -1)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower_yel = np.array([20, 150, 150])
upper_yel = np.array([30, 255, 255])

mask = cv2.inRange(hsv, lower_yel, upper_yel)
result = cv2.bitwise_and(img, img, mask=mask)

gray_scale = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
_,thresh = cv2.threshold(gray_scale, 50 , 255, cv2.THRESH_BINARY)

contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

i = 0

for cnt in contours:
    if cv2.contourArea(cnt) > 100:
        M = cv2.moments(contours[i])
        print("{}".format(round(M['m10'] / M['m00'])), "{}".format(round(M['m01'] / M['m00'])))
    i = i + 1
