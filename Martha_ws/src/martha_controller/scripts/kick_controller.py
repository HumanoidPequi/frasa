#!/usr/bin/env python

import rospy
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Header, Bool
import math

class KickController:
    def __init__(self):
        rospy.init_node('kick_controller', anonymous=True)

        
        self.kick_sub = rospy.Subscriber('/kick_command', Bool, self.kick_callback)
        self.pub = rospy.Publisher('/humanoid/joint_trajectory_controller/command', JointTrajectory, queue_size=10)

        
        self.thigh_length = 0.4  # Comprimento da coxa 
        self.shin_length = 0.4   # Comprimento da perna 

        # Perna direita
        self.joint_names = ['r_hip_yaw_link', 'r_hip_roll_link', 'r_hip_pitch_link', 'r_knee_link']

    def kick_callback(self, data):
        if data.data:
            
            target_position = [0.3, -0.5]  # Exemplo de coordenadas alvo para o pé
            joint_angles = self.inverse_kinematics(target_position)
            self.perform_kick(joint_angles)

    def inverse_kinematics(self, target_position):
        x, y = target_position

        # Calcular a distância até o ponto alvo
        distance = math.sqrt(x**2 + y**2)

        # Verificar se o alvo está dentro do alcance da perna
        if distance > (self.thigh_length + self.shin_length):
            raise ValueError("Target position is out of reach")

        # Lei dos Cossenos para calcular o ângulo do joelho
        cos_knee_angle = (x**2 + y**2 - self.thigh_length**2 - self.shin_length**2) / (2 * self.thigh_length * self.shin_length)
        knee_angle = math.acos(cos_knee_angle)

        # Lei dos Cossenos para calcular o ângulo do quadril
        alpha = math.atan2(y, x)
        cos_hip_angle = (x**2 + y**2 + self.thigh_length**2 - self.shin_length**2) / (2 * self.thigh_length * distance)
        hip_angle = alpha - math.acos(cos_hip_angle)

        # Consideração para ângulo do quadril em Yaw e Roll (aproximado)
        hip_yaw_angle = 0.0  # Ajuste este valor se precisar de rotação no eixo Yaw
        hip_roll_angle = 0.0  # Ajuste este valor para controlar a rotação lateral

        return [hip_yaw_angle, hip_roll_angle, hip_angle, knee_angle]

    def move_to_position(self, joint_angles, duration):
        trajectory = JointTrajectory()
        trajectory.header = Header()
        trajectory.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = joint_angles
        point.time_from_start = rospy.Duration(duration)

        trajectory.points = [point]
        self.pub.publish(trajectory)

    def perform_kick(self, joint_angles):
        rospy.loginfo("Starting kick sequence")

        # Posição de equilíbrio inicial
        balance_positions = [0.0, 0.0, 0.0, 0.0]
        self.move_to_position(balance_positions, 1.0)
        rospy.sleep(1.0)

        # Executar o chute com os ângulos calculados
        self.move_to_position(joint_angles, 1.0)
        rospy.sleep(1.0)

        # Retornar à posição inicial após o chute
        self.move_to_position(balance_positions, 1.0)
        rospy.sleep(1.0)

        rospy.loginfo("Kick sequence complete")

