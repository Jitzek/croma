from controller import Robot, DistanceSensor, Motor, Camera
import os, numpy as np, cv2 as cv, keyboard

#clear console
os.system('cls')
# time in [ms] of a simulation step
TIME_STEP = 1

MAX_SPEED = 0.9

# create the Robot instance.
robot = Robot()

# initialize devices
#ps = []
#psNames = [
 #   'ps0', 'ps1', 'ps2', 'ps3',
 #   'ps4', 'ps5', 'ps6', 'ps7'
#]

#for i in range(8):
#    ps.append(robot.getDistanceSensor(psNames[i]))
#    ps[i].enable(TIME_STEP)



camera = robot.getCamera('camera')
camera.enable(TIME_STEP)

leftFrontMotor = robot.getMotor('wheel_4')
leftMidMotor = robot.getMotor('wheel_5')
leftRearMotor = robot.getMotor('wheel_6')

rightFrontMotor = robot.getMotor('wheel_1')
rightMidMotor = robot.getMotor('wheel_2')
rightRearMotor = robot.getMotor('wheel_3')

leftFrontMotor.setPosition(float('inf'))
leftMidMotor.setPosition(float('inf'))
leftRearMotor.setPosition(float('inf'))

rightFrontMotor.setPosition(float('inf'))
rightMidMotor.setPosition(float('inf'))
rightRearMotor.setPosition(float('inf'))

left = 0
leftFrontMotor.setVelocity(left)
leftMidMotor.setVelocity(left)
leftRearMotor.setVelocity(left)

right = 0
rightFrontMotor.setVelocity(right)
rightMidMotor.setVelocity(right)
rightRearMotor.setVelocity(right)

lower_trap = np.array([0,0,0])
upper_trap = np.array([179,255,90])

counter = 250;
leftPos = 50;                
rightPos = 50;


def go(speed):
    speed = 5
    left = speed*-1
    leftFrontMotor.setVelocity(left)
    leftMidMotor.setVelocity(left)
    leftRearMotor.setVelocity(left)
    right = speed
    rightFrontMotor.setVelocity(right)
    rightMidMotor.setVelocity(right)
    rightRearMotor.setVelocity(right)  
    print("voorwaarts") 
    
def turnRight(speed):
    speed = 3
    left=right=speed
    leftFrontMotor.setVelocity(left)
    #leftMidMotor.setVelocity(left)
    leftRearMotor.setVelocity(left)
    rightFrontMotor.setVelocity(right)
    rightMidMotor.setVelocity(right)
    #rightRearMotor.setVelocity(right)  
    print("turning right")
    
def turnLeft(speed):
    speed = 3
    left=right=speed*-1
    leftFrontMotor.setVelocity(left)
    #leftMidMotor.setVelocity(left)
    leftRearMotor.setVelocity(left)
    rightFrontMotor.setVelocity(right)
    rightMidMotor.setVelocity(right)
    #rightRearMotor.setVelocity(right)  
    print("turning left")

    
       
