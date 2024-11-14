#! /usr/bin/env python


import json, jsonschema
import rospy, actionlib
from itertools import combinations
import rospy
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
            "description": "Lado Para o qual o robô deve cair",
            "type": "integer",
            "default": 0
        }
    },
    "required": []
}


class Taffarel(object):
    # create messages that are used to publish feedback/result
    _feedback = TaffarelActionFeedback()
    _result = TaffarelActionResult()

    def __init__(self, name):
        rospy.loginfo(f"Starting Taffarel action server with name: {name}")

        self._action_name = name

        self._as = actionlib.SimpleActionServer(self._action_name, TaffarelAction, execute_cb=self.runAction, auto_start = False)
        
        # Publishers para as articulações do braço e pernas da Martha
        
        #self.pub_r_shoulder_pitch = rospy.Publisher('/martha/r_sho_pitch_position/command', Float64, queue_size=10)
        #self.pub_r_shoulder_roll = rospy.Publisher('/martha/r_sho_roll_position/command', Float64, queue_size=10)
        #self.pub_r_elbow = rospy.Publisher('/martha/r_el_position/command', Float64, queue_size=10)

        #self.pub_l_shoulder_pitch = rospy.Publisher('/martha/l_sho_pitch_position/command', Float64, queue_size=10)
        #self.pub_l_shoulder_roll = rospy.Publisher('/martha/l_sho_roll_position/command', Float64, queue_size=10)
        #self.pub_l_elbow = rospy.Publisher('/martha/l_el_position/command', Float64, queue_size=10)

        #self.pub_r_hip_roll = rospy.Publisher('/martha/r_hip_roll_position/command', Float64, queue_size=10)
        #self.pub_r_ankle_roll = rospy.Publisher('/martha/r_ank_roll_position/command', Float64, queue_size=10)

        #self.pub_l_hip_roll = rospy.Publisher('/martha/l_hip_roll_position/command', Float64, queue_size=10)
        #self.pub_l_ankle_roll = rospy.Publisher('/martha/l_ank_roll_position/command', Float64, queue_size=10)
        
        self.pub_arm_r = rospy.Publisher('/marta/arm_r/command', Int16MultiArray, queue_size=10)
        self.pub_arm_l_head = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray, queue_size=10)
        self.pub_right_leg = rospy.Publisher('/marta/right_leg/command', Int16MultiArray, queue_size=10)
        self.pub_left_leg = rospy.Publisher('/marta/left_leg/command', Int16MultiArray, queue_size=10)

        self._as.start()


    def validateGoal(self, goal_json):
            """
            Validates a JSON object against a predefined schema.

            Args:
                goal_json (dict): The JSON object representing the goal to be validated.

            Returns:
                
                bool: True if the JSON object is valid according to the schema, False otherwise.
                str: An empty string if validation is successful, or an error message if validation fails.

            """
            try:
                # Validate the goal JSON against the schema
                jsonschema.validate(instance=goal_json, schema=schema)
                return True, ""
            except jsonschema.exceptions.ValidationError as err:
                return False, str(err)
            
    def move_joint_smoothly(self, publisher, start_position, end_position, duration):
        #Move a articulação suavemente de start_position para end_position em 'duration' segundos.
        
        rate = 50  # Hz, número de atualizações por segundo
        steps = rate * duration  # Número total de passos para completar o movimento
        delta_position = (end_position - start_position) / steps  # Incremento por passo

        for i in range(int(steps)):
            current_position = Int16MultiArray()
            current_position.data = [0,0,0,start_position + delta_position * i,0]
            publisher.publish(current_position)
            time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização
    
    def move_joint_smoothly_r(self, publisher, start_position, end_position, duration):
        #Move a articulação suavemente de start_position para end_position em 'duration' segundos.
        
        rate = 50  # Hz, número de atualizações por segundo
        steps = rate * duration  # Número total de passos para completar o movimento
        delta_position = (end_position - start_position) / steps  # Incremento por passo

        for i in range(int(steps)):
            current_position = Int16MultiArray()
            current_position.data = [0,start_position + delta_position * i,0]
            publisher.publish(current_position)
            time.sleep(1.0 / rate)  # Espera o tempo necessário para a próxima atualização

    def CairEsquerda(self):
        # Levanta o braço esquerdo lentamente
        start_position_l_shoulder_pitch = 0.0  # Posição inicial
        end_position_l_shoulder_pitch = -2.8    # Posição final (levantado)
        duration = 2.0                         # Tempo para levantar o braço

        # Mover o braço esquerdo suavemente ao longo de 5 segundos
        self.move_joint_smoothly(self.pub_arm_r, start_position_l_shoulder_pitch, end_position_l_shoulder_pitch, duration)

        # Publicar posições fixas para as outras articulações
        self.pub_r_shoulder_roll.publish(0.0)  # Para o lado direito
        self.pub_r_elbow.publish(0.0)          # Dobra o cotovelo


        # Coloca o braço direito para baixo
        self.pub_r_shoulder_pitch.publish(0.0)
        self.pub_r_shoulder_roll.publish(0.0)
        self.pub_r_elbow.publish(0.0)
        angles_arm_r = [0,0,0]
        angles_left_leg = [0,-0.5,0,0,0,0.3]
        angles_right_leg = [0,-0.5,0,0,0,0.3]

        msg_arm_r = Int16MultiArray()
        msg_arm_r.data = angles_arm_r
        self.pub_r_arm(msg_arm_r)

        rospy.sleep(1)

        # Mover as pernas para cair para o lado esquerdo
        self.pub_l_hip_roll.publish(-0.5)
        self.pub_l_ankle_roll.publish(0.3)

        msg_left_leg = Int16MultiArray()
        msg_left_leg.data = angles_left_leg

        self.pub_r_hip_roll.publish(-0.5)
        self.pub_r_ankle_roll.publish(0.3)

        msg_right_leg = Int16MultiArray()
        msg_right_leg.data = angles_right_leg

        self.pub_r_arm(msg_arm_r)
        self.pub_left_leg(msg_left_leg)
        self.pub_right_leg(msg_right_leg)


        rospy.sleep(1)  # Espera para que as posições sejam atingidas



    def CairDireita(self):
        # Levanta o braço direito lentamente
        start_position_r_shoulder_pitch = 0.0  # Posição inicial
        end_position_r_shoulder_pitch = 2.8    # Posição final (levantado)
        duration = 2.0                         # Tempo para levantar o braço

        # Mover o braço direito suavemente ao longo de 5 segundos
        self.move_joint_smoothly_r(self.pub_arm_r, start_position_r_shoulder_pitch, end_position_r_shoulder_pitch, duration)

        # Publicar posições fixas para as outras articulações
        self.pub_r_shoulder_roll.publish(0.0)  # Para o lado direito
        self.pub_r_elbow.publish(0.0)          # Dobra o cotovelo


        # Coloca o braço esquerdo para baixo
        self.pub_l_shoulder_pitch.publish(0.0) 
        self.pub_l_shoulder_roll.publish(0.0)
        self.pub_l_elbow.publish(0.0)
        
        angles_arm_l_head = [0,0,0,0,0]
        angles_left_leg = [0,0.5,0,0,0,-0.3]
        angles_right_leg = [0,-0.5,0,0,0,0.3]

        msg_arm_l_head = Int16MultiArray()
        msg_arm_l_head.data = angles_arm_l_head
        self.pub_r_arm(msg_arm_l_head)

        rospy.sleep(1)

        # Mover as pernas para cair para o lado direito
        self.pub_r_hip_roll.publish(0.5) #2 e 6
        self.pub_r_ankle_roll.publish(-0.3)

        self.pub_l_hip_roll.publish(0.5)#8 e 12
        self.pub_l_ankle_roll.publish(-0.3)
        
        msg_left_leg = Int16MultiArray()
        msg_left_leg.data = angles_left_leg

        self.pub_r_hip_roll.publish(-0.5)
        self.pub_r_ankle_roll.publish(0.3)
        msg_right_leg = Int16MultiArray()
        msg_right_leg.data = [0,-0.5,0,0,0,0.3]

        self.pub_r_arm(msg_arm_l_head)
        self.pub_left_leg(msg_left_leg)
        self.pub_right_leg(msg_right_leg)

        rospy.sleep(1)  # Espera para que as posições sejam atingidas

    def runAction(self, goal):
        rospy.loginfo(f"Received goal: {goal.json}")

        # Parse the JSON string from the goal
        try:
            goal_data = json.loads(goal.json)
        except json.JSONDecodeError:
            rospy.logerr("Invalid JSON received")
            self._result.result.json = json.dumps({"error": "Invalid JSON format"})
            self._as.set_aborted(self._result.result)
            return
        
        # Validate the goal JSON
        is_valid, error_message = self.validateGoal(goal_data)
        if not is_valid:
            rospy.logerr("JSON validation failed: %s", error_message)
            self._result.result.json = json.dumps({"error": f"Validation failed: {error_message}"})
            self._as.set_aborted(self._result.result)
            return
        
        lado = goal_data["Lado"]

        if lado == 0:
            self.CairEsquerda()
        else:
            self.CairDireita()

        # Set the result message
        self._result.result.json = json.dumps({"result": "Task completed successfully"})
        rospy.loginfo('%s: Succeeded' % self._action_name)
        self._as.set_succeeded(self._result.result)


def main():
    rospy.init_node('taffarel_server_node')
    server = Taffarel(rospy.get_name())
    rospy.spin()

if __name__ == '__main__':
    main()