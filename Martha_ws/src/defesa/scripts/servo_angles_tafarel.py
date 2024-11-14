#!/usr/bin/env python
#todo script é um nó diferente
#esse nó pega as coordenadas da bola que foram publicadas pelo nó "ball_tracking" e publica os angulos para o servo
import rospy
from std_msgs.msg import Float32MultiArray, Int16MultiArray, Float32

import yaml
import numpy as np
import math as mt

pub_angles = rospy.Publisher('/ball_tracking', Int16MultiArray,queue_size=1)
angles = Int16MultiArray()
leg = Int16MultiArray()

import time

with open('/home/marta/Documentos/ball_tracking/ball_tracking/params2.yaml') as f:
    cam_params = yaml.load(f, Loader=yaml.FullLoader)
    intrinsic = np.array(cam_params['mtx'])

fx = intrinsic[0,0]
fy = intrinsic[1,1]

bacate = 0

cx = 320
cy = 240

theta_z = 0   #< >
theta_y = -50 #cima e baixo ^v

h_cam = 62 #cm originalmente 68
ball_distance = Float32()
tafarel = Float32MultiArray()

pub_distance = rospy.Publisher("ball_distance", Float32, queue_size = 1)
#time.sleep(5)

def talker(angles):
    
    # If the motor has reached its limit, publish a new command.
    pub.publish(angles)

def speaker(velocity):
    
    vel.publish(velocity)

def arm(arm_angle):

    arm_pub.publish(arm_angle)

def optical_callback(data):
    global bacate
    bacate = data.data
    rospy.loginfo(data.data)
    #rospy.loginfo(bacate.data)
    # if (data.data[0] > 43.0):
    #     rospy.loginfo("tô do lado direito da martilda")
       
    # elif(data.data[0] < 41.0):
    #     rospy.loginfo("tô do lado esquerdo da martilda")

