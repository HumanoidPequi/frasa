#!/usr/bin/env python3
#todo script é um nó diferente
#esse nó pega as coordenadas da bola que foram publicadas pelo nó "ball_tracking" e publica os angulos para o servo
import rospy
from std_msgs.msg import Float32MultiArray, Int16MultiArray, Float32

import yaml
import numpy as np
import math as mt


#pub_angles = rospy.Publisher('/ball_tracking', Int16MultiArray,queue_size=1) ball tracing original
pub_angles = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray,queue_size=1)
angles = Int16MultiArray()
import time

with open('/home/marta/Documentos/ball_tracking/ball_tracking/params2.yaml') as f:
    cam_params = yaml.load(f, Loader=yaml.FullLoader)
    intrinsic = np.array(cam_params['mtx'])

fx = intrinsic[0,0]
fy = intrinsic[1,1]

cx = 320
cy = 240

theta_z = 0   #< >
theta_y = -50 #cima e baixo ^v

h_cam = 57 #cm originalmente 68
ball_distance = Float32()

pub_distance = rospy.Publisher("ball_distance", Float32, queue_size = 1)
#time.sleep(5)

def angles_callback(msg):#toda vez wue eu receber a posicao da bola eu vou executar o callback
    #esse calback calcula os 2 angulos da cabeça e publica
    global theta_y, theta_z
    angles.data = [theta_z * 10,theta_y * 10,0,0,0]
    if msg.data[0] !=1000 and msg.data[1] !=1000:
        
        v = msg.data[0]
        u = msg.data[1]
                                                
        if abs(v - cx) > 25 or abs(u - cy >20):
            rospy.loginfo("entrei no segundo if")
            x = -(v-cx)
            y = -(u-cy)
            #if (x >=15) and (y>=15):
            theta_z = theta_z + int(np.arctan2(x,fx)*180/mt.pi) 
            theta_y = theta_y + int(np.arctan2(y,fy)*180/mt.pi) 
            if(theta_y < -70):
                theta_y = -70
            if theta_y > -20:
                theta_y = -20
            if theta_z < -50:
                theta_z = -50 
            if theta_z > 50:
                theta_z = 50

            angles.data = [theta_z * 10,theta_y * 10,0,0,0]
        
    else:
        rospy.loginfo("não to entrando em porra nenhuma")
        theta_z = 0
        theta_y = -50
        angles.data = [theta_z * 10,theta_y * 10,0,0,0]
        
    rospy.loginfo('the angles are %i, %i', theta_y,theta_z)
    pub_angles.publish(angles)
    alpha = 90 - angles.data[1]/10
    #print(mt.tan(alpha))
    alpha_rad = mt.radians(alpha)
    #print(abacate)
    #rospy.loginfo("este é alpha %s", alpha)
    ball_distance.data = h_cam / mt.tan(alpha_rad) 
    #print(mt.tan(abacate))
    rospy.loginfo("este é ball_distance.data %s", ball_distance.data)
    pub_distance.publish(ball_distance)

    #time.sleep(0.8)

# def distance_callback(data):
#         #print(data)
#         #quat = [data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w]
#         #(roll, pitch, yaw) = euler_from_quaternion(quat)
#         alpha = mt.pi/2 - angles.data[1]
#         ball_distance.data = mt.tan(alpha) * h_cam
#         pub_distance.publish(ball_distance)

def angles_sub():
    rospy.Subscriber('/ball_pose', Float32MultiArray, angles_callback)
    rospy.spin()

if __name__=='__main__':
    rospy.init_node('head_control_node')
    rospy.loginfo('angles_pub node started')
    pub_angles.publish(angles)
    angles_sub()
