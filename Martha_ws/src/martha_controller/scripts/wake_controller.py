#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
import time

def move_joints_smoothly(publishers, start_positions, end_positions, duration):
    # Move múltiplas articulações suavemente de start_positions para end_positions em 'duration' segundos.
    rate = 50  # Hz, número de atualizações por segundo
    steps = rate * duration  # Número total de passos para completar o movimento

    # Calcula o incremento por passo para cada articulação
    delta_positions = [(end - start) / steps for start, end in zip(start_positions, end_positions)]

    for i in range(int(steps)):
        for pub, start, delta in zip(publishers, start_positions, delta_positions):
            current_position = start + delta * i
            pub.publish(Float64(current_position))
        time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização

def levantar_de_tras():
    rospy.loginfo("Iniciando movimento de levantamento de trás...")

    # Phase 1: Preparing to lift
    rospy.loginfo("Fase 1: Preparando para levantar...")
    publishers_phase1 = [
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_hip_pitch, pub_l_hip_pitch,
        pub_r_knee, pub_l_knee
    ]
    start_positions_phase1 = [0.0] * len(publishers_phase1)
    end_positions_phase1 = [
        -1.5, 1.5,  # Shoulders: move arms towards the shoulders
        -0.5, -0.5,  # Hips: flex hips to bring feet closer
        1.5, 1.5     # Knees: slightly bend
    ]
    move_joints_smoothly(publishers_phase1, start_positions_phase1, end_positions_phase1, 2)
    time.sleep(10)
    # Phase 2: Pushing up
    rospy.loginfo("Fase 2: Empurrando para cima...")
    publishers_phase2 = [
        pub_r_elbow, pub_l_elbow,
        pub_r_knee, pub_l_knee,
        pub_r_hip_pitch, pub_l_hip_pitch
    ]
    start_positions_phase2 = [
        0.0, 0.0,      # Elbows: start from initial position
        0.5, 0.5,      # Knees: from the end of Phase 1
        -0.5, -0.5     # Hips: from the end of Phase 1
    ]
    end_positions_phase2 = [
        -1.5, -1.5,    # Elbows: extend to push up
        1.0, 1.0,      # Knees: bend further
        -1.0, -1.0     # Hips: flex slightly more
    ]
    move_joints_smoothly(publishers_phase2, start_positions_phase2, end_positions_phase2, 2)
    time.sleep(10)
    # Phase 3: Standing up and moving into T-pose
    rospy.loginfo("Fase 3: Levantando e posicionando em T...")
    publishers_phase3 = [
        pub_r_hip_pitch, pub_l_hip_pitch,
        pub_r_knee, pub_l_knee,
        pub_r_ankle_pitch, pub_l_ankle_pitch,
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_shoulder_roll, pub_l_shoulder_roll,
        pub_r_elbow, pub_l_elbow
    ]
    start_positions_phase3 = [
        -1.0, -1.0,    # Hips: from the end of Phase 2
        1.0, 1.0,      # Knees: from the end of Phase 2
        0.0, 0.0,      # Ankles: initial position
        -1.0, 1.0,     # Shoulders pitch: from the end of Phase 1
        0.0, 0.0,      # Shoulders roll: initial position
        -1.5, -1.5     # Elbows: from the end of Phase 2
    ]
    end_positions_phase3 = [
        0.0, 0.0,      # Hips: stand up straight
        0.0, 0.0,      # Knees: fully extended
        0.0, 0.0,      # Ankles: maintain balance
        0.0, 0.0,      # Shoulders pitch: arms down
        0.0, 0.0,      # Shoulders roll: arms to the sides (T-pose)
        0.0, 0.0       # Elbows: relax arms
    ]
    move_joints_smoothly(publishers_phase3, start_positions_phase3, end_positions_phase3, 3)

    rospy.loginfo("Robô levantado de trás e em T-pose.")

