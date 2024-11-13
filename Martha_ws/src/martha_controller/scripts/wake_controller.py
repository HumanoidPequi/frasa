#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
import time
import math

def rad_to_deg(radian):
    return radian * (180.0 / math.pi)

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
    rospy.loginfo("Iniciando movimento de levantamento de costas...")

    # Fase 1: Puxar o braço para trás
    rospy.loginfo("Fase 1: Puxando o braço para trás para apoio...")

    publishers_phase1 = [
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_elbow, pub_l_elbow
    ]
    start_positions_phase1 = [0.0, 0.0, 0.0, 0.0]
    end_positions_phase1 = [
        -1.5, 1.5,  # Ombros: continuar puxando o braço para trás
        -1.5, -1.5    # Cotovelos: levantados para trás
    ]
    move_joints_smoothly(publishers_phase1, start_positions_phase1, end_positions_phase1, 1)

    rospy.sleep(1)  # Pequena pausa para garantir que o braço foi puxado para trás

    # Fase 2: Zerar antebraço e ajustar pernas e tornozelos
    rospy.loginfo("Fase 2: Zerando o antebraço e ajustando pernas e tornozelos...")

    publishers_phase2 = [
        pub_r_elbow, pub_l_elbow,
        #pub_r_knee, pub_l_knee,
        #pub_r_ankle_pitch, pub_l_ankle_pitch,
        #pub_r_hip_pitch, pub_l_hip_pitch,
    ]
    start_positions_phase2 = [
        -1.0, -1.0,   # Cotovelos: posição final da Fase 1
        #0.0, 0.0,   # Joelhos: posição inicial
        #0.0, 0.0,   # Tornozelos: posição inicial
        #0.0, 0.0    # Quadril: posição inicial
    ]
    end_positions_phase2 = [
        0.0, 0.0,   # Cotovelos: zerados para empurrar o chão
        #1.5, 1.5,   # Joelhos: dobrados para encolher as pernas
        #-1.0, -1.0,  # Tornozelos: girados ao contrário para equilíbrio
        #1.5, 1.5    # Quadril: posição final
    ]
    move_joints_smoothly(publishers_phase2, start_positions_phase2, end_positions_phase2, 2)

    rospy.sleep(3)  # Pausa para garantir que as pernas e tornozelos estejam ajustados

    # Passo final: Levantar o tronco e assumir a T-pose
    rospy.loginfo("Levantando o tronco para a T-pose...")

    publishers_step3 = [
        # pub_r_hip_pitch, pub_l_hip_pitch,
        # pub_r_knee, pub_l_knee,
        # pub_r_shoulder_roll, pub_l_shoulder_roll,
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        #pub_r_elbow, pub_l_elbow,
        # pub_r_ankle_pitch, pub_l_ankle_pitch  # Manter tornozelos no movimento final
    ]
    start_positions_step3 = [
        # 1.5, 1.5,    # Quadris: posição final do passo anterior
        # 1.5, 1.5,    # Joelhos: posição final do passo anterior
        # 0.0, 0.0,    # Ombros roll: posição inicial para elevação
        # 1.5, -1.5,   # Ombros pitch: posição inicial para elevação
        -1.5, 1.5,    # Cotovelos: posição final do passo anterior
        # -1.0, -1.0   # Tornozelos: posição final do passo anterior para equilíbrio
    ]
    end_positions_step3 = [
        # 0.0, 0.0,    # Quadris: posição ereta
        # 0.0, 0.0,    # Joelhos: completamente estendidos
        # 0.0, 0.0,    # Ombros roll: T-pose
        # 0.0, 0.0,    # Ombros pitch: T-pose
        0.0, 1.5,    # Cotovelos: relaxar para a posição T-pose
        # 0.0, 0.0     # Tornozelos: posição de equilíbrio final na T-pose
    ]
    move_joints_smoothly(publishers_step3, start_positions_step3, end_positions_step3, 3)

    rospy.loginfo("Robô levantado em T-pose.")

# def levantar_de_tras():
#     rospy.loginfo("Iniciando movimento de levantamento de costas...")

