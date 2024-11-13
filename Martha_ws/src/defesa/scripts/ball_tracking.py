import numpy as np
import cv2 as cv
from inference import ObjectDetection
import math as mt
import os
import time
import rospy
import yaml
import sys
from std_msgs.msg import Int16MultiArray, Float32
from sensor_msgs.msg import Imu
from tf.transformations import euler_from_quaternion

os.environ['ORT_TENSORRT_ENGINE_CACHE_ENABLE']='1'
os.environ['ORT_TENSORRT_CACHE_PATH']='/home/marta/.cache/triton-tensorrt'
# from yolofinal.utils.general import (LOGGER, check_file, check_img_size, check_imshow, check_requirements, colorstr,
#                            increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)


def imu_callback(data):
    #print(data)
    quat = [data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w]
    (roll, pitch, yaw) = euler_from_quaternion(quat)
    alpha = mt.pi/2 - pitch
    ball_distance.data = mt.tan(alpha) * h_cam
    pub_distance.publish(ball_distance)

def get_thetas(u,v):
    global theta_z, theta_y 
    # x = (v-cx)*sx
    # y = (u-cy)*sy
    x = (v-cx)
    y = (u-cy)
    theta_z = theta_z + int(np.arctan2(x,fx)*180/mt.pi) 
    #print(x,theta_x,np.arctan2(x,f))
    theta_y = theta_y + int(np.arctan2(y,fy)*180/mt.pi) 
    # if(theta_y) >= 90 or (theta_y<0):
    #     print('angulo invalido')
    #     theta_y = 0

    angles.data = [theta_z,theta_y]
    pub_angles.publish(angles)

#camera intrinsic parameters
with open('/home/dimitria/ball_tracking/ball_tracking/params2.yaml') as f:
    cam_params = yaml.load(f, Loader=yaml.FullLoader)
intrinsic = np.array(cam_params['mtx'])
print(intrinsic)
fx = intrinsic[0,0]
fy = intrinsic[1,1]
#f = 3.67 #(mm)
# sx = 3.98 * 10**(-3) #(mm)
# sy = 3.98 * 10**(-3)
cx = 320
cy = 240
global theta_z 
theta_z =   0
global theta_y 
theta_y = -50
h_cam = 68 #(cm)
euler = np.identity(3)

rospy.init_node('ball_tracking_angles', anonymous=True)
pub_angles = rospy.Publisher('/servo',Int16MultiArray, queue_size=10)
pub_distance = rospy.Publisher('ball_distance',Float32, queue_size=1)
rate = rospy.Rate(1)
angles = Int16MultiArray()
ball_distance = Float32()


# parser = argparse.ArgumentParser(description='This sample demonstrates Lucas-Kanade Optical Flow calculation. \
#                                               The example file can be downloaded from: \
#                                               https://www.bogotobogo.com/python/OpenCV_Python/images/mean_shift_tracking/slow_traffic_small.mp4')
# parser.add_argument('image', type=str, help='path to image file')
# args = parser.parse_args()

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )
# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 3,
                  criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))
# Create some random colors
color = np.random.randint(0,255,(100,3))
# Take first frame and find corners in it
Z = 0
pitch = 0

onnx_path = '/home/dimitria/ball_tracking/ball_tracking/best.onnx'
detect = ObjectDetection(onnx_path)
xx = yy = 0
tolerance = 20 #the maximum displacement tolerated to use
#optical flow to estimate ball position
old_frame = np.zeros((640,480,3))
cap = cv.VideoCapture(2)
cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
i = 0

