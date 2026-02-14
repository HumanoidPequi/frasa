import rospy
import numpy as np
from std_msgs.msg import Float32, Int16MultiArray

kick = rospy.Publisher("/ball_tracking", Int16MultiArray, queue_size=1)
angle_kick = Int16MultiArray()

limite = -13.0
limite32 = np.float32(limite)
stop_publishing = False

def kick_callback(data):
    valor_recebido = np.float32(data.data)  # Converta o valor recebido para np.float32
    if valor_recebido > limite32:
        rospy.loginfo("A distância está maior que -13.0")
        angle_kick.data = [0, -50]
        kick.publish(angle_kick)
        
    else:
        rospy.loginfo("A distância não está maior que -13.0")

def kick_sub():
    rospy.Subscriber("ball_distance", Float32, kick_callback)
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node("kick", anonymous=True)
    kick_sub()
