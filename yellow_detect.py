#!/usr/bin/env python3

import rospy # Python library for ROS
from sensor_msgs.msg import Image # Image is the message type
from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images
import cv2 # OpenCV library
import numpy as np

def callback(data):
 
    # Used to convert between ROS and OpenCV images
    br = CvBridge()
 
    # Output debugging information to the terminal
    rospy.loginfo("receiving video frame")
    #rospy.loginfo(data.header)
    # Convert ROS Image message to OpenCV image
    current_frame = br.imgmsg_to_cv2(data)
    hsv = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)
    
    lower_yel = np.array([94,130,0])
    upper_yel = np.array([97,158,255])
    mask = cv2.inRange(hsv, lower_yel, upper_yel)
    result = cv2.bitwise_and(current_frame, current_frame, mask=mask)
    gray_scale = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    _,thresh = cv2.threshold(gray_scale, 50 , 255, cv2.THRESH_BINARY)

    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    i = 0
    pos=[]
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            M = cv2.moments(contours[i])
            pos.insert(0, round(M['m10'] / M['m00']))
            pos.insert(1, round(M['m01'] / M['m00']))
        i = i + 1
    print(pos)
    # Display image
    cv2.imshow("camera", gray_scale)
    print(gray_scale.shape)
    # cv2.imshow("camera1", current_frame)
    # cv2.imshow("camera2", mask)
   
    cv2.waitKey(1)
      
def receive_message():
 
    # Tells rospy the name of the node.
    # Anonymous = True makes sure the node has a unique name. Random
    # numbers are added to the end of the name. 
    rospy.init_node('video_sub_py', anonymous=True)
    
    # Node is subscribing to the video_frames topic
    rospy.Subscriber("/edrone/camera_rgb/image_raw", Image, callback)
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
 
    # Close down the video stream when done
    cv2.destroyAllWindows()
  
if __name__ == '__main__':
  receive_message()