def levantar_de_frente():
    rospy.loginfo("Iniciando movimento de levantamento de frente...")

    # Passo 1: Girar ombro e ajustar antebraço para posição de apoio
    rospy.loginfo("Passo 1: Girando o ombro e ajustando o antebraço para apoio...")

    publishers_step1 = [
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_elbow, pub_l_elbow
    ]
    start_positions_step1 = [0.0, 0.0, 0.0, 0.0]
    end_positions_step1 = [
        -1.0, 1.0,     # Ombros: girar para apoio
        -2.0, -2.0     # Cotovelos: girar para perpendicularidade ao chão
    ]
    move_joints_smoothly(publishers_step1, start_positions_step1, end_positions_step1, 1)

    rospy.sleep(1)  

    # Passo 2: Empurrar o chão, dobrar joelhos e girar tornozelos
    rospy.loginfo("Passo 2: Empurrando o chão, dobrando joelhos e ajustando tornozelos...")

    publishers_step2 = [
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_knee, pub_l_knee,
        pub_r_hip_pitch, pub_l_hip_pitch,
        pub_r_ankle_pitch, pub_l_ankle_pitch  # Adicionando movimento de tornozelos
    ]
    start_positions_step2 = [
        -1.0, 1.0,     # Ombros: posição final do passo 1
        0.0, 0.0,      # Joelhos: posição inicial
        0.0, 0.0,      # Quadris: posição inicial
        0.0, 0.0       # Tornozelos: posição inicial
    ]
    end_positions_step2 = [
        1.0, -1.0,     # Ombros: estender para empurrar o chão
        1.5, 1.5,      # Joelhos: dobrar para trazer o peso para frente
        1.0, 1.0,      # Quadris: inclinar levemente para frente
        0.5, 0.5       # Tornozelos: inclinar para frente para auxiliar no equilíbrio
    ]
    move_joints_smoothly(publishers_step2, start_positions_step2, end_positions_step2, 2)

    rospy.sleep(1)  # Pausa de 10 segundos

    # Passo 3: Levantar o tronco e assumir a T-pose
    rospy.loginfo("Passo 3: Levantando o tronco para a T-pose...")

    publishers_step3 = [
        pub_r_hip_pitch, pub_l_hip_pitch,
        pub_r_knee, pub_l_knee,
        pub_r_shoulder_roll, pub_l_shoulder_roll,
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_elbow, pub_l_elbow,
        pub_r_ankle_pitch, pub_l_ankle_pitch  # Manter tornozelos no movimento final
    ]
    start_positions_step3 = [
        1.0, 1.0,    # Quadris: posição final do passo 2
        1.5, 1.5,      # Joelhos: posição final do passo 2
        0.0, 0.0,      # Ombros roll: posição inicial para elevação
        1.0, -1.0,     # Ombros pitch: posição inicial para elevação
        0.0, 0.0,      # Cotovelos: posição final do passo 2
        0.5, 0.5       # Tornozelos: posição final do passo 2 para auxiliar no equilíbrio
    ]
    end_positions_step3 = [
        0.0, 0.0,      # Quadris: posição ereta
        0.0, 0.0,      # Joelhos: completamente estendidos
        0.0, 0.0,      # Ombros roll: T-pose
        0.0, 0.0,      # Ombros pitch: T-pose
        0.0, 0.0,      # Cotovelos: relaxar para a posição T-pose
        0.0, 0.0       # Tornozelos: posição de equilíbrio final na T-pose
    ]
    move_joints_smoothly(publishers_step3, start_positions_step3, end_positions_step3, 3)

    rospy.loginfo("Robô levantado em T-pose.")




