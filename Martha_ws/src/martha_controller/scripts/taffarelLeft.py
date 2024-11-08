#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
import time

def move_joint_smoothly(publisher, start_position, end_position, duration):
    
    #Move a articulação suavemente de start_position para end_position em 'duration' segundos.
    
    rate = 50  # Hz, número de atualizações por segundo
    steps = rate * duration  # Número total de passos para completar o movimento
    delta_position = (end_position - start_position) / steps  # Incremento por passo

    for i in range(int(steps)):
        current_position = start_position + delta_position * i
        publisher.publish(Float64(current_position))
        time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização


def set_joint_positions():
    rospy.init_node('martha_fall_right', anonymous=True)

    # Publishers para as articulações do braço e pernas da Martha
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

    

    rospy.sleep(1)  # Dar tempo para os publishers inicializarem

    # Levanta o braço esquerdo lentamente
    start_position_l_shoulder_pitch = 0.0  # Posição inicial
    end_position_l_shoulder_pitch = 2.8    # Posição final (levantado)
    duration = 2.0                         # Tempo para levantar o braço

    # Mover o braço esquerdo suavemente ao longo de 5 segundos
    move_joint_smoothly(pub_l_shoulder_pitch, start_position_l_shoulder_pitch, end_position_l_shoulder_pitch, duration)

    # Publicar posições fixas para as outras articulações
    pub_r_shoulder_roll.publish(0.0)  # Para o lado direito
    pub_r_elbow.publish(0.0)          # Dobra o cotovelo


    # Coloca o braço direito para baixo
    pub_r_shoulder_pitch.publish(0.0)
    pub_r_shoulder_roll.publish(0.0)
    pub_r_elbow.publish(0.0)

    rospy.sleep(1)

    # Mover as pernas para cair para o lado esquerdo
    pub_l_hip_roll.publish(0.5)
    pub_l_ankle_roll.publish(-0.3)

    pub_r_hip_roll.publish(0.5)
    pub_r_ankle_roll.publish(-0.3)

    rospy.sleep(5)  # Espera para que as posições sejam atingidas

if __name__ == '__main__':
    try:
        set_joint_positions()
    except rospy.ROSInterruptException:
        pass

