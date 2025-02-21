import cv2

def draw_ball(ball, img):

    (x, y), radius = cv2.minEnclosingCircle(ball)
    center = (int(x), int(y))
    radius = int(radius)
    cv2.circle(img, center, radius, (0, 255, 0), 2)
    cv2.putText(img, 'Ball', (center[0], center[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return img




