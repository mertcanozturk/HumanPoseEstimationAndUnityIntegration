import argparse
import logging
import time
import socket
import cv2
import numpy as np
from threading import Thread

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

logger = logging.getLogger('TfPoseEstimator-Video')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
veri=""
fps_time = 0

def sending_and_reciveing(arg):
    s = socket.socket()
    print('socket created ')
    port = 1234
    s.bind(('127.0.0.1', port)) #bind port with ip address
    print('socket binded to port ')
    s.listen(5)#listening for connection
    print('socket listensing ... ')
    while True:
        c, addr = s.accept() #when port connected
        print("\ngot connection from ", addr)
        de=c.recv(1024).decode("utf-8") #Collect data from port and decode into  string
        print('Getting Data from the Unity : ',de)

        list=de.split(',') #cominda data is postion so we split into list on basis of ,

        UpdateValue=""

        for value in list: #loop for each value in the string single
            value=str(value)#sonvet list value into string
            if '(' in value or ')' in value: #coming data in to form of (1.0,2.2,3.0),when split then we check each value dosnt contan '(' or ')'
                value=value.replace('(','') #if it ( contain any one of these we remove it
                value=value.replace(')', '')#if it ) contain any one of these we remove it
            C_value=float(value) #convert string value into float
            UpdateValue=UpdateValue+(str(C_value+3.0))+" " #add 3.0 into float value and put it in a string
        print('After changing data sending back to Unity')
        c.sendall(UpdateValue[:-1].encode("utf-8"))#then encode and send taht string back to unity
        c.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation Video')
    parser.add_argument('--video', type=str, default='')
    parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    parser.add_argument('--showBG', type=bool, default=True, help='False to show skeleton only.')
    args = parser.parse_args()

    thread = Thread(target=sending_and_reciveing,args = (10, ))
    thread.start()
    thread.join()

    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resolution)
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    cap = cv2.VideoCapture(args.video)

    if cap.isOpened() is False:
        print("Error opening video stream or file")
    while cap.isOpened():
        ret_val, image = cap.read()
        humans = e.inference(image)
        if not args.showBG:
            image = np.zeros(image.shape)
        image,centers = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        cv2.putText(image, "FPS: %f" % (1.0 / (time.time() - fps_time)), (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()
        if cv2.waitKey(33) == ord('a'):
            break
    cv2.destroyAllWindows()
logger.debug('finished+')

