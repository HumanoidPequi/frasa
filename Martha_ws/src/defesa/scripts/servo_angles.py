#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float32MultiArray, Int16MultiArray, Float32

import yaml
import numpy as np
import math as mt

import json
import actionlib
from marta_msgs.msg import TaffarelGoal, TaffarelAction

client = actionlib.SimpleActionClient('taffarel_server_node', TaffarelAction)

# Definição dos tópicos e mensagens
pub_angles = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray, queue_size=1)
pub_distance = rospy.Publisher("ball_distance", Float32, queue_size=1)
pub_action = rospy.Publisher('/marta/fall_action', Int16MultiArray, queue_size=1)  # Tópico para as ações de cair
pub = rospy.Publisher('/taffarel_server_node/goal', TaffarelGoal, queue_size=10)
angles = Int16MultiArray()
action_msg = Int16MultiArray()

# Carregamento dos parâmetros da câmera
with open('/home/fabrycio/Downloads/marta_simulation/Martha_ws/src/defesa/scripts/params2.yaml') as f:
    cam_params = yaml.load(f, Loader=yaml.FullLoader)
    intrinsic = np.array(cam_params['mtx'])

fx = intrinsic[0, 0]
fy = intrinsic[1, 1]
cx = 320
cy = 240

# Ângulos iniciais e altura da câmera
theta_z = 0
theta_y = -50
h_cam = 57  # cm
ball_distance = Float32()

def angles_callback(msg):
    global theta_y, theta_z
    angles.data = [theta_z * 10, theta_y * 10, 0, 0, 0]
    
    # Verificação da posição da bola
    if msg.data[0] != 1000 and msg.data[1] != 1000:
        v = msg.data[0]
        u = msg.data[1]

        # Ajuste de ângulos com base na posição da bola
        if abs(v - cx) > 25 or abs(u - cy) > 20:
            x = -(v - cx)
            y = -(u - cy)
            theta_z += int(np.arctan2(x, fx) * 180 / mt.pi)
            theta_y += int(np.arctan2(y, fy) * 180 / mt.pi)

            # Limites de ângulos
            theta_y = max(-70, min(theta_y, -20))
            theta_z = max(-50, min(theta_z, 50))

            angles.data = [theta_z * 10, theta_y * 10, 0, 0, 0]
    
    else:
        theta_z = 0
        theta_y = -50
        angles.data = [theta_z * 10, theta_y * 10, 0, 0, 0]

    rospy.loginfo('the angles are %i, %i', theta_y, theta_z)
    pub_angles.publish(angles)

    # Cálculo da distância da bola
    alpha = 90 - angles.data[1] / 10
    alpha_rad = mt.radians(alpha)
    ball_distance.data = h_cam / mt.tan(alpha_rad)
    rospy.loginfo("ball_distance.data: %s", ball_distance.data)
    pub_distance.publish(ball_distance)

    ball_distance.data = 20
    theta_z = 25
    # Publicação da ação com base nas condições
    if ball_distance.data < 30 and theta_z > 20:  # Ajuste de condições conforme necessário
        rospy.loginfo("Publicando ação: Cair à Direita")
        goal_data = {
            "Lado": 1   
        }

        goal_json = json.dumps(goal_data)

        goal_msg = TaffarelGoal()
        goal_msg.json = goal_json
    else:
        rospy.loginfo("Publicando ação: Cair à Esquerda")
        goal_data = {
            "Lado": 0
        }

        goal_json = json.dumps(goal_data)

        goal_msg = TaffarelGoal()
        goal_msg.json = goal_json
    
    client.send_goal(goal_msg)

def angles_sub():
    rospy.Subscriber('/ball_pose', Float32MultiArray, angles_callback)
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node('head_control_node')
    rospy.loginfo('angles_pub node started')
    pub_angles.publish(angles)
    angles_sub()
