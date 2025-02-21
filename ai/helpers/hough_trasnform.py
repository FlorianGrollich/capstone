import numpy as np
import cv2


def hough_transform(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)

    lines = cv2.HoughLinesP(edges,1,np.pi/180,120,minLineLength=10,maxLineGap=35)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(img,(x1,y1),(x2,y2),(0,0,0),5)

    return img