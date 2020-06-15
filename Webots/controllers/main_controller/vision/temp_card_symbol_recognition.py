from controller import Robot, DistanceSensor, Motor, Camera
import os, numpy as np, cv2 as cv, keyboard

#clear console
os.system('cls')
# time in [ms] of a simulation step
TIME_STEP = 64

MAX_SPEED = 0.9

# create the Robot instance.
robot = Robot()

camera = robot.getCamera('camera')
camera.enable(TIME_STEP)

while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('k'):  # if key 'q' is pressed 
            input_text = "klaver"
            break
        if keyboard.is_pressed('s'):  # if key 'q' is pressed 
            input_text = "schoppen"
            break
        if keyboard.is_pressed('h'):  # if key 'q' is pressed 
            input_text = "harten"
            break
        if keyboard.is_pressed('r'):  # if key 'q' is pressed 
            input_text = "ruiten"
            break  # finishing the loop
    except:
        break  # if user pressed a key other than the given key the loop will break #Test input

if input_text == "ruiten": #Zet de juiste waarden voor kleurmask en het juiste template plaatje wanneer de input text gelijk is aan: 
    template = cv.imread('textures/ruiten.jpg')
    lower_color = np.array([110,30,30])
    upper_color = np.array([180,255,255])
if input_text == "harten":
    template = cv.imread('textures/Harten.jpg')
    lower_color = np.array([110,30,30])
    upper_color = np.array([180,255,255])
if input_text == "schoppen":
    template = cv.imread('textures/Schoppen.jpg')
    lower_color = np.array([0,0,0])
    upper_color = np.array([180,255,70])
if input_text == "klaver":
    template = cv.imread('textures/Klavers.jpg')
    lower_color = np.array([0,0,0])
    upper_color = np.array([180,255,70])
    
if input_text is not None:    
    template_hsv = cv.cvtColor(template, cv.COLOR_RGB2HSV)#Verander colorspace
    template_mask = cv.inRange(template_hsv, lower_color, upper_color)#maak een mask van de template
    template_dilate = cv.dilate(template_mask, (1,1), iterations = 3)
    ret, thresh2 = cv.threshold(template_dilate, 127, 255, 0)
    
    leftFrontMotor = robot.getMotor('wheel_6')
    leftMidMotor = robot.getMotor('wheel_5')
    leftRearMotor = robot.getMotor('wheel_4')

    rightFrontMotor = robot.getMotor('wheel_3')
    rightMidMotor = robot.getMotor('wheel_2')
    rightRearMotor = robot.getMotor('wheel_1')

    leftFrontMotor.setPosition(float('inf'))
    leftMidMotor.setPosition(float('inf'))
    leftRearMotor.setPosition(float('inf'))

    rightFrontMotor.setPosition(float('inf'))
    rightMidMotor.setPosition(float('inf'))
    rightRearMotor.setPosition(float('inf'))

    left = 2
    leftFrontMotor.setVelocity(left)
    leftMidMotor.setVelocity(left)
    leftRearMotor.setVelocity(left)

    right = 2
    rightFrontMotor.setVelocity(right)
    rightMidMotor.setVelocity(right)
    rightRearMotor.setVelocity(right)


    matches = 0
    nonmatches = 0

while robot.step(TIME_STEP) != -1:
    if input_text == None:
        break    
    cameraData = camera.getImage(); #Haal een foto uit de camera
    img = np.frombuffer(cameraData, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
    img_hsv = cv.cvtColor(img, cv.COLOR_RGB2HSV) #verander de colorspace
    img_mask = cv.inRange(img_hsv, lower_color, upper_color) #Maak een mask van de foto.
   
    
    img_dilate = cv.dilate(img_mask, (1,1), iterations = 3)


    ret, thresh = cv.threshold(img_dilate, 127, 255, 0)#Mask naar zwartwit

    contours,hierarchy = cv.findContours(thresh,cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)# Vind contouren in de zwart wit foto
    if len(contours) > 0: #Als er contouren zijn        
        for cnr in range(len(contours)):
            cnt = contours[cnr]
            perimeter = cv.arcLength(cnt, True)
            if perimeter > 100:
                cnt1 = cnt       
                epsilon = 0.009 * cv.arcLength(cnt1, True)
                approx1 = cv.approxPolyDP(cnt1, epsilon, closed=True)
                
                contours2,hierarchy2 = cv.findContours(thresh2,2,1)
                for cnr2 in range(len(contours2)):
                    cnt2 = contours2[cnr2]
                    area2 = cv.contourArea(cnt2)
                    if area2 > 300:
                
                        epsilon = 0.009 * cv.arcLength(cnt2, True)
                        approx2 = cv.approxPolyDP(cnt2, epsilon, closed=True)

                        if len(approx2)-3 <= len(approx1) <= len(approx2)+3:#Als het lijnen van de template gelijk is aan het aantal getelde lijnen (met een +- van 2) is het een match
                            print("Is a match")
                            matches = matches + 1
                            if matches > 4 or nonmatches == 0:
                                x,y,w,h = cv.boundingRect(cnt1)
                                img = cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                centerX = ((x+(x+w))/2)
                                centerY = ((y+(y+h))/2)
                                if 120 <= centerX <= 135:
                                    left = -2
                                    leftFrontMotor.setVelocity(left)
                                    leftMidMotor.setVelocity(left)
                                    leftRearMotor.setVelocity(left)
                                    right = 2
                                    rightFrontMotor.setVelocity(right)
                                    rightMidMotor.setVelocity(right)
                                    rightRearMotor.setVelocity(right)
                                elif centerX > 135:
                                    left = 2
                                    leftFrontMotor.setVelocity(left)
                                    leftMidMotor.setVelocity(left)
                                    leftRearMotor.setVelocity(left)
                                    right = 2
                                    rightFrontMotor.setVelocity(right)
                                    rightMidMotor.setVelocity(right)
                                    rightRearMotor.setVelocity(right)
                                elif centerX < 120:
                                    left = -2
                                    leftFrontMotor.setVelocity(left)
                                    leftMidMotor.setVelocity(left)
                                    leftRearMotor.setVelocity(left)

                                    right = -2
                                    rightFrontMotor.setVelocity(right)
                                    rightMidMotor.setVelocity(right)
                                    rightRearMotor.setVelocity(right)
                                    
                               
                        else:
                            if matches < 4:
                                print("Is not a match")
                                nonmatches += 1
                  
                        break
    else:
        nonmatches += 1
                  
        