while not rospy.is_shutdown():

    angles.data = [theta_z,theta_y]
    pub_angles.publish(angles)
    time.sleep(5)
    try:
        while (xx != cx) and (yy != cy):
            
            ret, old_frame = cap.read()
            # print(np.shape(old_frame))

            #cv.imwrite('old_frame.jpg',old_frame)
            # p0 = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params).astype('float32',casting='same_kind')
            # print(np.shape(p0))

            #detecting the ball
            #old_frame = cv.imread('/home/marta/ball_detection/blur.jpeg')
            class_ids, confidences, boxes = detect.unwrap_detection(old_frame)
            boxes = np.array(boxes)
            #print(boxes)
            if boxes != []:
                p0 = boxes[np.array(confidences).argmax()]
                p0 = np.array(p0).reshape(1,1,2).astype('float32')
                xx = p0[0,0,0]
                yy = p0[0,0,1]
                rospy.loginfo('the ball coordinate is  %f,%f', p0[0,0,0],p0[0,0,1])
            else:
                xx = cx 
                yy = cy
                p0 = np.array([xx,yy]).reshape(1,1,2).astype('float32')

            get_thetas(int(yy),int(xx))
            time.sleep(6)
    except KeyboardInterrupt:
            sys.exit(0)


        #publish theta here####################################

    #subscribe to IMU topic to read pitch and inside callback calculate z and
    rospy.Subscriber("/imu/BNO", Imu, imu_callback)
    #publishes it into a topic
    
    # print(np.shape(old_frame))
    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
    # ret, frame = cap.read()
    # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    good_new = p0
    good_old = p0
    try:
        while (good_old[0,0,0]-good_new[0,0,0] <= tolerance) and (good_old[0,0,1]-good_new[0,0,1] <= tolerance):
        # Create a mask image for drawing purposes
            
            ret,frame = cap.read()
            frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # calculate optical flow
            p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            # Select good points
            #print(p1)
            good_new = np.array(p1).reshape(1,1,2).astype('float32')
            good_old = np.array(p0).reshape(1,1,2).astype('float32')
            
            rospy.loginfo('the ball coordinate is %f,%f', good_new[0,0,0],good_new[0,0,1])
            # print(good_new,good_old)
            if good_new.any():
            # if (xx != cx) or (yy!= cy):
                get_thetas(int(good_new[0,0,0]),int(good_new[0,0,1]))
            old_gray = frame_gray.copy()
            p0 = good_new
            rospy.Subscriber("/imu/BNO", Imu, imu_callback)
    except KeyboardInterrupt:
        sys.exit(0)

        #     ser.write(bytes(str(theta_y)+'y', 'utf-8'))
        #     time.sleep(0.15)
        #     ser.write(bytes(str(-theta_x)+'x', 'utf-8'))
        #     print(theta_x,theta_x,'theeeeeeta')


        #     # break
            
            
            
        #     #print(theta_x,theta_y)
        #     #break
        #     # print("ok")

        #     print(theta_y,theta_x,"theeeeeeeeeeeeeeta")
        #     cxx = mt.cos(-theta_x*np.pi/180)
        #     sxx = mt.sin(-theta_x*np.pi/180)
        #     cyy = mt.cos(theta_y*np.pi/180)
        #     syy = mt.sin(theta_y*np.pi/180)
        #     euler = np.array([[cxx*cyy, -sxx,cxx*syy],[sxx*cyy,cxx,sxx*syy]
        #                             ,[-syy,0,cyy]])@euler
        #     pitch = np.arctan2(-euler[2,0],mt.sqrt(euler[2,1]**2+euler[2,2]**2))
        #     # pitch = pitch + theta_y*np.pi/180
        # # if p1 == :
        # if theta_y == 0:
        #     Z = get_3D(pitch)


        #     print(Z,pitch,'zzzzzzzzzz')

    #     #break
    #     #depois publicamos esses valores nos servos, então calculamos as coordenadas 3D
    
    # #depois que a bola está alinhada ao centro da câmera, calculamos as coordenadas 3D da bola

    

    # draw the tracks
    # for i,(new,old) in enumerate(zip(good_new, good_old)):
    #     a,b = new.ravel()
    #     c,d = old.ravel()
    #     mask = cv.line(mask, (a,b),(c,d), color[i].tolist(), 2)
    #     frame = cv.circle(frame,(a,b),5,color[i].tolist(),-1)
    #     frame = cv.circle(frame,(int(cx),int(cy)), 15, (0,0,255), -1)
    #     cv.putText(img=frame,text=str(Z), org=(int(xx), int(yy)), fontFace=cv.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=1, color=(255,255,0), 
    #     thickness=3)
    # img = cv.add(frame,mask)
    # cv.imshow('frame',img)
    # k = cv.waitKey(30) & 0xff
    # if k == 27:
    #     break
    # Now update the previous frame and previous points
        # old_gray = frame_gray.copy()
        # p0 = good_new.reshape(-1,1,2)

    rate.sleep()
