from enum import Enum, unique, auto
import cv2 as cv
import numpy as np

class Symbols(Enum):
    KLAVER = auto()
    SCHOPPEN = auto()
    HARTEN = auto()
    RUITEN = auto()

def symbolToString(symbol):
    return {
        Symbols.KLAVER: 'Club',
        Symbols.SCHOPPEN: 'Spade',
        Symbols.HARTEN: 'Heart',
        Symbols.RUITEN: 'Diamond'
    }.get(symbol, 'undefined')

class CardSymbolRecognition:
    matches = 0

    template_init = False
    template_thresh_init = False

    lower_color = False
    upper_color = False

    def __init__(self, camera):
        self.camera = camera
    
    def get_pos_match(self, symbol):
        if symbol not in [s for s in Symbols]:
            return False
        if not self.template_init:
            self._define_template_and_colors(symbol)
            self.template_init = True
        
        if not self.template_thresh_init:
            self.template_mask = self._mask_of_template(self.template)
            self.template_thresh_init = True
        
        cameraData = self.camera.getImage(); #Haal een foto uit de camera
        img = np.frombuffer(cameraData, np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        img_hsv = cv.cvtColor(img, cv.COLOR_RGB2HSV) #verander de colorspace
        img_mask = cv.inRange(img_hsv, self.lower_color, self.upper_color) #Maak een mask van de foto.
    
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
                
                    contours2,hierarchy2 = cv.findContours(self.template_mask,2,1)
                    for cnr2 in range(len(contours2)):
                        cnt2 = contours2[cnr2]
                        area2 = cv.contourArea(cnt2)
                        if area2 > 300:
                
                            epsilon = 0.009 * cv.arcLength(cnt2, True)
                            approx2 = cv.approxPolyDP(cnt2, epsilon, closed=True)

                            if len(approx2)-3 <= len(approx1) <= len(approx2)+3:#Als het lijnen van de template gelijk is aan het aantal getelde lijnen (met een +- van 2) is het een match
                                #print("Is a match")
                                self.matches += 1
                                if self.matches > 6:
                                    x,y,w,h = cv.boundingRect(cnt1)
                                    #img = cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                    centerX = ((x+(x+w))/2)
                                    centerY = ((y+(y+h))/2)
                                    return centerX
        return False

    def _define_template_and_colors(self, symbol):
        if symbol == Symbols.RUITEN: #Zet de juiste waarden voor kleurmask en het juiste template plaatje wanneer de input text gelijk is aan: 
            self.template = cv.imread('vision/textures/ruiten.jpg')
            self.lower_color = np.array([110,30,30])
            self.upper_color = np.array([180,255,255])
        elif symbol == Symbols.HARTEN:
            self.template = cv.imread('vision/textures/Harten.jpg')
            self.lower_color = np.array([110,30,30])
            self.upper_color = np.array([180,255,255])
        elif symbol == Symbols.SCHOPPEN:
            self.template = cv.imread('vision/textures/Schoppen.jpg')
            self.lower_color = np.array([0,0,0])
            self.upper_color = np.array([180,255,70])
        elif symbol == Symbols.KLAVER:
            self.template = cv.imread('vision/textures/Klavers.jpg')
            self.lower_color = np.array([0,0,0])
            self.upper_color = np.array([180,255,70])

    def _mask_of_template(self, template):
        template_hsv = cv.cvtColor(template, cv.COLOR_RGB2HSV)#Verander colorspace
        template_mask = cv.inRange(template_hsv, self.lower_color, self.upper_color)#maak een mask van de template
        return template_mask
        #template_dilate = cv.dilate(template_mask, (1,1), iterations = 3)
        #ret, thresh2 = cv.threshold(template_dilate, 127, 255, 0)