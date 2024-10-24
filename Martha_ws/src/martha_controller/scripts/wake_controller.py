#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
import numpy as np

l1 = 0.3  # Comprimento da coxa
l2 = 0.3  # Comprimento da perna
l_arm = 0.25  # Comprimento do braço superior
l_forearm = 0.25  # Comprimento do antebraço

pub_hip_esquerdo = rospy.Publisher('/humanoid/quadril_esquerdo_rX_position_controller/command', Float64, queue_size=10)
pub_hip_direito = rospy.Publisher('/humanoid/quadril_direito_rX_position_controller/command', Float64, queue_size=10)
pub_knee_esquerdo = rospy.Publisher('/humanoid/joelho_esquerdo_rX_position_controller/command', Float64, queue_size=10)
pub_knee_direito = rospy.Publisher('/humanoid/joelho_direito_rX_position_controller/command', Float64, queue_size=10)
pub_shoulder_esquerdo = rospy.Publisher('/humanoid/ombro_esquerdo_rX_position_controller/command', Float64, queue_size=10)
pub_shoulder_direito = rospy.Publisher('/humanoid/ombro_direito_rX_position_controller/command', Float64, queue_size=10)
pub_elbow_esquerdo = rospy.Publisher('/humanoid/mao_esquerda_position_controller/command', Float64, queue_size=10)
pub_elbow_direito = rospy.Publisher('/humanoid/mao_direita_position_controller/command', Float64, queue_size=10)

def calcular_angulo_levantar_de_frente():
    angulos_levantamento_frente = {
        'hip': [-np.pi/4, -np.pi/6, 0, np.pi/6, np.pi/4],  # Ângulos do quadril
        'knee': [np.pi/2, np.pi/3, np.pi/4, np.pi/6, 0],  # Ângulos do joelho
        'shoulder': [-np.pi/4, -np.pi/6, 0, np.pi/6, np.pi/4],  # Ângulos do ombro
        'elbow': [np.pi/4, np.pi/6, 0, -np.pi/6, -np.pi/4]  # Ângulos do cotovelo
    }
    return angulos_levantamento_frente

def calcular_angulo_levantar_de_tras():
    angulos_levantamento_tras = {
        'hip': [np.pi/4, np.pi/6, 0, -np.pi/6, -np.pi/4],  # Ângulos do quadril
        'knee': [np.pi/6, np.pi/4, np.pi/3, np.pi/2, np.pi],  # Ângulos do joelho
        'shoulder': [np.pi/4, np.pi/6, 0, -np.pi/6, -np.pi/4],  # Ângulos do ombro
        'elbow': [-np.pi/4, -np.pi/6, 0, np.pi/6, np.pi/4]  # Ângulos do cotovelo
    }
    return angulos_levantamento_tras

def publicar_angulos(angulos_levantamento):
    rate = rospy.Rate(1)
    for i in range(len(angulos_levantamento['hip'])):
        pub_hip_esquerdo.publish(angulos_levantamento['hip'][i])
        pub_hip_direito.publish(angulos_levantamento['hip'][i])
        pub_knee_esquerdo.publish(angulos_levantamento['knee'][i])
        pub_knee_direito.publish(angulos_levantamento['knee'][i])
        
        pub_shoulder_esquerdo.publish(angulos_levantamento['shoulder'][i])
        pub_shoulder_direito.publish(angulos_levantamento['shoulder'][i])
        pub_elbow_esquerdo.publish(angulos_levantamento['elbow'][i])
        pub_elbow_direito.publish(angulos_levantamento['elbow'][i])
        
        rospy.loginfo(f"Publicando ângulos - Fase {i+1}")
        rate.sleep()

def main():
    rospy.init_node('humanoid_lift_node')

    movimento = input("Digite 'frente' para levantar de frente ou 'tras' para levantar de trás: ")

    if movimento == 'frente':
        angulos_frente = calcular_angulo_levantar_de_frente()
        rospy.loginfo("Levantar de frente...")
        publicar_angulos(angulos_frente)
    elif movimento == 'tras':
        angulos_tras = calcular_angulo_levantar_de_tras()
        rospy.loginfo("Levantar de trás...")
        publicar_angulos(angulos_tras)
    else:
        rospy.loginfo("Movimento inválido.")

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
