# import cv2
# import numpy as np

# def empty(a):
#     pass

# def initializeTrackbars(intialTracbarVals=0):
#     cv2.namedWindow("Trackbars")
#     cv2.resizeWindow("Trackbars", 640, 240)
#     cv2.createTrackbar("Threshold1", "Trackbars", 0, 255, empty)
#     cv2.createTrackbar("Threshold2", "Trackbars", 255, 255, empty)

# def valTrackbars():
#     Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
#     Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
#     src = Threshold1, Threshold2
#     return src

import cv2
import numpy as np

frame = cv2.imread("/home/im-robot/Pictures/test1.png")

     

cv2.namedWindow("Hsv Capture")
def nothing(a):
    pass
# create trackbars for color change
# IMPORTANT: You have to define the correct HSV opencv range hence 179,255,255
cv2.createTrackbar('H', 'Hsv Capture', 94, 179, nothing)
cv2.createTrackbar('S', 'Hsv Capture', 130, 255, nothing)
cv2.createTrackbar('V', 'Hsv Capture', 0, 255, nothing)

cv2.createTrackbar('H1', 'Hsv Capture', 97, 179, nothing)
cv2.createTrackbar('S1', 'Hsv Capture', 158, 255, nothing)
cv2.createTrackbar('V1', 'Hsv Capture', 255, 255, nothing)

while(True):

    

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Trackbars realtime position
    h1 = cv2.getTrackbarPos('H', 'Hsv Capture')
    s1 = cv2.getTrackbarPos('S', 'Hsv Capture')
    v1 = cv2.getTrackbarPos('V', 'Hsv Capture')

    h2 = cv2.getTrackbarPos('H1', 'Hsv Capture')
    s2 = cv2.getTrackbarPos('S1', 'Hsv Capture')
    v2 = cv2.getTrackbarPos('V1', 'Hsv Capture')

    #How to store the min and max values from the trackbars
    blue_MIN = np.array([h1, s1, v1])
    blue_MAX = np.array([h2, s2, v2])

    #After finding your values, you can replace them like this
    #blue_MIN = np.array([102, 73, 145], np.uint8)
    #blue_MAX = np.array([123, 182, 242], np.uint8)
            
    #Using inRange to find the desired range
    hsvCapture = cv2.inRange(hsv,  blue_MIN, blue_MAX)

    # cv2.imshow('camera', hsv)
    # cv2.imshow('camera1', frame)
    cv2.imshow('camera2',hsvCapture)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()