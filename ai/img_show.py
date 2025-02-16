import cv2 as cv


def show(img):
    cv.imshow("show", img)
    cv.waitKey(0)