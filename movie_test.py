'''
Created on Feb 20, 2015

@author: Hao Wu
'''
import cv2
import numpy as np
from equipment.image_io import Collection


coll=Collection('data/2015-03-03-16-47-20',create=False)

video  = cv2.VideoWriter('data/counter1.avi', -1, 8, (1024, 1024));
end_count=coll.end_count

for i in range(end_count):
    img=coll.channels['counter'].get_frame(i)
    print(img)
    video.write(img)

video.release()    