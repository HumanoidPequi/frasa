#!/usr/bin/env python3

import rospy
import actionlib
from std_msgs.msg import Int16MultiArray
#from humanoid_msgs.msg import LiftAction, LiftActionFeedback, LiftActionResult
import time


def move_joints_smoothly(publisher, start_positions, end_positions, duration):
    rate = 50  # Hz
    steps = int(rate * duration)
    delta_positions = [(end - start) / steps for start, end in zip(start_positions, end_positions)]

    for step in range(steps):
        current_positions = [start + delta * step for start, delta in zip(start_positions, delta_positions)]
        publisher.publish(Int16MultiArray(data=current_positions))
        time.sleep(1.0 / rate)


class LiftActionServer:
    #_feedback = LiftActionFeedback()
    #_result = LiftActionResult()

    def __init__(self, name):
        self._action_name = name
        self._as = actionlib.SimpleActionServer(
            self._action_name,
            #LiftAction,
            execute_cb=self.execute_action,
            auto_start=False
        )

        # Publishers organizados por grupo
        self.pub_right_arm = rospy.Publisher('/marta/arm_r/command', Int16MultiArray, queue_size=10)
        self.pub_left_arm_head = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray, queue_size=10)
        self.pub_left_leg = rospy.Publisher('/marta/left_leg/command', Int16MultiArray, queue_size=10)
        self.pub_right_leg = rospy.Publisher('/marta/right_leg/command', Int16MultiArray, queue_size=10)

        self._as.start()

    def levantar_de_frente(self):
        rospy.loginfo("Iniciando movimento de levantamento de frente...")
        
        
        move_joints_smoothly(self.pub_left_arm_head, [0, 0, 0, 0, 0], [10, 10, 15, 10, 20], 2)
        move_joints_smoothly(self.pub_right_arm, [0, 0, 0], [10, 15, 20], 2)
        move_joints_smoothly(self.pub_left_leg, [0, 0, 0, 0, 0, 0], [5, 10, 15, 20, 25, 30], 3)
        move_joints_smoothly(self.pub_right_leg, [0, 0, 0, 0, 0, 0], [5, 10, 15, 20, 25, 30], 3)

        rospy.loginfo("Movimento de levantamento de frente concluído.")

    def levantar_de_tras(self):
        rospy.loginfo("Iniciando movimento de levantamento de trás...")
        
        move_joints_smoothly(self.pub_left_arm_head, [0, 0, 0, 0, 0], [10, -10, 15, -10, 20], 2)
        move_joints_smoothly(self.pub_right_arm, [0, 0, 0], [-10, -15, -20], 2)
        move_joints_smoothly(self.pub_left_leg, [0, 0, 0, 0, 0, 0], [-5, -10, -15, -20, -25, -30], 3)
        move_joints_smoothly(self.pub_right_leg, [0, 0, 0, 0, 0, 0], [-5, -10, -15, -20, -25, -30], 3)

        rospy.loginfo("Movimento de levantamento de trás concluído.")

    def execute_action(self, goal):
        rospy.loginfo(f"Recebido objetivo: {goal.mode}")
        mode = goal.mode.lower()

        if mode == "frente":
            self.levantar_de_frente()
        elif mode == "tras":
            self.levantar_de_tras()
        else:
            rospy.logerr("Modo inválido!")
            self._result.result = "Erro: Modo inválido!"
            self._as.set_aborted(self._result)
            return

        self._result.result = "Ação concluída com sucesso!"
        rospy.loginfo(f"{self._action_name}: Succeeded")
        self._as.set_succeeded(self._result)


# def main():
#     rospy.init_node('lift_action_server')
#     #server = LiftActionServer(rospy.get_name())
#     rospy.spin()
# Mantém o nó ativo
rospy.spin()
     # Escolher o movimento 
movimento = input("Digite 'frente' para levantar de frente ou 'tras' para levantar de trás: ")

if movimento == 'frente':
    levantar_de_frente()
elif movimento == 'tras':
    levantar_de_tras()
else:
    rospy.loginfo("Movimento inválido.")

#  if __name__ == '__main__':
#      try:
#          set_joint_positions()
#      except rospy.ROSInterruptException:
#          pass


if __name__ == '__main__':
    main()
