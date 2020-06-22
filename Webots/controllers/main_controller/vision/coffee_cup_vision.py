import cv2
import numpy as np
from vision.drive_to_cup import DriveToCup


class CoffeeCupVision:
    def __init__(self, camera, robot):
        self.camera = camera
        self.dtc = DriveToCup(robot)

    def decodeImage(self, data, width, height):
        # Gives us 1d array
        decoded = np.frombuffer(data, dtype=np.uint8)
        # We have to convert it into (height, width ,4) in order to see as an image
        decoded = decoded.reshape((height, width, 4))
        return decoded

    def converContours(self, img, l_c, u_c):
        # Convert HSV -> Mask -> get contours
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, l_c, u_c)
        #cv2.imshow('test', mask)
        #cv2.waitKey(0)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours, hierarchy

    def detectedWaterInCupIsClose(self, img, camera):
        # Find mask
        l_c = np.array([71, 153, 139])
        u_c = np.array([165, 255, 255])
        contours, hierarchy = self.converContours(img, l_c, u_c)

        height = camera.getHeight()

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            print('y',y)
            if y > 122:  # Make constant?
                return True

        return False

    def see_cup(self, image, camera):
        img = self.decodeImage(image, camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 135, 0])
        u_c = np.array([255, 255, 255])

        contours, hierarchy = self.converContours(img, l_c, u_c)

        width = 0

        waterInCupDetected = self.detectedWaterInCupIsClose(img, self.camera)

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            width = w
            if waterInCupDetected == False:
                self.dtc.steerTo((x + (w / 2)), self.camera.getWidth())
            elif waterInCupDetected == True:
                # brake()
                self.dtc.reverse(2)

        return waterInCupDetected

    def isCupSeen(self, camera):
        img = self.decodeImage(camera.getImage(), camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 135, 0])
        u_c = np.array([255, 255, 255])

        contours, hierarchy = self.converContours(img, l_c, u_c)

        x, y, w, h = 0, 0, 0, 0

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

        if w != 0 or h != 0:
            return True
        else:
            return False

    # Skybox seen
    def skyBoxSeen(self, image, camera):
        img = self.decodeImage(image, camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 0, 193])
        u_c = np.array([255, 255, 255])

        contours, hierarchy = self.converContours(img, l_c, u_c)

        width = camera.getWidth()

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            if w > (width / 4):
                # print('SkyBox is seen')
                return True
            else:
                return False
                # print('SkyBox not found')

        return False

    def findFarEdge(self, image, camera):
        img = self.decodeImage(image, camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 0, 85])
        u_c = np.array([52, 25, 149])

        contours, hierarchy = self.converContours(img, l_c, u_c)

        boolSkybox = self.skyBoxSeen(image, camera)

        h = 0
        w = 0

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            if boolSkybox:
                # print('Far edge found: ', h)
                return True, h, w
            else:
                # print('Edge not found')
                return False, h, w
        return False, h, w

    def findGroundToAlignEdge(self, image, camera):
        img = self.decodeImage(image, camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 31, 0])
        u_c = np.array([39, 72, 177])

        contours, hierarchy = self.converContours(img, l_c, u_c)

        height = camera.getHeight()

        boolSkybox = self.skyBoxSeen(image, camera)

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            if h <= ((height / 2) + 20) and h >= ((height / 2) - 20) and not boolSkybox:
                return "alligned"
        return "not alligned"

    def find_edge(self, image, camera):
        boolEdgeFound, EdgeHeight, EdgeWidth = self.findFarEdge(camera.getImage(), camera)

        # If edge not found keep turning
        print('Edgebool: ', boolEdgeFound)
        if not boolEdgeFound:
            print('turn')
            self.dtc.turn(2)
            return False, 0, 0
        else:
            self.dtc.turn(0)
            return True, EdgeHeight, EdgeWidth

    def driveto_edge(self, image, camera):
        # print('drive to edge')
        boolEdgeFound, EdgeHeight, EdgeWidth = self.find_edge(image, camera)
        cupBool = self.isCupSeen(camera)
        SkyBoxBool = self.skyBoxSeen(camera.getImage(), camera)

        if not cupBool and boolEdgeFound and EdgeHeight > 10:
            self.dtc.forward(2)

        # Check if edge is reached
        print(EdgeHeight)
        if EdgeHeight <= 10 and not cupBool and SkyBoxBool:
            # forward(0)
            return True
        else:
            return False

    def alignWithEdge(self, image, camera):
        aligned = self.findGroundToAlignEdge(camera.getImage(), camera)

        if aligned == "alligned":
            return True
        elif aligned == "not alligned":
            self.dtc.turn(-2)
            return False

    def avoid_cup(self, image, camera):
        img = self.decodeImage(image, camera.getWidth(), camera.getHeight())  # Output: normal array

        # Find mask
        l_c = np.array([0, 135, 0])
        u_c = np.array([255, 255, 255])

        width = camera.getWidth()

        contours, hierarchy = self.converContours(img, l_c, u_c)

        x, y, w, h = 0, 0, 0, 0

        for cont in range(len(contours)):
            cnt = contours[cont]
            cv2.drawContours(img, [cnt], -1, (255, 255, 0), 3)
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)

        print(w)
        if w > (width / 8) and w is not 0:
            print('reverse')
            self.dtc.reverse(2)
        elif w <= (width / 8) and not self.find_edge(image, camera):
            print('find Edge')
            self.find_edge(image, camera)
        elif w <= (width / 8) and self.find_edge(image, camera) and not self.driveto_edge(image, camera):
            print('now drive forward')
            self.driveto_edge(image, camera)
        elif w <= (width / 8) and self.driveto_edge(image, camera) and self.find_edge(image,
                                                                                      camera) and not self.alignWithEdge(
                image, camera):
            print('now start aligning')
            self.alignWithEdge(image, camera)
            return "align"

        return "not align"