def set_joint_positions():
    rospy.init_node('humanoid_lift_node', anonymous=True)

    global pub_r_shoulder_pitch, pub_r_shoulder_roll, pub_r_elbow
    global pub_l_shoulder_pitch, pub_l_shoulder_roll, pub_l_elbow
    global pub_r_hip_pitch, pub_r_hip_roll, pub_r_knee, pub_r_ankle_pitch
    global pub_l_hip_pitch, pub_l_hip_roll, pub_l_knee, pub_l_ankle_pitch

    # Publishers para as articulações dos braços e pernas
    pub_r_shoulder_pitch = rospy.Publisher('/martha/r_sho_pitch_position/command', Float64, queue_size=10)
    pub_r_shoulder_roll = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)
    pub_r_elbow = rospy.Publisher('/martha/r_el_position/command', Float64, queue_size=10)

    pub_l_shoulder_pitch = rospy.Publisher('/martha/l_sho_pitch_position/command', Float64, queue_size=10)
    pub_l_shoulder_roll = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
    pub_l_elbow = rospy.Publisher('/martha/l_el_position/command', Float64, queue_size=10)

    # Publishers para as articulações do quadril, joelho e tornozelo
    pub_r_hip_pitch = rospy.Publisher('/martha/r_hip_pitch_position/command', Float64, queue_size=10)
    pub_r_hip_roll = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)
    pub_r_knee = rospy.Publisher('/martha/r_knee_position/command', Float64, queue_size=10)
    pub_r_ankle_pitch = rospy.Publisher('/martha/r_ank_pitch_position/command', Float64, queue_size=10)

    pub_l_hip_pitch = rospy.Publisher('/martha/l_hip_pitch_position/command', Float64, queue_size=10)
    pub_l_hip_roll = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
    pub_l_knee = rospy.Publisher('/martha/l_knee_position/command', Float64, queue_size=10)
    pub_l_ankle_pitch = rospy.Publisher('/martha/l_ank_pitch_position/command', Float64, queue_size=10)

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


# afsbdfbggb
# dfbbtrbtr
# tsbtrtr



# #!/usr/bin/env python3

# import rospy
# from std_msgs.msg import Float64
# import time

# def move_joint_smoothly(publisher, start_position, end_position, duration):
#     # Move a articulação suavemente de start_position para end_position em 'duration' segundos.
#     rate = 50  # Hz, número de atualizações por segundo
#     steps = rate * duration  # Número total de passos para completar o movimento
#     delta_position = (end_position - start_position) / steps  # Incremento por passo

#     for i in range(int(steps)):
#         current_position = start_position + delta_position * i
#         publisher.publish(Float64(current_position))
#         time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização

# def levantar_de_frente():
#     rospy.loginfo("Iniciando movimento de levantamento de frente...")

#     # Movimento para levantar o robô de frente usando move_joint_smoothly
#     move_joint_smoothly(pub_l_hip_pitch, 0.0, -1.0, 1)
#     move_joint_smoothly(pub_r_hip_pitch, 0.0, -1.0, 1)

#     move_joint_smoothly(pub_l_knee, 0.0, 1.5, 1)
#     move_joint_smoothly(pub_r_knee, 0.0, 1.5, 1)

#     move_joint_smoothly(pub_l_ankle_pitch, 0.0, -0.5, 1)
#     move_joint_smoothly(pub_r_ankle_pitch, 0.0, -0.5, 1)

#     move_joint_smoothly(pub_l_hip_pitch, -1.0, 0.0, 1)
#     move_joint_smoothly(pub_r_hip_pitch, -1.0, 0.0, 1)

#     rospy.loginfo("Robô levantado de frente.")

# def levantar_de_tras():
#     rospy.loginfo("Iniciando movimento de levantamento de trás...")

#     # Movimento para levantar o robô de trás usando move_joint_smoothly

#     move_joint_smoothly(pub_r_elbow, 0.0, -1.5, 1), move_joint_smoothly(pub_l_elbow, 0.0, -1.5, 1)
    

#     move_joint_smoothly(pub_r_shoulder_pitch, 0.0, -2, 1)
#     move_joint_smoothly(pub_l_shoulder_pitch, 0.0, 2, 1)

#     move_joint_smoothly(pub_r_elbow, 0.0, -0.5, 1)
#     move_joint_smoothly(pub_l_elbow, 0.0, -0.5, 1)

#     move_joint_smoothly(pub_r_shoulder_pitch, -1.5, 0.0, 1)
#     move_joint_smoothly(pub_l_shoulder_pitch, 1.5, 0.0, 1)