#     # Fase 1: Puxar o braço para trás
#     rospy.loginfo("Fase 1: Puxando o braço para trás para apoio...")

#     publishers_phase1 = [
#         pub_r_shoulder_pitch, pub_l_shoulder_pitch,
#         pub_r_elbow, pub_l_elbow
#     ]
#     start_positions_phase1 = [0.0, 0.0, 0.0, 0.0]
#     end_positions_phase1 = [
#         -1.5, 1.5,  # Ombros: continuar puxando o braço para trás
#         -1.5, -1.5    # Cotovelos: levantados para trás
#     ]
#     move_joints_smoothly(publishers_phase1, start_positions_phase1, end_positions_phase1, 1)

#     rospy.sleep(1)  # Pequena pausa para garantir que o braço foi puxado para trás

#     # Fase 2: Zerar antebraço e ajustar pernas e tornozelos
#     rospy.loginfo("Fase 2: Zerando o antebraço e ajustando pernas e tornozelos...")

#     publishers_phase2 = [
#         pub_r_elbow, pub_l_elbow,
#         pub_r_knee, pub_l_knee,
#         pub_r_ankle_pitch, pub_l_ankle_pitch,
#          pub_r_hip_pitch, pub_l_hip_pitch,
#     ]
#     start_positions_phase2 = [
#         -1.0, -1.0,   # Cotovelos: posição final da Fase 1
#         0.0, 0.0,   # Joelhos: posição inicial
#         0.0, 0.0,   # Tornozelos: posição inicial
#         0.0, 0.0    # Quadril: posição inicial
#     ]
#     end_positions_phase2 = [
#         0.0, 0.0,   # Cotovelos: zerados para empurrar o chão
#         1.5, 1.5,   # Joelhos: dobrados para encolher as pernas
#         -1.0, -1.0,  # Tornozelos: girados ao contrário para equilíbrio
#         1.5, 1.5    # Quadril: posição final
#     ]
#     move_joints_smoothly(publishers_phase2, start_positions_phase2, end_positions_phase2, 2)

#     rospy.sleep(3)  # Pausa para garantir que as pernas e tornozelos estejam ajustados

#     # Passo final: Levantar o tronco e assumir a T-pose
#     rospy.loginfo("Levantando o tronco para a T-pose...")

#     publishers_step3 = [
#         pub_r_hip_pitch, pub_l_hip_pitch,
#         pub_r_knee, pub_l_knee,
#         pub_r_shoulder_roll, pub_l_shoulder_roll,
#         pub_r_shoulder_pitch, pub_l_shoulder_pitch,
#         pub_r_elbow, pub_l_elbow,
#         pub_r_ankle_pitch, pub_l_ankle_pitch  # Manter tornozelos no movimento final
#     ]
#     start_positions_step3 = [
#         1.5, 1.5,    # Quadris: posição final do passo anterior
#         1.5, 1.5,    # Joelhos: posição final do passo anterior
#         0.0, 0.0,    # Ombros roll: posição inicial para elevação
#         1.5, -1.5,   # Ombros pitch: posição inicial para elevação
#         0.0, 0.0,    # Cotovelos: posição final do passo anterior
#         -1.0, -1.0   # Tornozelos: posição final do passo anterior para equilíbrio
#     ]
#     end_positions_step3 = [
#         0.0, 0.0,    # Quadris: posição ereta
#         0.0, 0.0,    # Joelhos: completamente estendidos
#         0.0, 0.0,    # Ombros roll: T-pose
#         0.0, 0.0,    # Ombros pitch: T-pose
#         0.0, 0.0,    # Cotovelos: relaxar para a posição T-pose
#         0.0, 0.0     # Tornozelos: posição de equilíbrio final na T-pose
#     ]
#     move_joints_smoothly(publishers_step3, start_positions_step3, end_positions_step3, 3)

#     rospy.loginfo("Robô levantado em T-pose.")





