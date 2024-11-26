import GUI
import HAL
import cv2

i=0
previous_error = 0
kp = 0.01
kd = 0.01
sum = 0
ki = 0.000002

while True:
    img = HAL.getImage()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask= cv2.inRange(hsv,(0,125,125), (30,255,255))
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    M = cv2.moments(contours[0])
    if M["m00"]!=0:
      cX = M["m10"]/M["m00"]
      cY = M["m01"]/M["m00"]
    else: 
      cX, cY = 0,0
    if cX > 0:
      err = 320 -cX
      difference = previous_error - err
      HAL.setV(4)
      HAL.setW(kp *err + kd*difference + ki*sum)
    GUI.showImage(red_mask)
    print('%d cX: %.2f cY: %.2f' % (i, cX, cY))
    
    i+=1
    sum+=err
    previous_error = err