#     move_joint_smoothly(pub_l_knee, 0.0, 1.5, 1)
#     move_joint_smoothly(pub_r_knee, 0.0, 1.5, 1)

#     move_joint_smoothly(pub_l_hip_pitch, 0.0, -1.0, 1)
#     move_joint_smoothly(pub_r_hip_pitch, 0.0, -1.0, 1)

#     move_joint_smoothly(pub_l_ankle_pitch, 0.0, 0.5, 1)
#     move_joint_smoothly(pub_r_ankle_pitch, 0.0, 0.5, 1)

#     move_joint_smoothly(pub_l_hip_pitch, -1.0, 0.0, 1)
#     move_joint_smoothly(pub_r_hip_pitch, -1.0, 0.0, 1)

#     rospy.loginfo("Robô levantado de trás.")

# # A função set_joint_positions permanece inalterada
# def set_joint_positions():
#     rospy.init_node('humanoid_lift_node', anonymous=True)

#     global pub_r_shoulder_pitch, pub_r_shoulder_roll, pub_r_elbow, pub_l_shoulder_pitch, pub_l_shoulder_roll, pub_l_elbow
#     global pub_r_hip_yaw, pub_r_hip_roll, pub_r_hip_pitch, pub_r_knee, pub_r_ankle_pitch, pub_r_ankle_roll
#     global pub_l_hip_yaw, pub_l_hip_roll, pub_l_hip_pitch, pub_l_knee, pub_l_ankle_pitch, pub_l_ankle_roll

#     # Publishers para as articulações do braço e pernas
#     pub_r_shoulder_pitch = rospy.Publisher('/martha/r_sho_pitch_position/command', Float64, queue_size=10)
#     pub_r_shoulder_roll = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)
#     pub_r_elbow = rospy.Publisher('/martha/r_el_position/command', Float64, queue_size=10)

#     pub_l_shoulder_pitch = rospy.Publisher('/martha/l_sho_pitch_position/command', Float64, queue_size=10)
#     pub_l_shoulder_roll = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
#     pub_l_elbow = rospy.Publisher('/martha/l_el_position/command', Float64, queue_size=10)

#     pub_r_hip_yaw = rospy.Publisher('/martha/r_hip_yaw_position/command', Float64, queue_size=10)
#     pub_r_hip_roll = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)
#     pub_r_hip_pitch = rospy.Publisher('/martha/r_hip_pitch_position/command', Float64, queue_size=10)
#     pub_r_knee = rospy.Publisher('/martha/r_knee_position/command', Float64, queue_size=10)
#     pub_r_ankle_pitch = rospy.Publisher('/martha/r_ank_pitch_position/command', Float64, queue_size=10)
#     pub_r_ankle_roll = rospy.Publisher('/martha/r_ank_roll_position/command', Float64, queue_size=10)

#     pub_l_hip_yaw = rospy.Publisher('/martha/l_hip_yaw_position/command', Float64, queue_size=10)
#     pub_l_hip_roll = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
#     pub_l_hip_pitch = rospy.Publisher('/martha/l_hip_pitch_position/command', Float64, queue_size=10)
#     pub_l_knee = rospy.Publisher('/martha/l_knee_position/command', Float64, queue_size=10)
#     pub_l_ankle_pitch = rospy.Publisher('/martha/l_ank_pitch_position/command', Float64, queue_size=10)
#     pub_l_ankle_roll = rospy.Publisher('/martha/l_ank_roll_position/command', Float64, queue_size=10)

#     rospy.sleep(1)

#     # Escolher o movimento 
#     movimento = input("Digite 'frente' para levantar de frente ou 'tras' para levantar de trás: ")

#     if movimento == 'frente':
#         levantar_de_frente()
#     elif movimento == 'tras':
#         levantar_de_tras()
#     else:
#         rospy.loginfo("Movimento inválido.")

# if __name__ == '__main__':
#     try:
#         set_joint_positions()
#     except rospy.ROSInterruptException:
#         pass
