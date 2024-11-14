#! /usr/bin/env python3

import numpy as np
import cv2 as cv
from inference import ObjectDetection
from yolo_utils import nms, draw_detections
import math as mt
import os
import time
import rospy
import yaml
import sys
from image_thread import Image_thread
import warnings
warnings.filterwarnings("ignore")
from sensor_msgs.msg import Image, CompressedImage
# ROS Image message -> OpenCV2 image converter
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Int16MultiArray, Float32, Float32MultiArray
from sensor_msgs.msg import Imu
#from tf.transformations import euler_from_quaternion

import signal

#parametros do onnx para criar o cache do tensorrt
os.environ['ORT_TENSORRT_ENGINE_CACHE_ENABLE']='1'
os.environ['ORT_TENSORRT_CACHE_PATH']='/home/marta/.cache/triton-tensorrt'

bridge = CvBridge() #Convert your ROS Image message to OpenCV2

def handle_ctrl_c(signum, frame):
        # Este método será chamado quando você pressionar Ctrl+C
        # Aqui você pode executar o comando kill -9 para matar o processo
        print("Recebido o sinal SIGINT (Ctrl+C). Matando o processo...")
        # Use subprocess para executar o comando kill -9 com o ID do processo
        import subprocess
        process_id = os.getpid()  # Obter o ID do processo atual
        subprocess.call(["kill", "-9", str(process_id)])

class Ball_tracking():

    def __init__(self) -> None:
        with open('/home/marta/Documentos/ball_tracking/ball_tracking/params2.yaml') as f:
            cam_params = yaml.load(f, Loader=yaml.FullLoader)
        self.intrinsic = np.array(cam_params['mtx'])
        #print(intrinsic)
        self.fx = self.intrinsic[0,0]
        self.fy = self.intrinsic[1,1]
        self.cx = 320
        self.cy = 240
        self.mask = np.zeros((480,640,3)).astype('uint8') #mask to draw the optical flow


        self.theta_z =   0 #yaw

        self.theta_y = -50 #pitch
        self.h_cam = 62 #(cm)
        #imu
        self.euler = np.identity(3) #rotation matrix
        self.draw_optical = True #draw the optical flow

        rospy.init_node('ball_tracking_node', anonymous=True)
        self.pub_angles = rospy.Publisher('/ball_tracking',Int16MultiArray, queue_size=1)
        self.pub_ball_pos = rospy.Publisher('/ball_pose', Float32MultiArray,queue_size=1) #publish the ball position
        #só vamos usar esse ^
        self.pub_freq = rospy.Publisher('frequency',Float32, queue_size = 1)
        self.pub_image = rospy.Publisher('image', Image,queue_size = 1)
       
        self.pub_optical_flow = rospy.Publisher('flux_opt', Float32MultiArray, queue_size = 1)
       
        self.rate = rospy.Rate(5) #taxa de publicação com a qual o código vai rodar
        self.angles = Int16MultiArray()
        self.freq = Float32()
        
        self.opt_flux = Float32MultiArray()
        
        #self.ball_distance = Float32()
        self.lk_params = dict( winSize  = (15,15), #tamanho da região que ele vai usar para calcular a derivada
                        maxLevel = 7, #número de níveis da pirâmide
                        criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03)) #critérios de parada
        
        self.onnx_path = '/home/marta/Documentos/ball_tracking/ball_tracking/nano_480.onnx'
        self.detect = ObjectDetection(self.onnx_path)
        self.i = 0 #contador pra monitorar quantas vezes vai rodar a yolo e o optical flow
        self.yolo = True #se a yolo vai rodar ou não, se ela for False vai rodar o optical flow
        self.ball_position = Float32MultiArray()
        self.img_msg = Image() #instancia o objeto imagem do ros

        self.img_thread = Image_thread()
        self.img_thread.start()
        self.img_queue = self.img_thread.info #vai ter só uma posição, que é a imagem e toda vez que tem uma imagem nova ele tira a antiga e atualiza a fila pra colocar a nova
        #time.sleep(5) #espera 5 segundos pra começar a rodar o código pra dar tempo pro dynamixel ir pra posicao inicial

    def points(self,p0): #pega o ponto central do bounding box e cria uma matriz de pontos em volta dele com um quadrado 60x60. nao sao aleatorios
        yi = int(p0[1])-30 #esse p0 é o ponto central do bounding box, detectado pela yolo, em x e y
        xi = int(p0[0])-30
        points = []
        for i in range(yi,yi + 60):
            for j in range(xi,xi+60):
                points.append([j,i])
        return np.array(points).reshape(len(points),1,2).astype('float32')
    
