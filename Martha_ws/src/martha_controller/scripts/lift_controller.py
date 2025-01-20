#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64, Float64MultiArray
import time
def move_joints_smoothly(joints, start_positions, end_positions, duration):
    rate = 100  # Hz
    steps = rate * duration
    # Calcula o incremento por passo para cada articulação
    delta_positions = {joint: (end - start) / steps for joint, start, end in zip(joints, start_positions, end_positions)}
    current_positions = {joint: start for joint, start in zip(joints, start_positions)}
    for _ in range(int(steps)):
        for joint in joints:
            current_positions[joint] += delta_positions[joint]
            if simulation_mode:
                # Publica nos publishers individuais
                joint_publishers[joint].publish(Float64(current_positions[joint]))
            else:
                # Atualiza as posições nos arrays combinados
                array_name, index = joint_array_mapping[joint]
                arrays[array_name][index] = current_positions[joint]  # Usando valores em radianos
        if not simulation_mode:
            # Publica os arrays combinados
            for array_name in arrays:
                msg = Float64MultiArray()
                msg.data = arrays[array_name]
                array_publishers[array_name].publish(msg)
        time.sleep(1.0 / rate)
def levantar_de_tras():
    rospy.loginfo("Iniciando movimento de levantamento de costas...")
    # Fase 1: Puxar o braço para trás
    rospy.loginfo("Fase 1: Puxando o braço para trás para apoio...")
    joints_phase1 = ['r_shoulder_pitch', 'l_shoulder_pitch', 'r_elbow', 'l_elbow']
    start_positions_phase1 = [0.0, 0.0, 0.0, 0.0]
    end_positions_phase1 = [-1.5, 1.5, -1.5, -1.5]
    move_joints_smoothly(joints_phase1, start_positions_phase1, end_positions_phase1, 1)
    rospy.sleep(1)
    # Fase 2: Zerar antebraço e ajustar pernas e tornozelos
    rospy.loginfo("Fase 2: Zerando o antebraço e ajustando pernas e tornozelos...")
    joints_phase2 = ['r_elbow', 'l_elbow']
    start_positions_phase2 = [-1.5, -1.5]
    end_positions_phase2 = [0.0, 0.0]
    move_joints_smoothly(joints_phase2, start_positions_phase2, end_positions_phase2, 2)
    rospy.sleep(3)
    # Passo final: Levantar o tronco e assumir a T-pose
    rospy.loginfo("Levantando o tronco para a T-pose...")
    joints_step3 = ['r_shoulder_pitch', 'l_shoulder_pitch']
    start_positions_step3 = [-1.5, 1.5]
    end_positions_step3 = [0.0, 0.0]
    move_joints_smoothly(joints_step3, start_positions_step3, end_positions_step3, 3)
    rospy.loginfo("Robô levantado em T-pose.")

