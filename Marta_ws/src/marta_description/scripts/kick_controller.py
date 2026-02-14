#!/usr/bin/env python
import rospy
from std_msgs.msg import Float64
import time
import math

class HumanoidKick:
    def __init__(self):
        rospy.init_node('humanoid_kick_node', anonymous=True)
        self.rate = rospy.Rate(10)  # Frequência de publicação em Hz

        # Inicialização dos publicadores das juntas
        self.init_publishers()

    def init_publishers(self):
        # Publicadores para as juntas necessárias
        self.pub_l_hip_roll = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
        self.pub_r_hip_roll = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)

        self.pub_l_hip_pitch = rospy.Publisher('/martha/l_hip_pitch_position/command', Float64, queue_size=10)
        self.pub_l_hip_yaw= rospy.Publisher('/martha/l_hip_yaw_position/command', Float64, queue_size=10)
        self.pub_r_hip_pitch = rospy.Publisher('/martha/r_hip_pitch_position/command', Float64, queue_size=10)

        self.pub_l_knee = rospy.Publisher('/martha/l_knee_position/command', Float64, queue_size=10)
        self.pub_r_knee = rospy.Publisher('/martha/r_knee_position/command', Float64, queue_size=10)

        self.pub_l_ank_pitch = rospy.Publisher('/martha/l_ank_pitch_position/command', Float64, queue_size=10)
        self.pub_r_ank_pitch = rospy.Publisher('/martha/r_ank_pitch_position/command', Float64, queue_size=10)

        self.pub_l_ank_roll = rospy.Publisher('/martha/l_ank_roll_position/command', Float64, queue_size=10)
        self.pub_r_ank_roll = rospy.Publisher('/martha/r_ank_roll_position/command', Float64, queue_size=10)

        # Publicadores para compensação do tronco
        self.pub_l_sho_roll = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
        self.pub_r_sho_roll = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)

    def kick(self, leg='right'):
        if leg == 'right':
            self.kick_right_leg()
        elif leg == 'left':
            self.kick_left_leg()
        else:
            rospy.logerr("Leg must be 'right' or 'left'.")

    # def kick_right_leg(self):
    #     rospy.loginfo("Iniciando chute com a perna direita.")

    #     # Passo 1: Transferir o peso para a perna esquerda
    #     rospy.loginfo("Transferindo peso para a perna esquerda.")
    #     self.pub_l_hip_roll.publish(Float64(data=math.radians(25)))  # Inclinar o quadril esquerdo para a esquerda
    #     self.pub_r_hip_roll.publish(Float64(data=math.radians(50)))  # Levantar quadril direito
    #     self.pub_l_sho_roll.publish(Float64(data=math.radians(50)))   # Inclinar o ombro esquerdo para a direita
    #     self.pub_r_sho_roll.publish(Float64(data=math.radians(50)))  # Inclinar o ombro direito para a esquerda
    #     time.sleep(1)  # Esperar para estabilizar

    #     # Passo 2: Levantar a perna direita
    #     rospy.loginfo("Levantando a perna direita.")
    #     self.pub_r_hip_pitch.publish(Float64(data=-0.5))  # Levantar coxa
    #     self.pub_r_knee.publish(Float64(data=0.5))        # Dobrar joelho
    #     self.pub_r_ank_pitch.publish(Float64(data=0.0))   # Ajustar tornozelo
    #     time.sleep(1)

    #     # Passo 3: Movimento de chute
    #     rospy.loginfo("Executando o chute.")
    #     self.pub_r_knee.publish(Float64(data=-0.2))       # Estender joelho rapidamente
    #     time.sleep(0.5)

    #     # Passo 4: Retornar a perna direita
    #     rospy.loginfo("Retornando a perna direita à posição inicial.")
    #     self.pub_r_knee.publish(Float64(data=0.0))
    #     self.pub_r_hip_pitch.publish(Float64(data=0.0))
    #     time.sleep(1)

    #     # Passo 5: Recentralizar o centro de massa
    #     rospy.loginfo("Recentralizando o centro de massa.")
    #     self.pub_l_hip_roll.publish(Float64(data=0.0))
    #     self.pub_r_hip_roll.publish(Float64(data=0.0))
    #     self.pub_l_sho_roll.publish(Float64(data=0.0))
    #     self.pub_r_sho_roll.publish(Float64(data=0.0))
    #     time.sleep(1)

    #     rospy.loginfo("Chute com a perna direita concluído.")

    def smooth_move(self, publisher, start_angle, end_angle, duration):
        # Número de passos para a transição suave
        steps = 50
        rate = rospy.Rate(steps / duration)  # Define a taxa para a duração desejada
        step_size = (end_angle - start_angle) / steps

        for step in range(steps):
            current_angle = start_angle + step * step_size
            publisher.publish(Float64(data=current_angle))
            rate.sleep()  # Espera para a próxima iteração, respeitando a taxa definida

    def kick_left_leg(self):
        rospy.loginfo("Iniciando chute com a perna esquerda.")

        # Passo 1: Transferir o peso para a perna direita suavemente
        rospy.loginfo("Transferindo peso para a perna direita suavemente.")
        
        # Movimentação suave dos ombros e quadris
        self.smooth_move(self.pub_r_sho_roll, 0.0, math.radians(45), 2.0)  # Inclinar ombro direito para a esquerda em 2 segundos
        self.smooth_move(self.pub_l_sho_roll, 0.0, math.radians(-45), 2.0)  # Inclinar ombro esquerdo para a direita em 2 segundos

        self.smooth_move(self.pub_r_hip_roll, 0.0, math.radians(-10), 1.0)   # Inclinar quadril direito para a direita em 1 segundo
        self.smooth_move(self.pub_r_ank_roll, 0.0, math.radians(15), 1.0)   # Inclinar tornozelo direito para a direita em 1 segundo
        self.smooth_move(self.pub_l_hip_roll, 0.0, math.radians(10), 1.0)   # Levantar quadril esquerdo em 1 segundo

        # Tempo extra para estabilizar
        time.sleep(1)

        # Passo 2: Levantar a perna esquerda suavemente
        rospy.loginfo("Levantando a perna esquerda suavemente.")
        
        # Movimentação suave da perna esquerda (quadril, joelho e tornozelo)
        self.smooth_move(self.pub_l_hip_roll, 0.0, math.radians(45), 2)  # Levantar coxa pro lado em 1.5 segundos
        self.smooth_move(self.pub_l_hip_pitch, 0.0, math.radians(90), 1.5)  # Levantar coxa suavemente em 1.5 segundos
        self.smooth_move(self.pub_l_knee, 0.0, math.radians(45), 1.5)       # Dobrar joelho suavemente em 1.5 segundos
        self.smooth_move(self.pub_l_hip_yaw, 0.0, math.radians(25), 1.5)  # Volta a coxa  em 1.5 segundos

        # Recentralizar o centro de massa
        rospy.loginfo("Recentralizando o centro de massa.")
        self.pub_r_hip_roll.publish(data=math.radians(10))
        self.pub_l_hip_roll.publish(data=math.radians(10))
        self.pub_r_sho_roll.publish(data=math.radians(10))
        self.pub_l_sho_roll.publish(data=math.radians(10))
        time.sleep(1)

        rospy.loginfo("Chute com a perna esquerda concluído.")

    # def kick_left_leg(self):
    #     rospy.loginfo("Iniciando chute com a perna esquerda.")

    #     # Passo 1: Transferir o peso para a perna direita
    #     rospy.loginfo("Transferindo peso para a perna direita.")
    #     self.pub_r_sho_roll.publish(data=math.radians(45))  # Inclinar o ombro direito para a esquerda
    #     self.pub_l_sho_roll.publish(data=math.radians(-45))   # Inclinar o ombro esquerdo para a direita
    #     time.sleep(2)  # Esperar para estabilizar
    #     self.pub_r_hip_roll.publish(data=math.radians(10))   # Inclinar o quadril direito para a direita
    #     self.pub_l_hip_roll.publish(data=math.radians(10))   # Levantar quadril esquerdo
    #     time.sleep(1)  # Esperar para estabilizar

    #     # #Passo 2: Levantar a perna esquerda
    #     rospy.loginfo("Levantando a perna esquerda.")
    #     self.pub_l_hip_pitch.publish(data=math.radians(30))  # Levantar coxa
    #     self.pub_l_knee.publish(data=math.radians(30))        # Dobrar joelho
        # time.sleep(1)
        # rospy.loginfo("Levantando a perna esquerda.-parte 2")
        # self.pub_l_hip_pitch.publish(data=math.radians(-25))  # Levantar coxa
        # self.pub_l_knee.publish(data=math.radians(25))        # Dobrar joelho
        # self.pub_l_ank_pitch.publish(data=math.radians(5))   # Ajustar tornozelo
        # time.sleep(1)

        # # Passo 3: Movimento de chute
        # rospy.loginfo("Executando o chute.")
        # self.pub_l_knee.publish(data=math.radians(-11))       # Estender joelho rapidamente
        # time.sleep(0.5)

        # # Passo 4: Retornar a perna esquerda
        # rospy.loginfo("Retornando a perna esquerda à posição inicial.")
        # self.pub_l_knee.publish(Float64(data=0.0))
        # self.pub_l_hip_pitch.publish(Float64(data=0.0))
        # time.sleep(1)

        # # Passo 5: Recentralizar o centro de massa
        # rospy.loginfo("Recentralizando o centro de massa.")
        # self.pub_r_hip_roll.publish(data=math.radians(10))
        # self.pub_l_hip_roll.publish(data=math.radians(10))
        # self.pub_r_sho_roll.publish(data=math.radians(10))
        # self.pub_l_sho_roll.publish(data=math.radians(10))
        # time.sleep(1)

        # rospy.loginfo("Chute com a perna esquerda concluído.")

    def run(self):
        while not rospy.is_shutdown():
            #self.kick(leg='right')  # Chutar com a perna direita
            #time.sleep(2)           # Pausa entre os chutes
            self.kick(leg='left')   # Chutar com a perna esquerda
            time.sleep(2)

if __name__ == '__main__':
    try:
        humanoid_kick = HumanoidKick()
        humanoid_kick.run()
    except rospy.ROSInterruptException:
        pass

#mov = [[20 valores],[],[],[]]
# for i in range(0, 19):
#    rospy.pub_sub(mov[i][])

#o que fazer: a matriz mov deve ser preenchida com os valores de cada movimento, com um numero de "frames que eu definirei
# e depois, o robo deve executar cada movimento, um por um, com um delay de 0.5s entre cada movimento
# e também trocar a publicação de tópicos separados por uma lista com os valores de cada movimento"
