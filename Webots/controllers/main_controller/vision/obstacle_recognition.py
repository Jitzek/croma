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
    boxarray = []
    counter = 0
    leftPost = 50
    rightPos = 50

    lower_trap = np.array([0,0,0])
    upper_trap = np.array([179,255,90])

    current_stage = GapStage.GO_FORWARDS

    def __init__(self, rbc):
        self.rbc = rbc

    def get_pos_stairs(self):
        #imOnLeft = self.rightPos > 98
        #imOnRight = self.leftPos > 98

        cameraData = self.rbc.Camera.getImage(); #Haal een foto uit de camera
        img = np.frombuffer(cameraData, np.uint8).reshape((self.rbc.Camera.getHeight(), self.rbc.Camera.getWidth(), 4))
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        mask_trap = cv.inRange(hsv, self.lower_trap, self.upper_trap)
        trap_only = cv.bitwise_and(img,img, mask= mask_trap)
    
        contours,hierarchy = cv.findContours(mask_trap,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

        centerX = False
        if len(contours) > 0 and self.counter == 0: #Als er contouren zijn        
            #turnRight(2)
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                #print (perimeter)
                cv.drawContours(trap_only, [cnt], -1, (0,255,0), 3)
            
                if(perimeter > 300):
                    x,y,w,h = cv.boundingRect(cnt)
                    #print (x,y,w,h)
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    centerX = ((x+(x+w))/2)
                    if self.rbc.Camera.getWidth()/2 - 2 <= centerX <= self.rbc.Camera.getWidth()/2 + 2: 
                        if x < 30 and x+w > self.rbc.Camera.getWidth() - 30:
                            return True
        return centerX
    
    def _goForwards(self):
        self.rbc.RightWheelMotors.setVelocity(-5)
        self.rbc.LeftWheelMotors.setVelocity(5)

    def _turnLeft(self):
        self.rbc.RightWheelMotors.setVelocities(-3,-3,0)
        self.rbc.LeftWheelMotors.setVelocities(-3,-3,0)
    
    def _turnRight(self):
        self.rbc.RightWheelMotors.setVelocities(3,3,0)
        self.rbc.LeftWheelMotors.setVelocities(3,3,0)
    
    def go_over_gap(self):
        cameraData = self.rbc.Camera.getImage(); #Haal een foto uit de camera
        img = np.frombuffer(cameraData, np.uint8).reshape((self.rbc.Camera.getHeight(), self.rbc.Camera.getWidth(), 4))
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        mask_trap = cv.inRange(hsv, self.lower_trap, self.upper_trap)
    
        contours,hierarchy = cv.findContours(mask_trap,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)

        stage = {
            GapStage.GO_FORWARDS: partial(self._go_forwards, img, contours),
            GapStage.GO_LEFT_SIDE_1: partial(self._go_left_side_1, img, contours),
            GapStage.GO_LEFT_SIDE_2: partial(self._go_left_side_2, img, contours),
            GapStage.GO_RIGHT_SIDE_1: partial(self._go_right_side_1, img, contours),
            GapStage.GO_RIGHT_SIDE_2: partial(self._go_right_side_2, img, contours),
            GapStage.GO_LEFT_ROUTE_1: partial(self._go_left_route_1, img, contours),
            GapStage.GO_LEFT_ROUTE_2: partial(self._go_left_route_2, img, contours),
            GapStage.GO_RIGHT_ROUTE_1: partial(self._go_right_route_1, img, contours),
            GapStage.GO_RIGHT_ROUTE_2: partial(self._go_right_route_2, img, contours)
        }.get(self.current_stage, False)
        if not stage:
            cv.destroyAllWindows()
            return True
        stage()
        cv.imshow("gap", img)
        cv.waitKey(1)
        return False
        

    def _go_forwards(self, img, contours):
        self._goForwards()
         
        boxes= []     
        for cnr in range(len(contours)):
            cnt = contours[cnr]
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

            img_rect = img[top:bottom, left:right]
            if 19*(bottom-top) > (right-left) > 11*(bottom-top):
                hsv_rect = cv.cvtColor(img_rect, cv.COLOR_BGR2HSV)
                mask_rect = cv.inRange(hsv_rect, self.lower_trap, self.upper_trap)
                mask_brug = cv.bitwise_not(mask_rect)
                mask_brug = cv.morphologyEx(mask_brug, cv.MORPH_OPEN, (20,20))
                kernel = np.ones((5,5), np.uint8) 
                img_erosion = cv.erode(mask_brug, kernel, iterations=3) 
                img_dilation = cv.dilate(img_erosion, kernel, iterations=4) 
                height, width = img_dilation.shape 
                contours2,hierarchy2 = cv.findContours(img_dilation,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
                cv.drawContours(img_rect, contours2, -1, (25,255,0), 3)
                if len(contours2) > 0:
            
                    x2,y2,w2,h2 = cv.boundingRect(contours2[0])
                    cv.rectangle(img_rect,(x2,y2),(x2+w2,y2+h2),(0,255,0),2)
                    self.leftPos = 100 -((x2/width)*100)
                    self.rightPos = ((x2+w2)/width)*100
                    perimeter2 = cv.arcLength(contours2[0], True)
                    #print("p2",perimeter2)
                    if perimeter2 > 140 and self.rightPos > self.leftPos:
                        self.current_stage = GapStage.GO_LEFT_SIDE_1
                    if perimeter2 > 140 and self.leftPos > self.rightPos:
                        self.current_stage = GapStage.GO_RIGHT_SIDE_1
                #cv.imshow("brug", mask_brug)
                #cv.imshow("img_dil", img_dilation)
                #cv.imshow("img_rect", img_rect) 

    def _go_left_side_1(self, img, contours):
        # Go Left
        self._turnLeft()
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    self.boxarray.append([x,y,w,h])
                    if (x+w) == self.rbc.Camera.getWidth():
                        self.current_stage = GapStage.GO_LEFT_SIDE_2
                    
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
    
    def _go_left_side_2(self, img, contours):
        self._goForwards()
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    self.boxarray.append([x,y,w,h])
                    #print("y",y)
                    if y > 98:
                        self.rightPos = 100
                        self.current_stage = GapStage.GO_LEFT_ROUTE_1
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
    
    def _go_right_side_1(self, img, contours):
        # Go Right
        self._turnRight()
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    self.boxarray.append([x,y,w,h])
                    if x == 0:
                        self.current_stage = GapStage.GO_RIGHT_SIDE_2
                    
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
    
    def _go_right_side_2(self, img, contours):
        self._goForwards()
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    self.boxarray.append([x,y,w,h])
                    #print("y",y)
                    if y > 98:
                        self.leftPos = 100
                        self.current_stage = GapStage.GO_RIGHT_ROUTE_1
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
                    ################## GA RECHT ROUTE PART 1
    
    def _go_left_route_1(self, img, contours):
        box_array = []
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.rbc.Camera.getWidth()*0.8:
                    x,y,w,h = cv.boundingRect(cnt)
                    box_array.append([x,y,w,h])
                    #print(len(box_array), "left")
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
        if len(box_array) == 1:
            self._turnRight()

        if len(box_array) == 2:
            self._goForwards()
        
            min = 256
            for box in box_array:            
                if box[1] < min:
                    min = box[1]
           
            if min > self.rbc.Camera.getHeight()/2:
                self.current_stage = GapStage.GO_LEFT_ROUTE_2
    
    def _go_left_route_2(self, img, contours):
        box_array = []
        self._turnLeft()
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    box_array.append([x,y,w,h])
                    print(len(box_array))
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                if perimeter > self.rbc.Camera.getWidth()*2:
                    self.current_stage = GapStage.TRAVERSE_GAP
    
    def _go_right_route_1(self, img, contours):
        box_array = []
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > self.rbc.Camera.getWidth()*0.8:
                    x,y,w,h = cv.boundingRect(cnt)
                    box_array.append([x,y,w,h])
                    print(len(box_array), "right", y)
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                                   
        if len(box_array) == 1:
            self._turnLeft()

        if len(box_array) == 2:
            self._goForwards()
        
            min = self.rbc.Camera.getHeight()
            for box in box_array:            
                if box[1] < min:
                    min = box[1]
           
            if min > self.rbc.Camera.getHeight()/2:
                self.current_stage = GapStage.GO_RIGHT_ROUTE_2

    def _go_right_route_2(self, img, contours):
        box_array = []
        self._turnRight()    
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > self.rbc.Camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    box_array.append([x,y,w,h])
                    print(len(box_array))
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                if perimeter > self.rbc.Camera.getWidth()*2:
                    self.current_stage = GapStage.TRAVERSE_GAP