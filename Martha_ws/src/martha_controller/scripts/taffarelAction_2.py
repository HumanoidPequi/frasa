#!/usr/bin/env python3

import json, jsonschema
import rospy, actionlib
import time
from std_msgs.msg import Int16MultiArray
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

# Joint indices mapping for clarity
RIGHT_ARM_JOINTS = {
    0: 'r_sho_pitch',
    1: 'r_sho_roll',
    2: 'r_el'
}

LEFT_ARM_HEAD_JOINTS = {
    0: 'head_yaw',
    1: 'head_pitch',
    2: 'l_sho_pitch',
    3: 'l_sho_roll',
    4: 'l_el'
}

RIGHT_LEG_JOINTS = {
    0: 'r_hip_yaw',
    1: 'r_hip_roll',
    2: 'r_hip_pitch',
    3: 'r_knee_pitch',
    4: 'r_ank_pitch',
    5: 'r_ank_roll'
}

LEFT_LEG_JOINTS = {
    0: 'l_hip_yaw',
    1: 'l_hip_roll',
    2: 'l_hip_pitch',
    3: 'l_knee_pitch',
    4: 'l_ank_pitch',
    5: 'l_ank_roll'
}

def convert_command_degree(degrees):
    # Convert degrees to robot units (assuming 11.3777777778 ticks per degree)
    conversion_factor = 11.3777777778
    return int(degrees * conversion_factor)

class BodyPart:
    def __init__(self, name, topic, joint_count):
        self.name = name
        self.publisher = rospy.Publisher(topic, Int16MultiArray, queue_size=10)
        self.command = Int16MultiArray()
        self.command.data = [0] * joint_count  # Initialize joint positions

    def set_positions(self, positions):
        if len(positions) != len(self.command.data):
            rospy.logerr(f"Incorrect number of joint positions for {self.name}")
            return
        self.command.data = positions
        self.publisher.publish(self.command)

    def move_joints_smoothly(self, start_positions, end_positions, duration):
        rate = 50  # Hz
        steps = int(rate * duration)
        delta_positions = [(end - start) / steps for start, end in zip(start_positions, end_positions)]

        for step in range(steps):
            current_positions = [int(start + delta * step) for start, delta in zip(start_positions, delta_positions)]
            self.set_positions(current_positions)
            rospy.sleep(1.0 / rate)

class Taffarel(object):
    # create messages that are used to publish feedback/result
    _feedback = TaffarelActionFeedback()
    _result = TaffarelActionResult()

    def __init__(self, name):
        rospy.loginfo(f"Starting Taffarel action server with name: {name}")

        self._action_name = name

        self._as = actionlib.SimpleActionServer(self._action_name, TaffarelAction, execute_cb=self.runAction, auto_start=False)

        # Publishers for the arms and legs of Marta
        self.pub_r_arm = rospy.Publisher('/marta/arm_r/command', Int16MultiArray, queue_size=10)
        self.pub_l_head = rospy.Publisher('/marta/arm_l_head/command', Int16MultiArray, queue_size=10)
        self.pub_r_leg = rospy.Publisher('/marta/right_leg/command', Int16MultiArray, queue_size=10)
        self.pub_l_leg = rospy.Publisher('/marta/left_leg/command', Int16MultiArray, queue_size=10)

        # Initialize BodyPart instances
        self.right_arm = BodyPart('right_arm', '/marta/arm_r/command', joint_count=3)
        self.left_arm_head = BodyPart('left_arm_head', '/marta/arm_l_head/command', joint_count=5)
        self.right_leg = BodyPart('right_leg', '/marta/right_leg/command', joint_count=6)
        self.left_leg = BodyPart('left_leg', '/marta/left_leg/command', joint_count=6)

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

    def CairEsquerda(self):
        # Lift left arm slowly
        start_position_l_arm = [0] * 5  # Initial positions
        end_position_l_arm = [0] * 5    # Target positions
        end_position_l_arm[2] = convert_command_degree(-160)  # l_sho_pitch
        duration = 2.0  # Time to lift the arm

        # Move the left arm smoothly over the duration
        self.left_arm_head.move_joints_smoothly(
            start_positions=start_position_l_arm,
            end_positions=end_position_l_arm,
            duration=duration
        )

        # Lower right arm
        right_arm_positions = [0] * 3  # All joints to 0
        self.right_arm.set_positions(right_arm_positions)

        rospy.sleep(1)

        # Move legs to fall to the left
        left_leg_positions = [0] * 6
        right_leg_positions = [0] * 6

        # Set specific joint positions for falling
        left_leg_positions[1] = convert_command_degree(-28.6)   # l_hip_roll
        left_leg_positions[5] = convert_command_degree(17.2)    # l_ank_roll

        right_leg_positions[1] = convert_command_degree(-28.6)  # r_hip_roll
        right_leg_positions[5] = convert_command_degree(17.2)   # r_ank_roll

        self.left_leg.set_positions(left_leg_positions)
        self.right_leg.set_positions(right_leg_positions)

        rospy.sleep(1)

    def CairDireita(self):
        # Lift right arm slowly
        start_position_r_arm = [0] * 3  # Initial positions
        end_position_r_arm = [0] * 3    # Target positions
        end_position_r_arm[0] = convert_command_degree(160)  # r_sho_pitch
        duration = 2.0  # Time to lift the arm

        # Move the right arm smoothly over the duration
        self.right_arm.move_joints_smoothly(
            start_positions=start_position_r_arm,
            end_positions=end_position_r_arm,
            duration=duration
        )

        # Lower left arm
        left_arm_positions = [0] * 5  # All joints to 0
        self.left_arm_head.set_positions(left_arm_positions)

        rospy.sleep(1)

        # Move legs to fall to the right
        left_leg_positions = [0] * 6
        right_leg_positions = [0] * 6

        # Set specific joint positions for falling
        left_leg_positions[1] = convert_command_degree(28.6)    # l_hip_roll
        left_leg_positions[5] = convert_command_degree(-17.2)   # l_ank_roll

        right_leg_positions[1] = convert_command_degree(28.6)   # r_hip_roll
        right_leg_positions[5] = convert_command_degree(-17.2)  # r_ank_roll

        self.left_leg.set_positions(left_leg_positions)
        self.right_leg.set_positions(right_leg_positions)

        rospy.sleep(1)

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
    rospy.init_node('taffarel_node')
    server = Taffarel(rospy.get_name())
    rospy.spin()

if __name__ == '__main__':
    main()
