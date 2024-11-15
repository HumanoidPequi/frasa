#!/usr/bin/env python3

import json
import jsonschema
import rospy
import actionlib
from std_msgs.msg import Float64, Int16MultiArray
import time
from marta_msgs.msg import TaffarelAction, TaffarelActionFeedback, TaffarelActionResult

# JSON schema
schema = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'title': 'Locality cost',
    'description': 'Compute locality cost online.',
    "type": "object",
    "properties": {
        "Lado": {
            "description": "Lado para o qual o robô deve cair",
            "type": "integer",
            "default": 0
        }
    },
    "required": []
}

class Taffarel(object):
    _feedback = TaffarelActionFeedback()
    _result = TaffarelActionResult()

    def __init__(self, name):
        rospy.loginfo(f"Starting Taffarel action server with name: {name}")
        self._action_name = name
        self._as = actionlib.SimpleActionServer(self._action_name, TaffarelAction, execute_cb=self.runAction, auto_start=False)

        # Publishers para as articulações
        self.pub_arm_r = rospy.Publisher('/marta/arm_r/command', Int16MultiArray, queue_size=10)
        self.pub_arm_l_head = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray, queue_size=10)
        self.pub_right_leg = rospy.Publisher('/marta/right_leg/command', Int16MultiArray, queue_size=10)
        self.pub_left_leg = rospy.Publisher('/marta/left_leg/command', Int16MultiArray, queue_size=10)

        self._as.start()

    def validateGoal(self, goal_json):
        try:
            jsonschema.validate(instance=goal_json, schema=schema)
            return True, ""
        except jsonschema.exceptions.ValidationError as err:
            return False, str(err)

    def move_joint_smoothly(self, publisher, start_position, end_position, duration, joint_index=0):
        rate = 50  # Hz
        steps = rate * duration
        delta_position = (end_position - start_position) / steps

        for i in range(int(steps)):
            current_position = Int16MultiArray()
            positions = [0] * 5
            positions[joint_index] = int(start_position + delta_position * i)
            current_position.data = positions
            publisher.publish(current_position)
            time.sleep(1.0 / rate)

    def CairEsquerda(self):
        # Levantar o braço esquerdo suavemente
        start_position = 0
        end_position = -280  # Posição em décimos (para compatibilidade com Int16MultiArray)
        duration = 2.0
        self.move_joint_smoothly(self.pub_arm_r, start_position, end_position, duration, joint_index=3)

        # Definir posições para pernas e outros membros
        angles_arm_r = [0, 0, 0]
        angles_left_leg = [0, -50, 0, 0, 0, 30]
        angles_right_leg = [0, -50, 0, 0, 0, 30]

        msg_arm_r = Int16MultiArray(data=angles_arm_r)
        msg_left_leg = Int16MultiArray(data=angles_left_leg)
        msg_right_leg = Int16MultiArray(data=angles_right_leg)

        self.pub_arm_r.publish(msg_arm_r)
        self.pub_left_leg.publish(msg_left_leg)
        self.pub_right_leg.publish(msg_right_leg)
        rospy.sleep(1)

    def CairDireita(self):
        rospy.loginfo("Deu bom demais!")
        # Levantar o braço direito suavemente
        start_position = 0
        end_position = 280  # Posição em décimos
        duration = 2.0
        self.move_joint_smoothly(self.pub_arm_r, start_position, end_position, duration, joint_index=1)

        # Definir posições para pernas e outros membros
        angles_arm_l_head = [0, 0, 0, 0, 0]
        angles_left_leg = [0, 50, 0, 0, 0, -30]
        angles_right_leg = [0, -50, 0, 0, 0, 30]

        msg_arm_l_head = Int16MultiArray(data=angles_arm_l_head)
        msg_left_leg = Int16MultiArray(data=angles_left_leg)
        msg_right_leg = Int16MultiArray(data=angles_right_leg)

        self.pub_arm_l_head.publish(msg_arm_l_head)
        self.pub_left_leg.publish(msg_left_leg)
        self.pub_right_leg.publish(msg_right_leg)
        rospy.sleep(1)

    def runAction(self, goal):
        rospy.loginfo(f"Received goal: {goal.json}")

        try:
            goal_data = json.loads(goal.json)
        except json.JSONDecodeError:
            rospy.logerr("Invalid JSON received")
            self._result.result.json = json.dumps({"error": "Invalid JSON format"})
            self._as.set_aborted(self._result.result)
            return

        is_valid, error_message = self.validateGoal(goal_data)
        if not is_valid:
            rospy.logerr("JSON validation failed: %s", error_message)
            self._result.result.json = json.dumps({"error": f"Validation failed: {error_message}"})
            self._as.set_aborted(self._result.result)
            return

        lado = goal_data.get("Lado", 0)

        if lado == 0:
            self.CairEsquerda()
        else:
            self.CairDireita()

        self._result.result.json = json.dumps({"result": "Task completed successfully"})
        rospy.loginfo('%s: Succeeded' % self._action_name)
        self._as.set_succeeded(self._result.result)

def action_callback(action_msg):
    rospy.loginfo("Recebido action_msg.data: %s", action_msg.data)
    # Aqui você pode adicionar a lógica para ativar a ação com base nos dados recebidos
    if action_msg.data[0] == 1:
        rospy.loginfo("Ação: Cair à Direita")
        CairDireita()
        # Adicione a lógica para ativar a ação de cair à direita
    elif action_msg.data[0] == 0:
        rospy.loginfo("Ação: Cair à Esquerda")
        # Adicione a lógica para ativar a ação de cair à esquerda

def action_listener():
    rospy.init_node('taffarel_action_node', anonymous=True)
    rospy.Subscriber('/marta/fall_action', Int32MultiArray, action_callback)
    rospy.spin()


def main():
    rospy.init_node('taffarel_server_node')
    server = Taffarel(rospy.get_name())
    rospy.spin()

if __name__ == '__main__':
    main()