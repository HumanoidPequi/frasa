#!/usr/bin/env python3

import rospy
import actionlib
import json
from std_msgs.msg import Int16
from marta_msgs.msg import TaffarelAction, TaffarelGoal

class TaffarelActionClient:
    def __init__(self):
        # Inicializa o nó
        rospy.init_node('taffarel_client_node')

        # Cria o cliente de action
        self.client = actionlib.SimpleActionClient('taffarel_server_node', TaffarelAction)

        # Espera o action server estar disponível
        rospy.loginfo("Esperando pelo action server 'taffarel_node'...")
        self.client.wait_for_server()
        rospy.loginfo("Action server 'taffarel_node' disponível!")

        # Configura o subscriber para receber o lado (0 para esquerda, 1 para direita)
        self.sub = rospy.Subscriber('/lado_cmd', Int16, self.callback)

    def callback(self, msg):
        # Recebe o valor do lado e chama a action
        lado = msg.data
        rospy.loginfo(f"Recebido valor de 'Lado': {lado}")

        # Cria o objetivo para a action
        goal = TaffarelGoal()
        goal_json = {"Lado": lado}
        goal.json = json.dumps(goal_json)

        rospy.loginfo(f"Enviando objetivo para o action server: {goal_json}")

        # Envia o objetivo para o servidor
        self.client.send_goal(goal)

        # Espera o resultado e imprime no log
        self.client.wait_for_result()
        result = self.client.get_result()
        rospy.loginfo(f"Resultado da action: {result.json}")

if __name__ == '__main__':
    try:
        # Inicializa o cliente de action com subscriber
        client = TaffarelActionClient()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.logerr("A execução foi interrompida.")
