import argparse
import logging
import time
import os
import threading
import socket
import cv2
import numpy as np

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh
bones={}
logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0


def sending_and_reciveing():
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
        print('After changing data sending back to Unity')
        c.sendall(str(bones).encode("utf-8"))#then encode and send taht string back to unity
        c.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)

    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')

    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()
    
    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))

    threading.Thread(target=sending_and_reciveing).start()


    while True:
        ret_val, image = cam.read()

        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)

        logger.debug('postprocess+')
        image,bones = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        fontface = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 1
        fontcolor = (255, 255, 255)
        cv2.putText(image, 'mert', (50, 50), fontface, fontscale, fontcolor)


        logger.debug(str(bones))
        cv2.imshow('tf-pose-estimation result', image)
        if len(bones)!=0:
            if os.path.isfile("deneme2.txt") and os.access("deneme2.txt", os.R_OK):
                f = open("deneme2.txt", "r+")
                f.write(str(bones))
                f.close()
        fps_time = time.time()
        if cv2.waitKey(33) == ord('a'):
            break

    cv2.destroyAllWindows()
