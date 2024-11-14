#!/usr/bin/env python
import rospy

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
rospy.init_node('image_pub')
rospy.loginfo('image_pub node started')
pub = rospy.Publisher('image', Image,queue_size=1)
bridge = CvBridge()
from std_msgs.msg import Bool
cap = cv2.VideoCapture(0)

def ready_callback(msg):
    ready = msg.data
    if ready == True:
        pub.publish(imgMsg)
        print('publishing')
    
while not rospy.is_shutdown():

    ret,img = cap.read()
    imgMsg = bridge.cv2_to_imgmsg(img, "bgr8")
    rospy.Subscriber("/ready",Bool , ready_callback)
    pub.publish(imgMsg)
    rospy.Rate(30).sleep() 
