#!/usr/bin/env python

import rospy
import numpy as np
import tf.transformations as tf_trans
from geometry_msgs.msg import Quaternion
from std_msgs.msg import Int16MultiArray, Int16, Float32  
from sensor_msgs.msg import Imu

class HeadControl:

    def __init__(self):
        rospy.init_node("head_control")

        # Subscribers
        self.balltracking_angles_sub = rospy.Subscriber("/gimball", Int16MultiArray, self.balltracking_callback)
        self.imu_angles_sub = rospy.Subscriber("/micro/IMU", Imu, self.imu_callback)

        # Publishers
        self.error_pub = rospy.Publisher("/head/error", Quaternion, queue_size=1)
        #self.pitch_servo_pub = rospy.Publisher("/Neckpitch", Float32, queue_size=1) 
        #self.yaw_servo_pub = rospy.Publisher("/Neckyaw", Float32, queue_size=1) 
        self.gimble_pub = rospy.Publisher("/ball_tracking", Int16MultiArray, queue_size=1) 

        self.balltracking_quaternion = None
        self.imu_quaternion = None

    def euler_to_quaternion(self, roll, pitch, yaw): 
        return tf_trans.quaternion_from_euler(roll, pitch, yaw)

    def balltracking_callback(self, msg):
        #rospy.loginfo("to entrando no balltracking callback")
        roll = 0
        pitch, yaw = msg.data
        self.balltracking_quaternion = self.euler_to_quaternion(roll, pitch, yaw)
        
        self.calculate_error()

    def imu_callback(self, msg):
        #rospy.loginfo("to entrando no imu callback")
        #roll, pitch, yaw = msg.data
        #self.imu_quaternion = self.euler_to_quaternion(roll, pitch, yaw)
        orientation = msg.orientation
        roll, pitch, yaw = tf_trans.euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])
        self.imu_quaternion = self.euler_to_quaternion(roll, pitch, yaw)
        self.calculate_error()

    def calculate_error(self):
        if self.balltracking_quaternion is not None and self.imu_quaternion is not None:
            #rospy.loginfo("to entrando no carai do if do quarteirão")
            error = Int16MultiArray()
            
            error.data = [
                self.balltracking_quaternion[0] - self.imu_quaternion[0],
                self.balltracking_quaternion[1] - self.imu_quaternion[1],
                self.balltracking_quaternion[2] - self.imu_quaternion[2],
                self.balltracking_quaternion[3] - self.imu_quaternion[3]
            ]
            error_msg = Quaternion(*error.data)
            self.error_pub.publish(error_msg)

            error_data_int = [int(value) for value in error.data[:2]]
            error_two = Int16MultiArray(data=error_data_int[:2])
            error_two = tf_trans.euler_from_quaternion(error_two)
            rospy.loginfo(error_data_int)
            #rospy.loginfo(error[1]) 
            #rospy.loginfo(error[2])
            
            #self.pitch_servo_pub.publish(error[1])
            #self.yaw_servo_pub.publish(error[2])
            self.gimble_pub.publish(error_two)

if __name__ == "__main__":
    hc = HeadControl()
    rospy.spin()

