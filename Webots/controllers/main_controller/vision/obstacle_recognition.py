from controller import Robot, Motor, Camera
from functools import partial
import numpy as np, cv2 as cv

from enum import Enum, unique, auto
class GapStage(Enum):
    NONE = auto()

    GO_FORWARDS = auto()

    GO_LEFT_SIDE_1 = auto()
    GO_LEFT_SIDE_2 = auto()
    GO_LEFT_ROUTE_1 = auto()
    GO_LEFT_ROUTE_2 = auto()

    GO_RIGHT_SIDE_1 = auto()
    GO_RIGHT_SIDE_2 = auto()
    GO_RIGHT_ROUTE_1 = auto()
    GO_RIGHT_ROUTE_2 = auto()

    TRAVERSE_GAP = auto()


class ObstacleCourseVision:
    lower_trap = np.array([0,0,0])
    upper_trap = np.array([179,255,90])

    current_stage = GapStage.GO_FORWARDS

    def __init__(self, camera):
        self.camera = camera

    # refresh vision data
    def refreshVisionData(self):
        self.cameraData = self.camera.getImage() #Haal een foto uit de camera
        self.img = np.frombuffer(self.cameraData, np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        self.hsv = cv.cvtColor(self.img, cv.COLOR_BGR2HSV)

        self.mask_trap = cv.inRange(self.hsv, self.lower_trap, self.upper_trap)
    
        self.contours,hierarchy = cv.findContours(self.mask_trap,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

        cv.imshow("img", self.img)
        cv.waitKey(1)

    # returns centerX of stairs boxed
    def get_pos_stairs(self):
        centerX = False
        if len(self.contours) > 0: #Als er contouren zijn        
            #turnRight(2)
            for cnr in range(len(self.contours)):
                cnt = self.contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                #print (perimeter)
            
                if(perimeter > 300):
                    x,y,w,h = cv.boundingRect(cnt)
                    #print (x,y,w,h)
                    cv.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
                    centerX = ((x+(x+w))/2)
                    if self.camera.getWidth()/2 - 2 <= centerX <= self.camera.getWidth()/2 + 2: 
                        if x < 30 and x+w > self.camera.getWidth() - 30:
                            return True
        return centerX
        cv.imshow("img", self.img)
        cv.waitKey(1)

    # returns True when a gap is detected
    # a gap is two contours boxed together with a certain width to height ratio
    def getIsGapDetected(self):
        boxes= []     
        for cnr in range(len(self.contours)):
            cnt = self.contours[cnr]
            perimeter = cv.arcLength(cnt, True)
            if perimeter > 0: 
                (x, y, w, h) = cv.boundingRect(cnt)
                boxes.append([x,y, x+w,y+h])
        if len(boxes) > 0:
            boxes = np.asarray(boxes)
            left = np.min(boxes[:,0])
            top = np.min(boxes[:,1])
            right = np.max(boxes[:,2])
            bottom = np.max(boxes[:,3])

            self.img_rect = self.img[top:bottom, left:right]

            if 19*(bottom-top) > (right-left) > 11*(bottom-top):
                return True
            
    #return bridge perimeter on camera image and position
    def getBridgeStats(self):
        boxes= []     
        for cnr in range(len(self.contours)):
            cnt = self.contours[cnr]
            perimeter = cv.arcLength(cnt, True)
            if perimeter > 0: 
                (x, y, w, h) = cv.boundingRect(cnt)
                boxes.append([x,y, x+w,y+h])
        if len(boxes) > 0:
            boxes = np.asarray(boxes)
            left = np.min(boxes[:,0])
            top = np.min(boxes[:,1])
            right = np.max(boxes[:,2])
            bottom = np.max(boxes[:,3])

            self.img_rect = self.img[top:bottom, left:right]
        
        hsv_rect = cv.cvtColor(self.img_rect, cv.COLOR_BGR2HSV)
        mask_rect = cv.inRange(hsv_rect, self.lower_trap, self.upper_trap)
        mask_brug = cv.bitwise_not(mask_rect)
        mask_brug = cv.morphologyEx(mask_brug, cv.MORPH_OPEN, (20,20))
        kernel = np.ones((5,5), np.uint8) 
        img_erosion = cv.erode(mask_brug, kernel, iterations=3) 
        img_dilation = cv.dilate(img_erosion, kernel, iterations=4) 
        height, width = img_dilation.shape 
        contours2,hierarchy2 = cv.findContours(img_dilation,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(self.img_rect, contours2, -1, (0,255,0), 3)
        
        cv.imshow("gap", self.img_rect)
        cv.waitKey(1)

        perimeter2 = 0
        leftPos = 50
        rightPos = 50
        if len(contours2) > 0:
            
            x2,y2,w2,h2 = cv.boundingRect(contours2[0])
            cv.rectangle(self.img_rect,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)
            leftPos = 100 -((x2/width)*100)
            rightPos = ((x2+w2)/width)*100
            perimeter2 = cv.arcLength(contours2[0], True)
            print("p2",perimeter2)
            return perimeter2, leftPos, rightPos

        return perimeter2, leftPos, rightPos

    #returns measurment of gap box
    def getGapBoxMeasurements(self):        
        if len(self.contours) > 0:
            for cnr in range(len(self.contours)):
                cnt = self.contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    return x,y,w,h
                   # self.boxarray.append([x,y,w,h])
                    #if (x+w) == self.rbc.Camera.getWidth():
                     #   self.current_stage = GapStage.GO_LEFT_SIDE_2
                    
                    cv.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(self.img, [cnt], -1, (25,255,0), 3)
                    
        cv.imshow("img", self.img)
        cv.waitKey(1)

    # returns gap boxes   
    def getGapBoxes(self):
        box_array = []
        if len(self.contours) > 0:
            for cnr in range(len(self.contours)):
                cnt = self.contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.camera.getWidth()*0.8:
                    x,y,w,h = cv.boundingRect(cnt)
                    box_array.append([x,y,w,h])
                    #print(len(box_array), "left")
                    cv.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(self.img, [cnt], -1, (25,255,0), 3)
                    
        cv.imshow("img", self.img)
        cv.waitKey(1)
                    
        return box_array

    #returns true when robot is centered
    def robotIsCentered(self):
        if len(self.contours) > 0:
            for cnr in range(len(self.contours)):
                cnt = self.contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    #box_array.append([x,y,w,h])
                    #print(len(box_array))
                    cv.rectangle(self.img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(self.img, [cnt], -1, (25,255,0), 3)
                if perimeter > self.camera.getWidth()*2:
                    return True
        cv.imshow("img", self.img)
        cv.waitKey(1)
    