while robot.step(TIME_STEP) != -1:
    imOnLeft = rightPos > 98
    imOnRight = leftPos > 98
    
    print("leftpos", leftPos)
    print("rightpos", rightPos)

    cameraData = camera.getImage(); #Haal een foto uit de camera
    img = np.frombuffer(cameraData, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    mask_trap = cv.inRange(hsv, lower_trap, upper_trap)
    trap_only = cv.bitwise_and(img,img, mask= mask_trap)
    
    contours,hierarchy = cv.findContours(mask_trap,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
#############3ZOEK TRAP
    if len(contours) > 0 and counter == 0: #Als er contouren zijn        
        turnRight(2)
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
                if camera.getWidth()/2 - 2 <= centerX <= camera.getWidth()/2 + 2: 
                    if x < 20 and x+w > 226:
                        print("WTFTTTT")
                        counter = 250
                elif centerX < camera.getWidth()/2 - 2: 
                    turnLeft(2)

                elif centerX > camera.getWidth()/2 + 2: 
                    turnRight(2)



####################ZOEK GAP
    if counter == 250: 
        go(2)
         
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

        #cv.rectangle(img, (left,top), (right,bottom), (0, 255, 0), 2)
            img_rect = img[top:bottom, left:right]
            if 19*(bottom-top) > (right-left) > 11*(bottom-top):
                hsv_rect = cv.cvtColor(img_rect, cv.COLOR_BGR2HSV)
                mask_rect = cv.inRange(hsv_rect, lower_trap, upper_trap)
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
                    leftPos = 100 -((x2/width)*100)
                    rightPos = ((x2+w2)/width)*100
                    print (leftPos)
                    print (rightPos)
                    perimeter2 = cv.arcLength(contours2[0], True)
                    print("p2",perimeter2)
                    if perimeter2 > 140 and rightPos > leftPos:
                        imInMiddle = True
                        print("LEFT MID")
                        print("p2",perimeter2)
                        counter = 666
                    if perimeter2 > 140 and leftPos > rightPos:
                        imInMiddle = True
                        print("RIGHT MID")
                        print("p2",perimeter2)
                        counter = 123
                cv.imshow("brug", mask_brug)
                cv.imshow("img_dil", img_dilation)
                cv.imshow("img_rect", img_rect) 
            
            
                #if cv.countNonZero(img_dilation) == 0: # if black no color
                    #print("wtffdsfa")
                    #counter = 100;
                    
           ####################GA LINKERKANT PART 1
    if counter == 666:
        turnLeft(2)
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    if (x+w) == camera.getWidth():
                         counter = 888
                    
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
          ##################GA LINKERKANT PART `2
    if counter == 888:
        go(2)
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print("y",y)
                    if y > 98:
                        rightPos = 100
                        counter = 4000
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    ##################### GA LINKS ROUTE PART 1
                    
    boxarray =[]
    if imOnLeft:
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.8:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print(len(boxarray), "left")
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
                                       
        if len(boxarray) == 1:
            turnRight(2)

        if len(boxarray) == 2:
            go(2)
        
            min = 256
            for box in boxarray:            
                if box[1] < min:
                    min = box[1]
            print(boxarray)
            print(min)
           
            if min > camera.getHeight()/2:
                counter = 3
                ############### GA LINKS ROUTE PART 2
    if counter == 3:  
        turnLeft(2)    
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print(len(boxarray))
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                if perimeter > camera.getWidth()*2:
                    counter = 4 
                    
                    ########### GA RECHTS PART 1
    if counter == 123:
        turnRight(2)
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    if x == 0:
                         counter = 238
                    
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
                    ############## GA RECHTS PART 2
                        
    if counter == 238:
        go(2)
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print("y",y)
                    if y > 98:
                        leftPos = 100
                        counter = 4000
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                    
                    ################## GA RECHT ROUTE PART 1
    if imOnRight:
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.8:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print(len(boxarray), "right", y)
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                                   
        if len(boxarray) == 1:
            turnLeft(2)

        if len(boxarray) == 2:
            go(2)
        
            min = 256
            for box in boxarray:            
                if box[1] < min:
                    min = box[1]
            print(boxarray)
            print(min)
           
            if min > camera.getHeight()/2:
                counter = 5  
                 

          
######################## GA RECHTs ROUTE Part 2   

    if counter == 5:  
        turnRight(2)    
        if len(contours) > 0:
            for cnr in range(len(contours)):
                cnt = contours[cnr]
                perimeter = cv.arcLength(cnt, True)
                print(perimeter)
                if perimeter > camera.getWidth()*0.9:
                    x,y,w,h = cv.boundingRect(cnt)
                    boxarray.append([x,y,w,h])
                    print(len(boxarray))
                    cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    cv.drawContours(img, [cnt], -1, (25,255,0), 3)
                if perimeter > camera.getWidth()*2:
                    counter = 4    

                    



   #################### GA FORWARD NAAR BEKER 
    
    if counter == 4:
            go(2)  
            
        #else if perimeter2
        
        
                                 
    cv.imshow("img", img)
    cv.imshow("trap", trap_only)
    cv.waitKey(TIME_STEP)

        
