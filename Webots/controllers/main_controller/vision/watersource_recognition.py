import numpy as np, cv2 as cv, math

from enum import Enum, unique, auto

def getColorTemp(image, width, height):
   img = np.frombuffer(image, dtype= np.uint8)
   #convert img to readable image: height x width x N channels
   img = img.reshape(height, width,4)

   ##focused image/ make crop
   center_y = int(height/2)
   center_x = int(width/2)
   crop_img = img[(center_y)-1:(center_y),(center_x)-1:(center_x)]#make crop
   #crop_img = img[125:125+7,125:125+7]# make crop
   ##color recognition

   # Take each frame
   frame = crop_img

   # Convert BGR to HSV
   hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

   # define range of koud color in HSV
   lower_koud = np.array([84,30,50])
   upper_koud = np.array([110,255,255])
   #([90,36,50])
   #[102,155,255])
   # define range of lauw color in HSV
   lower_lauw = np.array([31,17,0])
   upper_lauw = np.array([83,83,255])
   #([32,17,184])
   #([90,89,255])
   # define range of warm color in HSV
   lower_warm = np.array([22,89,0])
   upper_warm = np.array([34,214,220])
   # [22,89,182])
   #[34,217,192])
   # define range of heet color in HSV
   lower_heet = np.array([0,0,0])
   upper_heet = np.array([22,255,255])
   #[0,222,188])
   #[22,255,200])
   # define range of black to white color in HSV
   lower_black = np.array([0,0,0])
   upper_white = np.array([0,0,255])

   # Threshold the HSV image to get only black to white colorrange
   bw = cv.inRange(hsv, lower_black, upper_white)

   # Threshold the HSV image to get only koud colors
   mask_koud = cv.inRange(hsv, lower_koud, upper_koud)

   # Threshold the HSV image to get only lauw colors
   mask_lauw = cv.inRange(hsv, lower_lauw, upper_lauw)

   #Threshold the HSV image to get only warm colors
   mask_warm = cv.inRange(hsv, lower_warm, upper_warm)

   # Threshold the HSV image to get only heet colors
   mask_heet = cv.inRange(hsv, lower_heet, upper_heet)

   #debug: show all masks
   #cv.namedWindow('masks',cv.WINDOW_NORMAL)
   #cv.imshow('masks', mask_heet | mask_warm | mask_lauw | mask_koud )

   # Bitwise-AND mask and original image
   #koud_only = cv.bitwise_and(frame,frame, mask= mask_koud |bw)
   #lauw_only = cv.bitwise_and(frame,frame, mask= mask_lauw | bw)
   #warm_only = cv.bitwise_and(frame,frame, mask= mask_warm | bw)
   #heet_only = cv.bitwise_and(frame,frame, mask= mask_heet |bw)

   #debug: show all colored masks
   #cv.namedWindow('colored',cv.WINDOW_NORMAL)
   #cv.imshow('heet_only', heet_only)
   #cv.imshow('warm_only', warm_only)
   #cv.imshow('lauw_only', lauw_only)
   #cv.imshow('koud_only', koud_only)

   #convert klwh images to greyscale for next step

   #debug: show all grey
   #cv.namedWindow('grays',cv.WINDOW_NORMAL)
   #cv.imshow('grays', gray_heet | gray_warm | gray_lauw | gray_koud)

   #if color recognized print the temp in console and refresh image window    
   if cv.countNonZero(mask_koud) != 0:#if count of NonZero(non-black pixels) is not 0
     return "Cold"
     
   if cv.countNonZero(mask_lauw) != 0:
     return "Lukewarm"
     
   if cv.countNonZero(mask_warm) != 0:
     return "Warm"
     
   if cv.countNonZero(mask_heet) != 0:
     return "Hot"

   return "NaN"
  

def getPosWaterSource(image, width, height):
  lower_color = np.array([3,9,56])
  upper_color = np.array([31,105,255])

  lower_color2 = np.array([3,0,13])
  upper_color2 = np.array([45,185,201])

  img = np.frombuffer(image, np.uint8).reshape((height, width, 4))
  img_blur = cv.GaussianBlur(img,(5,5),0)
  img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV) #verander de colorspace
  img_mask1 = cv.inRange(img_hsv, lower_color, upper_color) #Maak een mask van de foto.
  img_mask2 = cv.inRange(img_hsv, lower_color2, upper_color2)
  img_mask = img_mask1 | img_mask2

  ret, thresh = cv.threshold(img_mask, 127, 255, 0)#Mask naar zwartwit

  img_mask = cv.medianBlur(img_mask,5)
  mask_inv = cv.bitwise_not(img_mask)

  x_dev = width/10
  y_dev = height/10

  min_x = width/2 - x_dev
  max_x = width/2 + x_dev

  min_y = height/2 - y_dev
  max_y = height/2 - y_dev

  contours,hierarchy = cv.findContours(mask_inv,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)# Vind contouren in de zwart wit foto
  if len(contours) > 0: #Als er contouren zijn        
    for cnr in range(len(contours)):
      cnt = contours[cnr]
      perimeter = cv.arcLength(cnt, True)
      area = cv.contourArea(cnt)
      if area > 200:
        factor = 4 * math.pi * area / perimeter**2
        x,y,w,h = cv.boundingRect(cnt)
        #img = cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        centerX = ((x+(x+w))/2)
        centerY = ((y+(y+h))/2)
        return centerX, centerY
  return False