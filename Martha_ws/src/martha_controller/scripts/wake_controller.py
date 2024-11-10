#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
import time

def move_joint_smoothly(publisher, start_position, end_position, duration):
    # Move a articulação suavemente de start_position para end_position em 'duration' segundos.
    rate = 50  # Hz, número de atualizações por segundo
    steps = rate * duration  # Número total de passos para completar o movimento
    delta_position = (end_position - start_position) / steps  # Incremento por passo

    for i in range(int(steps)):
        current_position = start_position + delta_position * i
        publisher.publish(Float64(current_position))
        time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização

def levantar_de_frente():
    rospy.loginfo("Iniciando movimento de levantamento de frente...")

    # Movimento para levantar o robô de frente usando move_joint_smoothly
    move_joint_smoothly(pub_l_hip_pitch, 0.0, -1.0, 1)
    move_joint_smoothly(pub_r_hip_pitch, 0.0, -1.0, 1)

    move_joint_smoothly(pub_l_knee, 0.0, 1.5, 1)
    move_joint_smoothly(pub_r_knee, 0.0, 1.5, 1)

    move_joint_smoothly(pub_l_ankle_pitch, 0.0, -0.5, 1)
    move_joint_smoothly(pub_r_ankle_pitch, 0.0, -0.5, 1)

    move_joint_smoothly(pub_l_hip_pitch, -1.0, 0.0, 1)
    move_joint_smoothly(pub_r_hip_pitch, -1.0, 0.0, 1)

    rospy.loginfo("Robô levantado de frente.")

def levantar_de_tras():
    rospy.loginfo("Iniciando movimento de levantamento de trás...")

    # Movimento para levantar o robô de trás usando move_joint_smoothly
    move_joint_smoothly(pub_r_shoulder_pitch, 0.0, -1.5, 1)
    move_joint_smoothly(pub_l_shoulder_pitch, 0.0, 1.5, 1)

    move_joint_smoothly(pub_r_elbow, 0.0, -0.5, 1)
    move_joint_smoothly(pub_l_elbow, 0.0, -0.5, 1)

    move_joint_smoothly(pub_r_shoulder_pitch, -1.5, 0.0, 1)
    move_joint_smoothly(pub_l_shoulder_pitch, 1.5, 0.0, 1)

    move_joint_smoothly(pub_l_knee, 0.0, 1.5, 1)
    move_joint_smoothly(pub_r_knee, 0.0, 1.5, 1)

    move_joint_smoothly(pub_l_hip_pitch, 0.0, -1.0, 1)
    move_joint_smoothly(pub_r_hip_pitch, 0.0, -1.0, 1)

    move_joint_smoothly(pub_l_ankle_pitch, 0.0, 0.5, 1)
    move_joint_smoothly(pub_r_ankle_pitch, 0.0, 0.5, 1)

    move_joint_smoothly(pub_l_hip_pitch, -1.0, 0.0, 1)
    move_joint_smoothly(pub_r_hip_pitch, -1.0, 0.0, 1)

    rospy.loginfo("Robô levantado de trás.")

# A função set_joint_positions permanece inalterada
def set_joint_positions():
    rospy.init_node('humanoid_lift_node', anonymous=True)

    global pub_r_shoulder_pitch, pub_r_shoulder_roll, pub_r_elbow, pub_l_shoulder_pitch, pub_l_shoulder_roll, pub_l_elbow
    global pub_r_hip_yaw, pub_r_hip_roll, pub_r_hip_pitch, pub_r_knee, pub_r_ankle_pitch, pub_r_ankle_roll
    global pub_l_hip_yaw, pub_l_hip_roll, pub_l_hip_pitch, pub_l_knee, pub_l_ankle_pitch, pub_l_ankle_roll

    # Publishers para as articulações do braço e pernas
    pub_r_shoulder_pitch = rospy.Publisher('/martha/r_sho_pitch_position/command', Float64, queue_size=10)
    pub_r_shoulder_roll = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)
    pub_r_elbow = rospy.Publisher('/martha/r_el_position/command', Float64, queue_size=10)

    pub_l_shoulder_pitch = rospy.Publisher('/martha/l_sho_pitch_position/command', Float64, queue_size=10)
    pub_l_shoulder_roll = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
    pub_l_elbow = rospy.Publisher('/martha/l_el_position/command', Float64, queue_size=10)

    pub_r_hip_yaw = rospy.Publisher('/martha/r_hip_yaw_position/command', Float64, queue_size=10)
    pub_r_hip_roll = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)
    pub_r_hip_pitch = rospy.Publisher('/martha/r_hip_pitch_position/command', Float64, queue_size=10)
    pub_r_knee = rospy.Publisher('/martha/r_knee_position/command', Float64, queue_size=10)
    pub_r_ankle_pitch = rospy.Publisher('/martha/r_ank_pitch_position/command', Float64, queue_size=10)
    pub_r_ankle_roll = rospy.Publisher('/martha/r_ank_roll_position/command', Float64, queue_size=10)

    pub_l_hip_yaw = rospy.Publisher('/martha/l_hip_yaw_position/command', Float64, queue_size=10)
    pub_l_hip_roll = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
    pub_l_hip_pitch = rospy.Publisher('/martha/l_hip_pitch_position/command', Float64, queue_size=10)
    pub_l_knee = rospy.Publisher('/martha/l_knee_position/command', Float64, queue_size=10)
    pub_l_ankle_pitch = rospy.Publisher('/martha/l_ank_pitch_position/command', Float64, queue_size=10)
    pub_l_ankle_roll = rospy.Publisher('/martha/l_ank_roll_position/command', Float64, queue_size=10)

    rospy.sleep(1)

    # Escolher o movimento 
    movimento = input("Digite 'frente' para levantar de frente ou 'tras' para levantar de trás: ")

    if movimento == 'frente':
        levantar_de_frente()
    elif movimento == 'tras':
        levantar_de_tras()
    else:
        rospy.loginfo("Movimento inválido.")

if __name__ == '__main__':
    try:
        set_joint_positions()
    except rospy.ROSInterruptException:
        pass