def levantar_de_frente():
    rospy.loginfo("Iniciando movimento de levantamento de frente...")
    # Passo 1: Girar ombro e ajustar antebraço para posição de apoio
    #rospy.loginfo("Passo 1: Girando o ombro e ajustando o antebraço para apoio...")
    joints_step1 = ['r_shoulder_pitch', 'l_shoulder_pitch', 'r_elbow', 'l_elbow']
    start_positions_step1 = [0.0, 0.0, 0.0, 0.0]
    end_positions_step1 = [-1.0, 1.0, -2.5, -2.5]
    move_joints_smoothly(joints_step1, start_positions_step1, end_positions_step1, 1)
    rospy.sleep(1)
    # Passo 2: Empurrar o chão, dobrar joelhos e girar tornozelos
    #rospy.loginfo("Passo 2: Empurrando o chão, dobrando joelhos e ajustando tornozelos...")
    joints_step2 = ['r_shoulder_pitch', 'l_shoulder_pitch', 'r_knee', 'l_knee', 'r_hip_pitch', 'l_hip_pitch', 'r_ankle_pitch', 'l_ankle_pitch']
    start_positions_step2 = [-1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    end_positions_step2 = [2.5, -2.5, 1.7, 1.7, -2.2, -2.2, -1.3, -1.3]
    move_joints_smoothly(joints_step2, start_positions_step2, end_positions_step2, 1)
    rospy.sleep(1)
    # Passo 2.5: Retornar cotovelos para posição 0.0 e dobrar mais os joelhos
    #rospy.loginfo("Passo 2.5: Retornando cotovelos para posição 0.0 e dobrando mais os joelhos...")
    joints_step2_5 = ['r_elbow', 'l_elbow', 'r_knee', 'l_knee', 'r_shoulder_pitch', 'l_shoulder_pitch', 'r_hip_pitch', 'l_hip_pitch', 'r_ankle_pitch', 'l_ankle_pitch']
    start_positions_step2_5 = [-2.5, -2.5, 1.7, 1.7, 2.5, -2.0, -2.0, -2.2, -1.45, -1.45]
    end_positions_step2_5 = [0.0, 0.0, 2.1, 2.1, 1.0, -1.0, -1.8, -1.8, -1.1, -1.1]
    move_joints_smoothly(joints_step2_5, start_positions_step2_5, end_positions_step2_5, 1)
    rospy.sleep(1)
     # Passo 2.: Retornar cotovelos para posição 0.0 e dobrar mais os joelhos
    #rospy.loginfo("Passo 2.8: Retornando cotovelos para posição 0.0 e dobrando mais os joelhos...")
    joints_step2_8 = ['r_knee', 'l_knee', 'r_hip_pitch', 'l_hip_pitch', 'r_ankle_pitch', 'l_ankle_pitch']
    start_positions_step2_8 = [2.1, 2.1, -1.8, -1.8, -1.1, -1.1]
    end_positions_step2_8 = [2.3, 2.3, -1.3, -1.3, -1.6, -1.6]
    move_joints_smoothly(joints_step2_8, start_positions_step2_8, end_positions_step2_8, 1)
    rospy.sleep(1)
    # Passo 2.5: Retornar cotovelos para posição 0.0 e dobrar mais os joelhos
    #rospy.loginfo("Passo 2.8: Retornando cotovelos para posição 0.0 e dobrando mais os joelhos...")
    joints_step2_9 = ['r_knee', 'l_knee', 'r_hip_pitch', 'l_hip_pitch', 'r_ankle_pitch', 'l_ankle_pitch']
    start_positions_step2_9 = [2.3, 2.3, -1.3, -1.3, -1.6, -1.6]
    end_positions_step2_9 = [2.5, 2.5, -1.0, -1.0, -2.0, -2.0]
    move_joints_smoothly(joints_step2_9, start_positions_step2_9, end_positions_step2_9, 1)
    rospy.sleep(1)
    # Passo 3: Levantar o tronco e assumir a T-pose
    #rospy.loginfo("Passo 3: Levantando o tronco para a T-pose...")
    joints_step3 = ['r_hip_pitch', 'l_hip_pitch', 'r_knee', 'l_knee', 'r_shoulder_roll', 'l_shoulder_roll', 'r_shoulder_pitch', 'l_shoulder_pitch', 'r_elbow', 'l_elbow', 'r_ankle_pitch', 'l_ankle_pitch']
    start_positions_step3 = [-1.0, -1.0, 2.5, 2.5, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0, -2.0, -2.0]
    end_positions_step3 = [-0.5, -0.5, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, -0.5]
    move_joints_smoothly(joints_step3, start_positions_step3, end_positions_step3, 1)
    #rospy.loginfo("Robô levantado em T-pose.")

def set_joint_positions():
    rospy.init_node('humanoid_lift_node', anonymous=True)
    global simulation_mode
    simulation_input = input("Digite 'y' se estiver usando a simulação, ou 'n' caso contrário: ")
    simulation_mode = (simulation_input.lower() == 'y')
    global joint_publishers, joint_array_mapping, arrays, array_publishers
    # Publishers individuais (simulação)
    joint_publishers = {}
    if simulation_mode:
        # Publishers para as articulações dos braços e pernas
        joint_publishers['r_shoulder_pitch'] = rospy.Publisher('/martha/r_sho_pitch_position/command', Float64, queue_size=10)
        joint_publishers['r_shoulder_roll'] = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)
        joint_publishers['r_elbow'] = rospy.Publisher('/martha/r_el_position/command', Float64, queue_size=10)
        joint_publishers['l_shoulder_pitch'] = rospy.Publisher('/martha/l_sho_pitch_position/command', Float64, queue_size=10)
        joint_publishers['l_shoulder_roll'] = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
        joint_publishers['l_elbow'] = rospy.Publisher('/martha/l_el_position/command', Float64, queue_size=10)
        # Publishers para as articulações do quadril, joelho e tornozelo
        joint_publishers['r_hip_pitch'] = rospy.Publisher('/martha/r_hip_pitch_position/command', Float64, queue_size=10)
        joint_publishers['r_hip_roll'] = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)
        joint_publishers['r_knee'] = rospy.Publisher('/martha/r_knee_position/command', Float64, queue_size=10)
        joint_publishers['r_ankle_pitch'] = rospy.Publisher('/martha/r_ank_pitch_position/command', Float64, queue_size=10)
        joint_publishers['l_hip_pitch'] = rospy.Publisher('/martha/l_hip_pitch_position/command', Float64, queue_size=10)
        joint_publishers['l_hip_roll'] = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
        joint_publishers['l_knee'] = rospy.Publisher('/martha/l_knee_position/command', Float64, queue_size=10)
        joint_publishers['l_ankle_pitch'] = rospy.Publisher('/martha/l_ank_pitch_position/command', Float64, queue_size=10)
        rospy.sleep(1)
    else:
        # Publishers combinados
        array_publishers = {}
        array_publishers['right_leg'] = rospy.Publisher('/marta/right_leg/command', Float64MultiArray, queue_size=10)
        array_publishers['left_leg'] = rospy.Publisher('/marta/left_leg/command', Float64MultiArray, queue_size=10)
        array_publishers['right_arm'] = rospy.Publisher('/marta/arm_r/command', Float64MultiArray, queue_size=10)
        array_publishers['left_arm_head'] = rospy.Publisher('/marta/arm_l_head/command', Float64MultiArray, queue_size=10)
        # Inicializa os arrays de posições
        arrays = {}
        arrays['right_leg'] = [0]*6
        arrays['left_leg'] = [0]*6
        arrays['right_arm'] = [0]*3
        arrays['left_arm_head'] = [0]*5
        # Mapeamento das articulações para os índices nos arrays
        joint_array_mapping = {
            'r_shoulder_pitch': ('right_arm', 0),
            'r_shoulder_roll': ('right_arm', 1),
            'r_elbow': ('right_arm', 2),
            'l_shoulder_pitch': ('left_arm_head', 2),
            'l_shoulder_roll': ('left_arm_head', 3),
            'l_elbow': ('left_arm_head', 4),
            'neck_yaw': ('left_arm_head', 0),
            'neck_pitch': ('left_arm_head', 1),
            'r_hip_pitch': ('right_leg', 2),
            'r_hip_roll': ('right_leg', 1),
            'r_knee': ('right_leg', 3),
            'r_ankle_pitch': ('right_leg', 4),
            'l_hip_pitch': ('left_leg', 2),
            'l_hip_roll': ('left_leg', 1),
            'l_knee': ('left_leg', 3),
            'l_ankle_pitch': ('left_leg', 4),
        }
        rospy.sleep(1)
    # Escolher o movimento
    movimento = input("Digite 'f' para levantar de frente ou 't' para levantar de trás: ")
    if movimento == 'f':
        levantar_de_frente()
    elif movimento == 't':
        levantar_de_tras()
    else:
        rospy.loginfo("Movimento inválido.")
if __name__ == '__main__':
    try:
        set_joint_positions()
    except rospy.ROSInterruptException:
        pass