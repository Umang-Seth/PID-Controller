#!/usr/bin/env python3

'''

This python file runs a ROS-node of name drone_control which holds the position of e-Drone on the given dummy.
This node publishes and subsribes the following topics:

        PUBLICATIONS			SUBSCRIPTIONS
        /drone_command			/whycon/poses
        /alt_error				/pid_tuning_altitude
        /pitch_error			/pid_tuning_pitch
        /roll_error				/pid_tuning_roll
                    
                                

Rather than using different variables, use list. eg : self.setpoint = [1,2,3], where index corresponds to x,y,z ...rather than defining self.x_setpoint = 1, self.y_setpoint = 2
CODE MODULARITY AND TECHNIQUES MENTIONED LIKE THIS WILL HELP YOU GAINING MORE MARKS WHILE CODE EVALUATION.	
'''

# Importing the required libraries

from edrone_client.msg import *
from geometry_msgs.msg import PoseArray
from std_msgs.msg import Int16
from std_msgs.msg import Int64
from std_msgs.msg import Float64
from pid_tune.msg import PidTune
import rospy
import time
import cv2
import numpy as np
from sensor_msgs.msg import Image 
from cv_bridge import CvBridge 

class Edrone():
    """docstring for Edrone"""
    def __init__(self):
        
        rospy.init_node('drone_control')	# initializing ros node with name drone_control

        # This corresponds to your current position of drone. This value must be updated each time in your whycon callback
        # [x,y,z]
        self.drone_position = [0.0,0.0,0.0]	

        # [x_setpoint, y_setpoint, z_setpoint]
        self.setpoint = [0,0,26] # whycon marker at the position of the dummy given in the scene. Make the whycon marker associated with position_to_hold dummy renderable and make changes accordingly
        

        #Declaring a cmd of message type edrone_msgs and initializing values
        self.cmd = edrone_msgs()
        self.cmd.rcRoll = 1500
        self.cmd.rcPitch = 1500
        self.cmd.rcYaw = 1500
        self.cmd.rcThrottle = 1500
        self.cmd.rcAUX1 = 1500
        self.cmd.rcAUX2 = 1500
        self.cmd.rcAUX3 = 1500
        self.cmd.rcAUX4 = 1500


        #initial setting of Kp, Kd and ki for [roll, pitch, throttle]. eg: self.Kp[2] corresponds to Kp value in throttle axis
        #after tuning and computing corresponding PID parameters, change the parameters
        self.Kp = [0,0,0]
        self.Ki = [0,0,0]
        self.Kd = [0,0,0]


        #-----------------------Add other required variables for pid here ----------------------------------------------

        self.error = [0,0,0]
        self.prev_error = [0,0,0]
        self.sum_error = [0,0,0]


        self.min_values = 1000
        self.max_values = 2000
        self.flag=0

        self.current_frame = Image

        # Hint : Add variables for storing previous errors in each axis, like self.prev_values = [0,0,0] where corresponds to [pitch, roll, throttle]		#		 Add variables for limiting the values like self.max_values = [2000,2000,2000] corresponding to [roll, pitch, throttle]
        #													self.min_values = [1000,1000,1000] corresponding to [pitch, roll, throttle]
        #																	You can change the upper limit and lower limit accordingly. 
        #----------------------------------------------------------------------------------------------------------

        # # This is the sample time in which you need to run pid. Choose any time which you seem fit. Remember the stimulation step time is 50 ms
        # self.sample_time = 0.060 # in seconds






        # Publishing /drone_command, /alt_error, /pitch_error, /roll_error
        self.command_pub = rospy.Publisher('/drone_command', edrone_msgs, queue_size=1)
        #------------------------Add other ROS Publishers here-----------------------------------------------------
        self.alt_error_pub = rospy.Publisher('/alt_error', Float64, queue_size=1)
        self.pitch_error_pub = rospy.Publisher('/pitch_error', Float64, queue_size=1)
        self.roll_error_pub = rospy.Publisher('/roll_error', Float64, queue_size=1)





        #-----------------------------------------------------------------------------------------------------------


        # Subscribing to /whycon/poses, /pid_tuning_altitude, /pid_tuning_pitch, pid_tuning_roll
        rospy.Subscriber('/whycon/poses', PoseArray, self.whycon_callback)
        rospy.Subscriber('/pid_tuning_altitude',PidTune,self.altitude_set_pid)
        #-------------------------Add other ROS Subscribers here----------------------------------------------------
        rospy.Subscriber('/pid_tuning_pitch',PidTune,self.pitch_set_pid)
        rospy.Subscriber('/pid_tuning_roll',PidTune,self.roll_set_pid)
        rospy.Subscriber("/edrone/camera_rgb/image_raw", Image, self.callback)



        self.flag=0
        #------------------------------------------------------------------------------------------------------------
        print("Run arm")
        self.arm() # ARMING THE DRONE
        print("Armed")

    # Disarming condition of the drone
    def disarm(self):
        self.cmd.rcThrottle = 1000
        self.cmd.rcAUX4 = 0
        self.command_pub.publish(self.cmd)
        rospy.sleep(1)


    # Arming condition of the drone : Best practise is to disarm and then arm the drone.
    def arm(self):

        self.disarm()

        self.cmd.rcRoll = 1500
        self.cmd.rcYaw = 1500
        self.cmd.rcPitch = 1500
        self.cmd.rcThrottle = 1500
        self.cmd.rcAUX1 = 0
        self.cmd.rcAUX2 = 0
        self.cmd.rcAUX3 = 0
        self.cmd.rcAUX4 = 1500
        self.command_pub.publish(self.cmd)	# Publishing /drone_command
        rospy.sleep(1)



    # Whycon callback function
    # The function gets executed each time when /whycon node publishes /whycon/poses 
    def whycon_callback(self,msg):
        self.drone_position[0] = msg.poses[0].position.x

        #--------------------Set the remaining co-ordinates of the drone from msg----------------------------------------------

        self.drone_position[1] = msg.poses[0].position.y
        self.drone_position[2] = msg.poses[0].position.z


        
        #---------------------------------------------------------------------------------------------------------------

    def callback(self,data):
        self.br = CvBridge()
        #rospy.loginfo("receiving video frame")
        self.current_frame = self.br.imgmsg_to_cv2(data)
        # self.cv_image = cv2.transpose(self.img)
        # self.current_frame = cv2.flip(self.cv_image,1)
    # Callback function for /pid_tuning_altitude
    # This function gets executed each time when /tune_pid publishes /pid_tuning_altitude
    def altitude_set_pid(self,alt):
        self.Kp[2] = alt.Kp * 0.06 # This is just for an example. You can change the ratio/fraction value accordingly
        self.Ki[2] = alt.Ki * 0.008
        self.Kd[2] = alt.Kd * 0.3

    #----------------------------Define callback function like altitide_set_pid to tune pitch, roll--------------

    def pitch_set_pid(self,pitch):
        self.Kp[1] = pitch.Kp * 0.06
        self.Ki[1] = pitch.Ki * 0.008
        self.Kd[1] = pitch.Kd * 0.3

    def roll_set_pid(self,roll):
        self.Kp[0] = roll.Kp * 0.06
        self.Ki[0] = roll.Ki * 0.008
        self.Kd[0] = roll.Kd * 0.3

    def waypoints(self,flag):
        # switcher = {
        # 0: [0,0,20],
        # 1: [-10,-10,20],
        # 2: [-10,10,20],
        # 3: [-5,10,20],
        # 4: [-5,-10,20],
        # 5: [0,-10,20],
        # 6: [0,10,20],
        # 7: [5,10,20],
        # 8: [5,-10,20],
        # 9: [10,-10,20],
        # 10: [10,10,20],
        # }
        switcher = {
        0: [0,0,20],
        1: [-10,-10,20],
        2: [-10,-5,20],
        3: [-10,0,20],
        4: [-10,5,20],
        5: [-10,10,20],
        6: [-5,10,20],
        7: [-5,5,20],
        8: [-5,0,20],
        9: [-5,-5,20],
        10: [-5,-10,20],
        11: [0,-10,20],
        12: [0,-5,20],
        13: [0,0,20],
        14: [0,5,20],
        15: [0,10,20],
        16: [5,10,20],
        17: [5,5,20],
        18: [5,0,20],
        19: [5,-5,20],
        20: [5,-10,20],
        21: [10,-10,20],
        22: [10,-5,20],
        23: [10,0,20],
        24: [10,5,20],
        25: [10,10,20],
        }
        return switcher.get(flag, [0,0,20])
        
    def yellow_detect(self,img):
        

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_yel = np.array([94,130,0])
        upper_yel = np.array([97,158,255])

        mask = cv2.inRange(hsv, lower_yel, upper_yel)
        result = cv2.bitwise_and(img, img, mask=mask)

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
        return pos


        
    #----------------------------------------------------------------------------------------------------------------------


    def pid(self):
    #-----------------------------Write the PID algorithm here--------------------------------------------------------------

    # Steps:
    # 	1. Compute error in each axis. eg: error[0] = self.drone_position[0] - self.setpoint[0] ,where error[0] corresponds to error in x...
    #	2. Compute the error (for proportional), change in error (for derivative) and sum of errors (for integral) in each axis. Refer "Understanding PID.pdf" to understand PID equation.
    #	3. Calculate the pid output required for each axis. For eg: calcuate self.out_roll, self.out_pitch, etc.
    #	4. Reduce or add this computed output value on the avg value ie 1500. For eg: self.cmd.rcRoll = 1500 + self.out_roll. LOOK OUT FOR SIGN (+ or -). EXPERIMENT AND FIND THE CORRECT SIGN
    #	5. Don't run the pid continously. Run the pid only at the a sample time. self.sampletime defined above is for this purpose. THIS IS VERY IMPORTANT.
    #	6. Limit the output value and the final command value between the maximum(2000) and minimum(1000)range before publishing. For eg : if self.cmd.rcPitch > self.max_values[1]:
    #																														self.cmd.rcPitch = self.max_values[1]
    #	7. Update previous errors.eg: self.prev_error[1] = error[1] where index 1 corresponds to that of pitch (eg)
    #	8. Add error_sum
        
        e_drone.main()
        
        

        # self.cmd.rcThrottle = int(1500 + self.error[2] * self.Kp[2] + (self.error[2] - self.prev_error[2]) * self.Kd[2] + self.sum_error[2] * self.Ki[2])
        # self.cmd.rcPitch = int(1500 + -(self.error[1] * self.Kp[1] + (self.error[1] - self.prev_error[1]) * self.Kd[1] + self.sum_error[1] * self.Ki[1]))
        # self.cmd.rcRoll = int(1500 + self.error[0] * self.Kp[0] + (self.error[0] - self.prev_error[0]) * self.Kd[0] + self.sum_error[0] * self.Ki[0])

        self.cmd.rcPitch = int(1500 + -(self.error[1] * 12 + (self.error[1] - self.prev_error[1]) * 360 + self.sum_error[1] * 0))
        self.cmd.rcRoll = int(1500 + self.error[0] * 12 + (self.error[0] - self.prev_error[0]) * 360 + self.sum_error[0] * 0)
        self.cmd.rcThrottle = int(1500 + self.error[2] * 24 + (self.error[2] - self.prev_error[2]) * 360 + self.sum_error[2] * 0)
    
        if self.cmd.rcThrottle > self.max_values:
            self.cmd.rcThrottle = self.max_values
        if self.cmd.rcThrottle < self.min_values:
            self.cmd.rcThrottle = self.min_values

        if self.cmd.rcPitch > self.max_values:
            self.cmd.rcPitch = self.max_values
        if self.cmd.rcPitch < self.min_values:
            self.cmd.rcPitch = self.min_values

        if self.cmd.rcRoll > self.max_values:
            self.cmd.rcRoll = self.max_values
        if self.cmd.rcRoll < self.min_values:
            self.cmd.rcRoll = self.min_values



        self.prev_error[2] = self.error[2]
        self.prev_error[1] = self.error[1]
        self.prev_error[0] = self.error[0]
        
        # self.sum_error[2] = self.sum_error[2] + self.error[2]
        # self.sum_error[1] = self.sum_error[1] + self.error[1]
        # self.sum_error[0] = self.sum_error[0] + self.error[0]

        if self.sum_error[2]<8:
            self.sum_error[2] = self.sum_error[2] + self.error[2]
        else:
            self.sum_error[2]=8
        
        if self.sum_error[1]>3:
            self.sum_error[1] = self.sum_error[1] + self.error[1]
        else:
            self.sum_error[1]=3

        if self.sum_error[0]>3:
            self.sum_error[0] = self.sum_error[0] + self.error[0]
        else:
            self.sum_error[0]=3
        
        
        # anti-windup to limit the sum error

    #------------------------------------------------------------------------------------------------------------------------
        # if -0.15<self.error[0]<0.15 and -0.15<self.error[1]<0.15 and -0.18<self.error[2]<0.18:
        #         print("Checking")
        #         print(self.yellow_pos)
        #         self.flag+=1
        
            #self.setpoint = e_drone.waypoints(self.flag)
            
            # print("Waypoint",flag,self.setpoint)

        
        self.command_pub.publish(self.cmd)
        self.alt_error_pub.publish(self.error[2])
        self.pitch_error_pub.publish(self.error[1])
        self.roll_error_pub.publish(self.error[0])

    def main(self):        
        self.yellow_pos = e_drone.yellow_detect(self.current_frame)
        #print(self.yellow_pos)
        if not self.yellow_pos:
            self.setpoint = e_drone.waypoints(self.flag)
            print("Waypoint scan",self.flag,self.setpoint)
            self.error[2] = - (self.setpoint[2] - self.drone_position[2])
            self.error[0] = self.setpoint[0] - self.drone_position[0]
            self.error[1] = self.setpoint[1] - self.drone_position[1]
            if -0.15<self.error[0]<0.15 and -0.15<self.error[1]<0.15 and -0.18<self.error[2]<0.18:
                print("Checking")
                self.flag+=1
        else:
            
            self.error[2] = - (self.setpoint[2] - self.drone_position[2])
            self.error[0] = self.setpoint[0] - self.drone_position[0]
            self.error[1] = self.setpoint[1] - self.drone_position[1]
            print(self.setpoint)
            print(self.yellow_pos)
            # if self.yellow_pos[1]<260:
            #     self.setpoint[1]=self.setpoint[1]-0.01
            # elif self.yellow_pos[1]>280:
            #     self.setpoint[1]=self.setpoint[1]+0.01
            # elif self.yellow_pos[0]<350:
            #     self.setpoint[0]=self.setpoint[0]-0.01
            # elif self.yellow_pos[0]>370:
            #     self.setpoint[0]=self.setpoint[0]+0.01
            # else:
            #     self.setpoint[0]=self.setpoint[0]
            #     self.setpoint[1]=self.setpoint[1]            
            
        
        




if __name__ == '__main__':

    e_drone = Edrone()
    r = rospy.Rate(15) #specify rate in Hz based upon your desired PID sampling time, i.e. if desired sample time is 33ms specify rate as 30Hz
    while not rospy.is_shutdown():
        e_drone.pid()
        r.sleep()
