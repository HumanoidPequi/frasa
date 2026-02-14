import cv2
from threading import Thread
from queue import Queue
from os.path import join
class Image_thread(Thread):
    def __init__(self):
        Thread.__init__(self, name="image_thread")
        self.running = True
        self.info = Queue(maxsize=1)
        self.cap = cv2.VideoCapture(0)

    def run(self):
        i = 0
        image_folder = "/home/marta/Imagens/ball_tracking_nuc"
        while self.run:
            ret, image = self.cap.read()
            if self.info.full():
                self.info.get()
        
            self.info.put(image)
            cv2.imwrite(join(image_folder,'image_'+str(i)+'.jpg'),image)
            i = i + 1

    def stop(self):
        self.running = False