#callback vai ser executado toda vez que o subscriber recebe uma mensagem. 
#subscriber vai subscrever no tópico
    def image_callback(self, image): #função que vai rodar toda vez que tiver uma imagem nova. quando chegar a imagem, o callback sera executado


        #global image
        #print("Received an image!")

        #Convert your ROS Image message to OpenCV2
        #image = bridge.imgmsg_to_cv2(msg, "bgr8")


        if self.yolo == True:
            start = time.perf_counter() #começa a contar o tempo de execução da yolo
            #old_frame = image
            # print(np.shape(old_frame))

            #cv.imwrite('old_frame.jpg',old_frame)
            # p0 = cv.goodFeaturesToTrack(old_gray, mask = None, **feature_params).astype('float32',casting='same_kind')
            # print(np.shape(p0))

            #detecting the ball
            #old_frame = cv.imread('/home/marta/ball_detection/blur.jpeg')
            class_ids, confidences, boxes = self.detect.unwrap_detection(image)

            # indexes = nms(np.squeeze(boxes), confidences, detect.IOU_THRESHOLD)
            # boxes = np.array(boxes)
            #print(boxes)
            if boxes != []:
                p0 = boxes[np.array(confidences).argmax()]
                #print(p0)
                
                xx = p0[0]
                yy = p0[1]

                img_detect = draw_detections(image, boxes, confidences, class_ids, mask_alpha=0.3)
                imgMsg = bridge.cv2_to_imgmsg(img_detect, "bgr8")
                rospy.loginfo('(yolo) the ball coordinates are  %f,%f', xx, yy)#ólives was here
                self.ball_position.data = [xx,yy] #pega os dados da posicao da bola
                self.pub_ball_pos.publish(self.ball_position) #e publica essa posicao num topico do ros
                self.i = self.i + 1
                if self.i == 2: 
                    #if abs(xx - self.cx) > 25 or abs(yy-self.cy >20):
                        
                    #self.get_thetas(int(yy),int(xx))
                    #self.i =0
                    #ultimo frame q ele fez a deteccao
                    self.old_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #ta armazenando o frame anterior pra usar no optical flow
                    #self.good_old = np.array([xx,yy]).reshape(1,1,2).astype('float32')
                    self.good_old = self.points(np.array([xx,yy])) #pega a regiao em volta da ultima coordenada da bola da yolo
                    self.yolo = False

            
                
                # if self.i == 0:
                #     self.i = 1

            else: #quando nao tem deteccao, ele olha pra baixo e pro meio
                xx = 1000
                yy = 1000
                #self.good_old = np.array([xx,yy]).reshape(1,1,2).astype('float32')
                self.ball_position.data = [xx,yy]
                self.pub_ball_pos.publish(self.ball_position)
                #self.angles.data = [0,-50]
                #self.pub_angles.publish(self.angles)
                #imgMsg = bridge.cv2_to_imgmsg(image, "bgr8")

                    
                    #print(image)
        
            end = (time.perf_counter() - start)
            #rospy.loginfo("(yolo) Pipeline time: %f s", end)
            self.freq.data = 1/end
            self.pub_freq.publish(self.freq)
        else: #se a yolo for false, ele vai rodar o optical flow
            
            # ret, frame = cap.read()
            # frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    
        
            # Create a mask image for drawing purposes
                
            start = time.perf_counter()
            frame_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) #imagem/frame atual
            # calculate optical flow
            p1, st, err = cv.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.good_old, None, **self.lk_params)
            #p1 é a posicao de todos os pontos da janela em torno do ponto central
            # Select good points
            #print(p1)
            self.good_new = np.mean(np.array(p1),axis=0).reshape(1,1,2).astype('float32') #media das coordenadas dos pontos da janela, pra me dar so uma posicao
            #good_old = np.array(self.p0).reshape(1,1,2).astype('float32')
            end = (time.perf_counter() - start)
            #rospy.loginfo("(optical flow) Pipeline time: %f s", end)
            self.freq.data = 1/end
            self.pub_freq.publish(self.freq)
            #rospy.loginfo('(optical flow) the ball coordinate are %f,%f', self.good_new[0,0,0],self.good_new[0,0,1])
            # print(good_new,good_old)
            #p1 - p0 vai dar o vetor pra onde o opt flow tá apontando
            if self.good_new.any(): #se tiver alguma ponto
                   
            # if (xx != cx) or (yy!= cy):
                self.ball_position.data = [self.good_new[0,0,0],self.good_new[0,0,1]]
                self.pub_ball_pos.publish(self.ball_position) #publica a posicao da bola no frame atual
                #self.get_thetas(int(self.good_new[0,0,0]),int(self.good_new[0,0,1]))
                if self.draw_optical == True:
                    #se draw_optical for true, ele vai desenhar o optical flow
                    color = [[0,0,255]]
                    for i, (new, old) in enumerate(zip(self.good_new, self.good_old)):
                        a, b = new.ravel()
                        c, d = old.ravel()
                        px = new - old
                        mag, ang = cv.cartToPolar(new, old)
                        angulo = Float32MultiArray()
                        #angulo.data = np.tolist()
                        ang_aux = ang[0] * 180 / np.pi
                        #angulo.data = ang * 180 / np.pi
                        angulo.data = ang_aux
                        #angulo.data = list(angulo.data)
                        # angulo = float(angulo)
                        print('angulo',angulo.data)
                        #print(type(angulo.data))
                        #self.opt_flux.data = ang
                        self.pub_optical_flow.publish(angulo) #dreca was here

                        #print(type(px))
                        #new - old
                        self.mask = cv.line(self.mask, (int(a), int(b)), (int(c), int(d)), color[i], 2)
                        image = cv.circle(image, (int(a), int(b)), 5, color[i], -1)
                    #img = cv.add(image, self.mask)
                    
                    #self.img_msg.header.stamp = rospy.Time.now()
                    #self.img_msg.format = "jpeg"
                    #self.img_msg.data = np.array(cv.imencode('.jpg', img)[1]).tostring()
                    img_msg = bridge.cv2_to_imgmsg(img, "bgr8")
                    # Publish new image
                    self.pub_image.publish(img_msg)
            self.i = self.i +1
            #if (self.good_old[0,0,0]-self.good_new[0,0,0] >= self.tolerance) and (self.good_old[0,0,1]-self.good_new[0,0,1] >= self.tolerance):

            if self.i == 7 :
                self.yolo = True
                self.i = 0
            else: #vai fazendo o optical flow ate dar i=7
                self.old_gray = frame_gray.copy()
                self.good_old = self.points([self.good_new[0,0,0],self.good_new[0,0,1]]) #self.good_new
    
        return




    # def imu_callback(data):
    #     #print(data)
    #     quat = [data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w]
    #     (roll, pitch, yaw) = euler_from_quaternion(quat)
    #     alpha = mt.pi/2 - angles.data[1]
    #     ball_distance.data = mt.tan(alpha) * h_cam
    #     pub_distance.publish(ball_distance)

    def get_thetas(self, u,v):
        #global theta_z, theta_y 
        # x = (v-cx)*sx
        # y = (u-cy)*sy
        x = -(v-self.cx)
        y = -(u-self.cy)
        #if (x >=15) and (y>=15):
        self.theta_z = self.theta_z + int(np.arctan2(x,self.fx)*180/mt.pi) 
        #print(x,theta_x,np.arctan2(x,f))
        self.theta_y = self.theta_y + int(np.arctan2(y,self.fy)*180/mt.pi) 
        #if(theta_y<=-80):
            #print('angulo invalido')
            #theta_y = -80

        self.angles.data = [self.theta_z,self.theta_y]
        rospy.loginfo('the ball coordinate is  %i,%i', u,v)
        self.pub_angles.publish(self.angles)
        time.sleep(1)



    def image_sub(self): #funcao que vai ficar recebendo as imagens da camera
        #o subscriber recebe algo
        #o nó vai subscrever ou publicar num topico
        #o publish vai publicar/enviar algo num topico


    
    # try:
    #     for i in range(100):#while (xx != cx) and (yy != cy):
            #cap = cv.VideoCapture(2)
        rospy.Subscriber("/usb_cam/image_raw", Image, self.image_callback,queue_size=1, buff_size=2**32)
        rospy.spin() #volta pro subscriber, como se fosse um loop pra ficar cosntantemente no subcsriber

if __name__=='__main__':
    bt = Ball_tracking()



    while not rospy.is_shutdown(): #enquanto o roscore estiver rodando, ele vai ficar subscrevendo/recebendo a imagem do topíco da camera e publicando a posicao da bola no topico ball_position
        img = bt.img_queue.get()
        bt.image_callback(img)
        signal.signal(signal.SIGINT, handle_ctrl_c)
        #print('here')
        rospy.Rate(5.0).sleep()

        





            
            
            
