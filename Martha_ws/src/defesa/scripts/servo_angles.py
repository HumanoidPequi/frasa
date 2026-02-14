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
angles = Int16MultiArray()

# Carregamento dos parâmetros da câmera
with open('/home/marta/marta_simulation/Martha_ws/src/defesa/scripts/params2.yaml') as f:
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

# Variáveis de temporização
start_time = None
condition_met = False

def angles_callback(msg):
    global theta_y, theta_z, start_time, condition_met
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

    #rospy.loginfo('Os ângulos são: theta_y = %i, theta_z = %i', theta_y, theta_z)

    # Publica os ângulos
    if pub_angles.get_num_connections() > 0:
        pub_angles.publish(angles)

    # Cálculo da distância da bola
    alpha = 90 - abs(angles.data[1]) / 10
    alpha_rad = mt.radians(alpha)
    ball_distance.data = h_cam / mt.tan(abs(alpha_rad))
    #rospy.loginfo("Distância da bola: %s", ball_distance.data)

    # Publica a distância da bola
    if pub_distance.get_num_connections() > 0:
        pub_distance.publish(ball_distance)

    # Verificação da condição para cair
    if ball_distance.data > 75.0 and theta_z < -7.0:
        #rospy.loginfo("Condição para cair à direita detectada.")
        if not condition_met:
            condition_met = True
            start_time = rospy.get_time()
        elif rospy.get_time() - start_time >= 0.3:
            rospy.loginfo("Publicando ação: Cair à Direita")
            goal_data = {"Lado": 1}
            enviar_goal(goal_data)

    elif ball_distance.data > 75.0 and theta_z > 7.0:
        #rospy.loginfo("Condição para cair à esquerda detectada.")
        if not condition_met:
            condition_met = True
            start_time = rospy.get_time()
        elif rospy.get_time() - start_time >= 0.3:
            #rospy.loginfo("Publicando ação: Cair à Esquerda")
            goal_data = {"Lado": 0}
            enviar_goal(goal_data)

    else:
        condition_met = False
        start_time = None

def enviar_goal(goal_data):
    goal_json = json.dumps(goal_data)
    goal_msg = TaffarelGoal()
    goal_msg.json = goal_json

    if client.wait_for_server(timeout=rospy.Duration(1.0)):
        client.send_goal(goal_msg)
        #rospy.loginfo("Goal enviado com sucesso.")
    else:
        #rospy.logwarn("Servidor de ação não está pronto. Tentando novamente...")
        rospy.sleep(2)

def angles_sub():
    rospy.Subscriber('/ball_pose', Float32MultiArray, angles_callback)
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node('head_control_node')
    #rospy.loginfo('O nó head_control_node foi iniciado')

    angles_sub()
