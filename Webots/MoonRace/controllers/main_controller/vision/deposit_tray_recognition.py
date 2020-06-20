import numpy as np
import cv2

# CONST wall
WALLHEIGHT = 20 # In centimeters

# CONST bakje
BAKJEHEIGHT = 10 # In centimeters

FOCAL_LENGTH = 6.5


def _decodeImage(data, width, height):
    #Gives us 1d array
    decoded = np.frombuffer(data, dtype=np.uint8)
    #We have to convert it into (height, width ,4) in order to see as an image
    decoded = decoded.reshape((height, width,4))
    return decoded;


def distance_from_deposit_tray(image, camera_width, camera_height):
    img = _decodeImage(image, camera_width, camera_height) #Output: normal array
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    #Find mask
    l_h = 0
    l_s = 0
    l_v = 154
    
    u_h = 18
    u_s = 104
    u_v = 164

    l_c = np.array([l_h, l_s, l_v])
    u_c = np.array([u_h, u_s, u_v])


    mask = cv2.inRange(hsv, l_c, u_c)
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for cont in range(len(contours)):
        cnt = contours[cont]
        cv2.drawContours(img, [cnt], -1, (255,255,0), 3)
        # find the biggest countour 
        c = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(c)
        #print('x,y:',x,y)
        #print('w,h:',w,h)
        if y + h > camera_height - (camera_height/10) and h > 10:
            return True
        # draw rectangle around found contours
        #display.setColor(0xFFFFFF)
        #display.drawRectangle(x,y,w,h)
        if x != 0 or w != 200:
            return x+w/2,y,(BAKJEHEIGHT * FOCAL_LENGTH) / round((h * 0.0264583333), 4)
            #print('Distance',(BAKJEHEIGHT * FOCAL_LENGTH) / round((h * 0.0264583333), 4))
    return False