def angles_callback(msg):#toda vez wue eu receber a posicao da bola eu vou executar o callback
    #esse calback calcula os 2 angulos da cabeça e publica
    global theta_y, theta_z
    global bacate

    angles.data = [theta_z,theta_y]
    
    if msg.data[0] !=1000 and msg.data[1] !=1000:
        
        v = msg.data[0]
        u = msg.data[1]
                                                
        if abs(v - cx) > 25 or abs(u - cy >20):
            #rospy.loginfo("entrei no segundo if")
            x = -(v-cx)
            y = -(u-cy)
            #if (x >=15) and (y>=15):
            theta_z = theta_z + int(np.arctan2(x,fx)*180/mt.pi) 
            theta_y = theta_y + int(np.arctan2(y,fy)*180/mt.pi) 
            if(theta_y<-70):
                theta_y = -70
            if theta_y > -15:
                theta_y = -15
            if theta_z < -60:
                theta_z = -60 
            if theta_z > 60:
                theta_z = 60

            angles.data = [theta_z,theta_y]
        
    else:
        rospy.loginfo("não to entrando em porra nenhuma")
        theta_z = 0
        theta_y = -50
        angles.data = [theta_z,theta_y]
    

    #rospy.loginfo('the angles are %i, %i', theta_y,theta_z)
    pub_angles.publish(angles)
    alpha = 90 - angles.data[1]
    #print(mt.tan(alpha))
    abacate = mt.radians(alpha)
    #print(abacate)
    #rospy.loginfo("este é alpha %s", alpha)
    ball_distance.data = mt.tan(abacate) * h_cam
    pub_distance.publish(ball_distance)
    print("thetaa", theta_z)
    #if (ball_distance.data > -40 and ball_distance.data < -23) :
    #   rospy.loginfo("sem tempo irmão")
        # pub_angles.publish(angles)

        # rospy.loginfo('meus patinho estao voando')
        # rospy.sleep(1)
        # leg.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
        # arm_angle.data = [0, 700, 0, 0, 700, 0]
        #     #velocity.data = [200, 200, 300, 0]
        #     #speaker(velocity)
        # arm(arm_angle)
        # talker(leg)
        # rospy.sleep(3)
            
        #     #levantar braços
        # leg.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
        # arm_angle.data = [0, 0, 0, 0, 0, 0]
        #     #velocity.data = [200, 200, 300, 0]
        #     #speaker(velocity)
        # arm(arm_angle)
        # talker(leg)
        # rospy.sleep(2)
    if (ball_distance.data > -23):
        #global theta_y, theta_z
        rospy.loginfo("parei minha camera e to preparada")
        angles.data = [theta_z,theta_y]
        pub_angles.publish(angles)
        
            
        if (theta_z > 50):
            
             #global theta_y, theta_z
             angles.data = [theta_z,theta_y]
             pub_angles.publish(angles)
            
             rospy.loginfo("tô do lado esquerdo da martilda")
             rospy.sleep(1)
             leg.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
             arm_angle.data = [0, 1600, 0, 0, 0, 0]
             velocity.data = [0, 0, 120, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(1)
             
             leg.data = [0, 110, -400, 670, -320, 200-200, 0,50, -370, 670, -310, 200]
             arm_angle.data = [0, 1600, 0, 0, 0, 0]
             velocity.data = [0, 0, 120, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(2)
             
             leg.data = [0, 110-100, -1400, 670, -320, 200-200, 0,50, -370, 670, -310, 200]
             arm_angle.data = [0, 1600, 0, 0, 0, 0]
             velocity.data = [0, 0, 120, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(20)
             
        elif(theta_z < -35):
             rospy.loginfo("tô do lado direito da martilda")
            
             angles.data = [theta_z,theta_y]
             pub_angles.publish(angles)
            
             rospy.loginfo("tô do lado esquerdo da martilda")
             rospy.sleep(1)
             leg.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
             arm_angle.data = [0, 0, 0, 0, 1600, 0]
             velocity.data = [0, 0, 150, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(1)
             
             leg.data = [0, 50, -400, 670, -320, -200, 0,110, -370, 670, -310, 200-200]
             arm_angle.data = [0, 0, 0, 0, 1600, 0]
             velocity.data = [0, 0, 150, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(2)
             
             leg.data = [0, 110-100, -400, 670, -320, 200-200, 0,50, -1400, 670, -310, 200]
             arm_angle.data = [0, 0, 0, 0, 1600, 0]
             velocity.data = [0, 0, 150, 0]
             speaker(velocity)
             arm(arm_angle)
             talker(leg)
             pub_angles.publish(angles)
             rospy.sleep(20)
        #     rospy.sleep(1)
        #     angles.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
        #     arm_angle.data = [1700, 700, 0, 0, 700, 0]
        #     #velocity.data = [200, 200, 300, 0]
        #     #speaker(velocity)
        #     arm(arm_angle)
        #     talker(angles)
        #     rospy.sleep(3)
            
        #     #levantar braços
        #     angles.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
        #     arm_angle.data = [1700, 0, 0, 0, 0, 0]
        #     #velocity.data = [200, 200, 300, 0]
        #     #speaker(velocity)
        #     arm(arm_angle)
        #     talker(angles)
        #     rospy.sleep(2)
        #       #levantar braços
        #     angles.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
        #     arm_angle.data = [0, 0, 0, 0, 0, 0]
        #     #velocity.data = [200, 200, 300, 0]
        #     #speaker(velocity)
        #     arm(arm_angle)
        #     talker(angles)
        #     rospy.sleep(2)
 
            # angles.data = [0, 50, -270, 500, -250, -200, 0, 110, -270, 500, -250, 50]
            # arm_angle.data = [-1700, 0, 0, 0, 0, 0]
            # #velocity.data = [200, 200, 300, 0]
            # #speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
            
            # angles.data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # arm_angle.data = [0, 0, 0, 0, 0, 0]
            # velocity.data = [200, 200, 300, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
            
            # #dobrar o joelho
            # angles.data = [0, 0, -270, 500, -250, 0, 0, 0, -270, 500, -250, 0]
            # velocity.data = [400, 400, 300, 0]
            # arm_angle.data = [200, 835-835, 0, 200, -791+791, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(0.5)

            # #levantar braços
            # angles.data = [0, 50, -270, 500, -250, -200, 0, 110, -270, 500, -250, 50]
            # #angles.data = [0, 50, -270, 500, -250, -150, 0, 160, -270, 500, -250, 20]
            # velocity.data = [400, 400, 600, 0]
            # arm_angle.data = [200-1800, 0, 0, 200+1800, 0, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
            

            # #equilibrar em uma perna
            # angles.data = [0, 20, -300, 500, -250, -150, 0, 110, -360, 520, -250, 0]
            # arm_angle.data = [-300, 100, 0, 300, 0, 0]
            # velocity.data = [20, 20, 100, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(1)
     
       
        
        
            # rospy.sleep(1)
            # angles.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
            # arm_angle.data = [0, 700, 0, 1700, 700, 0]
            # #velocity.data = [200, 200, 300, 0]
            # #speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(4)

            # #levantar braços
            # angles.data = [0, 0, -400, 670, -320, 0, 0, 0, -370, 670, -310, 0]
            # arm_angle.data = [0, 0, 0, 1700, 0, 0]
            # #velocity.data = [200, 200, 300, 0]
            # #speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)

            # angles.data = [0, 110, -400, 150, -320, 50, 0, 50, -370, 670, -310, -200]
            # arm_angle.data = [0, 0, 0, 1700, 0, 0]
            # #velocity.data = [200, 200, 300, 0]
            # #speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
           
            # angles.data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # arm_angle.data = [0, 0, 0, 0, 0, 0]
            # velocity.data = [200, 200, 300, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
            
            # #dobrar o joelho
            # angles.data = [0, 0, -270, 500, -250, 0, 0, 0, -270, 500, -250, 0]
            # velocity.data = [400, 400, 300, 0]
            # arm_angle.data = [200, 835-835, 0, 200, -791+791, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(0.5)

            # #levantar braços
            # angles.data = [0, 50, -270, 500, -250, -200, 0, 110, -270, 500, -250, 50]
            # #angles.data = [0, 50, -270, 500, -250, -150, 0, 160, -270, 500, -250, 20]
            # velocity.data = [400, 400, 600, 0]
            # arm_angle.data = [200-1800, 0, 0, 200+1800, 0, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(2)
            

            # #equilibrar em uma perna
            # angles.data = [0, 20, -300, 500, -250, -150, 0, 110, -360, 520, -250, 0]
            # arm_angle.data = [-300, 100, 0, 300, 0, 0]
            # velocity.data = [20, 20, 100, 0]
            # speaker(velocity)
            # arm(arm_angle)
            # talker(angles)
            # rospy.sleep(1)
            
        # else:
        #     rospy.loginfo("to no meio e com a camera parada")
    # else:
    #     rospy.loginfo("to mexendo minha cabeça adoidada")
    #     pub_angles.publish(angles)
    # #print(mt.tan(abacate))
    # #rospy.loginfo("este é ball_distance.data %s", ball_distance.data)
    # pub_distance.publish(ball_distance)

    #time.sleep(0.8)

def distance_callback(data):
        #print(data)
        #quat = [data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w]
        #(roll, pitch, yaw) = euler_from_quaternion(quat)
        alpha = mt.pi/2 - angles.data[1]
        ball_distance.data = mt.tan(alpha) * h_cam
        pub_distance.publish(ball_distance)

def angles_sub():
    rospy.Subscriber('/ball_pose', Float32MultiArray, angles_callback)
    flow_sub = rospy.Subscriber("flux_opt", Float32MultiArray, optical_callback)
    rospy.spin()

if __name__=='__main__':
    rospy.init_node('angles_publisher')
    rospy.loginfo('angles_pub node started')
    angles = Int16MultiArray()
    velocity = Int16MultiArray()
    arm_angle = Int16MultiArray()
    rate = rospy.Rate(10)
    pub = rospy.Publisher('/servo', Int16MultiArray, queue_size=100)
    vel = rospy.Publisher('/velocity', Int16MultiArray, queue_size=100)
    arm_pub = rospy.Publisher('/arms', Int16MultiArray, queue_size=100)
    angles.data = [0, -50]
    pub_angles.publish(angles)
    angles_sub()