def levantar_de_frente():
    rospy.loginfo("Iniciando movimento de levantamento de frente...")

    # Passo 1: Girar ombro e ajustar antebraço para posição de apoio
    rospy.loginfo("Passo 1: Girando o ombro e ajustando o antebraço para apoio...")

    publishers_step1 = [
        pub_r_shoulder_pitch, pub_l_shoulder_pitch,
        pub_r_elbow, pub_l_elbow
    ]
    start_positions_step1 = [rad_to_deg(0.0), rad_to_deg(0.0), rad_to_deg(0.0), rad_to_deg(0.0)]
    end_positions_step1 = [
        rad_to_deg(-1.0), rad_to_deg(1.0),     # Ombros: girar para apoio
        rad_to_deg(-2.0), rad_to_deg(-2.0)     # Cotovelos: girar para perpendicularidade ao chão
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
        rad_to_deg(-1.0), rad_to_deg(1.0),     # Ombros: posição final do passo 1
        rad_to_deg(0.0), rad_to_deg(0.0),      # Joelhos: posição inicial
        rad_to_deg(0.0), rad_to_deg(0.0),      # Quadris: posição inicial
        rad_to_deg(0.0), rad_to_deg(0.0)       # Tornozelos: posição inicial
    ]
    end_positions_step2 = [
        rad_to_deg(2.0), rad_to_deg(-2.0),     # Ombros: estender para empurrar o chão
        rad_to_deg(1.7), rad_to_deg(1.7),      # Joelhos: dobrar para trazer o peso para frente
        rad_to_deg(1.5), rad_to_deg(1.5),      # Quadris: inclinar levemente para frente
        rad_to_deg(1.2), rad_to_deg(1.2)       # Tornozelos: inclinar para frente para auxiliar no equilíbrio
    ]
    move_joints_smoothly(publishers_step2, start_positions_step2, end_positions_step2, 2)

    rospy.sleep(3)

    # Passo 2.5: Retornar cotovelos para posição 0.0 e dobrar mais os joelhos
    rospy.loginfo("Passo 2.5: Retornando cotovelos para posição 0.0 e dobrando mais os joelhos...")

    publishers_step2_5 = [
        pub_r_elbow, pub_l_elbow,
        pub_r_knee, pub_l_knee
    ]
    start_positions_step2_5 = [
        rad_to_deg(-2.0), rad_to_deg(-2.0),     # Cotovelos: posição final do passo 2
        rad_to_deg(1.7), rad_to_deg(1.7)        # Joelhos: posição final do passo 2
    ]
    end_positions_step2_5 = [
        rad_to_deg(0.0), rad_to_deg(0.0),       # Cotovelos: retornar para posição inicial
        rad_to_deg(2.5), rad_to_deg(2.5)        # Joelhos: dobrar completamente para agachamento total
    ]
    move_joints_smoothly(publishers_step2_5, start_positions_step2_5, end_positions_step2_5, 1)

    rospy.sleep(1)

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
        rad_to_deg(1.5), rad_to_deg(1.5),    # Quadris: posição final do passo 2
        rad_to_deg(2.5), rad_to_deg(2.5),      # Joelhos: posição final do passo 2.5
        rad_to_deg(0.0), rad_to_deg(0.0),      # Ombros roll: posição inicial para elevação
        rad_to_deg(2.0), rad_to_deg(-2.0),     # Ombros pitch: posição inicial para elevação
        rad_to_deg(0.0), rad_to_deg(0.0),      # Cotovelos: posição final do passo 2.5
        rad_to_deg(1.2), rad_to_deg(1.2)       # Tornozelos: posição final do passo 2 para auxiliar no equilíbrio
    ]
    end_positions_step3 = [
        rad_to_deg(0.0), rad_to_deg(0.0),      # Quadris: posição ereta
        rad_to_deg(0.0), rad_to_deg(0.0),      # Joelhos: completamente estendidos
        rad_to_deg(0.0), rad_to_deg(0.0),      # Ombros roll: T-pose
        rad_to_deg(0.0), rad_to_deg(0.0),      # Ombros pitch: T-pose
        rad_to_deg(0.0), rad_to_deg(0.0),      # Cotovelos: relaxar para a posição T-pose
        rad_to_deg(0.0), rad_to_deg(0.0)       # Tornozelos: posição de equilíbrio final na T-pose
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
