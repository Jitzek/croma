import numpy as np
import cv2
import math
import itertools

from enum import Enum, unique, auto
@unique
class MineralFlags(Enum):
    SMALL = auto()
    NORMAL = auto()
    BIG = auto()

class DistanceFromMineral:
    DEFAULT_CAMERA_WIDTH = 108
    DEFAULT_CAMERA_HEIGHT = 108

    MINERAL_WIDTH_BIG = 260
    MINERAL_HEIGHT_BIG = 216

    MINERAL_WIDTH_SMALL = 140
    MINERAL_HEIGHT_SMALL = 108
    def __init__(self, camera_width = 128, camera_height = 128, camera_height_from_ground = 0.0):
        self.multiplier = ((camera_width / self.DEFAULT_CAMERA_WIDTH) + (camera_height / self.DEFAULT_CAMERA_HEIGHT))/2
        self.camera_height_from_ground = camera_height_from_ground

    def getDistance_Big(self, width, height):
        return (((0.1 * (self.MINERAL_WIDTH_BIG / width) - self.camera_height_from_ground) + (0.1 * (self.MINERAL_HEIGHT_BIG / height) - self.camera_height_from_ground))/2) * self.multiplier

    def getDistance_SMALL(self, width, height):
        return (((0.1 * (self.MINERAL_WIDTH_SMALL / width) - self.camera_height_from_ground) + (0.1 * (self.MINERAL_HEIGHT_SMALL / height) - self.camera_height_from_ground))/2) * self.multiplier

    """
        Decides the distance from a mineral stone by using the logic that: |distance = 1 / (max_size_mineral / observed_size_mineral)|
                                                                           derived from |distance * 2| means |size / 2|
        0.1 * (COMPARE_VALUE / size)
    """
    def getDistance(self, width, height, flag = MineralFlags.BIG):
        return {
            MineralFlags.BIG: self.getDistance_Big(width, height),
            MineralFlags.SMALL: self.getDistance_SMALL(width, height)
        }.get(flag, self.getDistance_Big(width, height)) # get(case, default)
        
        """
        if perspective == 'GLOBAL':
            w_distance = self._getDistance(width, self.MINERAL_WIDTH_GLOBAL) - self.camera_height_from_ground
            h_distance = self._getDistance(height, self.MINERAL_HEIGHT_GLOBAL) - self.camera_height_from_ground
            return (w_distance+h_distance)/2
        """

########################################
# Colors:
#   - Hex #848476
#   - RGB 132 132 118
#   - HSV 60 10 52
#   - HSV 357 81 51
#
#   - Hex #76705D
#   - RGB 118 112 93
#   - HSV 46 21 46
#   - HSV 14 83 53
#
#   - Hex #5E4028
#   - RGB 94 64 40
#   - HSV 27 57 37
#   - HSV 84 90 58

class MineralRecognition:
    bright_lower_color = np.array([60, 0, 110])
    bright_upper_color = np.array([110, 50, 160])

    inbetween_lower_color = np.array([100, 50, 50])
    inbetween_upper_color = np.array([150, 102, 150])

    dark_lower_color = np.array([102, 15, 80])
    dark_upper_color = np.array([110, 150, 120])

    def __init__(self, camera):
        self.camera_width = camera.getWidth()
        self.camera_height = camera.getHeight()
        pass
    
    def cv2ShowImage(self, image):
        cv2.imshow("preview", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    """
    def sharpen_image(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened
    """

    def get_largest_location(self, locations):
        largest_location = False
        for location in locations:
            if not largest_location or largest_location[2] + largest_location[3] < location[2] + location[3]:
                largest_location = location
        return largest_location

    """
        image:
        Webots Camera getImage()

        Decodes given image and uses opencv to determine de x, y, width and height of all mineral stones in the image

        returns:
        array [0] = x
              [1] = y
              [2] = width
              [3] = height
    """
    def get_location_minerals(self, image):
        # Decode Image for OpenCV Use
        decoded = self.decodeImage(image)
        
        data = self._get_location_minerals(decoded)
        #self.cv2ShowImage(decoded)
        
        self.decoded_img = decoded
        merged_data = self._merge_data(data)
        filtered_data = self._filter_locations(merged_data)
        flagged_data = self._assignFlags(filtered_data)
        return flagged_data
    
    
    def _filter_locations(self, locations):
        ff_strictness = 0.4
        min_height_percentage = 0
        max_height_percentage = 80
        filtered_locations = []
        accuracy = 0
        for location in locations:
            # The closer strictness gets to 1, the more squarelike the location has to be
            # ff_strictness closer to 0 is more forgiving and will accept more rectangular locations
            if location[2]*ff_strictness > location[3] or location[3]*ff_strictness > location[2]: continue
            # Ignore minerals under a certain point of the image (filters out stones in the landscape texture)
            if location[1] - location[3]/2 > self.camera_height*(1 - min_height_percentage*0.01): continue
            if location[1] + location[3]/2 < self.camera_height*(1 - max_height_percentage*0.01): continue

            filtered_locations.append(location)
        return filtered_locations
    
    def _assignFlags(self, locations):
        small_max_height = 30
        big_max_height = 50
        flagged_locations = []
        for location in locations:
            if location[1] + location[3]/2 > self.camera_height*(1 - small_max_height*0.01):
                location.append(MineralFlags.SMALL)
            else:
                location.append(MineralFlags.BIG)
            flagged_locations.append(location)
        return flagged_locations
        
    def _merge_data(self, dataset):
        valid_locations = []

        # Loop through all matches
        for location in dataset:
            result_location = location
            # Loop through all matches again to compare
            for location_compare in dataset:
                if location is location_compare: continue
                x_dev = result_location[2] + location_compare[2]
                y_dev = result_location[3] + location_compare[3]
                if result_location[0] - x_dev > location_compare[0]:
                    continue
                if result_location[0] + x_dev < location_compare[0]:
                    continue
                if result_location[1] - y_dev > location_compare[1]:
                    continue
                if result_location[1] + y_dev < location_compare[1]:
                    continue
                
                """ Merge two locations together """
                # [0] - x
                # [1] - y
                # [2] - width
                # [3] - height
                min_x = (result_location[0] - result_location[2]
                        if result_location[0] - result_location[2] < location_compare[0] - location_compare[2]
                        else location_compare[0] - location_compare[2])
                max_x = (result_location[0] + result_location[2]
                        if result_location[0] + result_location[2] > location_compare[0] + location_compare[2]
                        else location_compare[0] + location_compare[2])
                min_y = (result_location[1] - result_location[3]
                        if result_location[1] - result_location[3] < location_compare[1] - location_compare[3]
                        else location_compare[1] - location_compare[3])
                max_y = (result_location[1] + result_location[3]
                        if result_location[1] + result_location[3] > location_compare[1] + location_compare[3]
                        else location_compare[1] + location_compare[3])
                
                w = abs(max_x - min_x)
                h = abs(max_y - min_y)
                x = min_x + w/2
                y = min_y + h/2
                result_location = [
                                    int(x), 
                                    int(y),
                                    int(w/2),
                                    int(h/2),
                                ]
            valid_locations.append(result_location)
        if len(valid_locations) < 1:
            return dataset

        return valid_locations
    
    def _get_location_minerals(self, image):
        # Convert Image to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Only look for determined colors (leaves only mineral and surface)
        bright_res = self._apply_color_mask(hsv, self.bright_lower_color, self.bright_upper_color)
        inbetween_res = self._apply_color_mask(hsv, self.inbetween_lower_color, self.inbetween_upper_color)
        dark_res = self._apply_color_mask(hsv, self.dark_lower_color, self.dark_upper_color)

        bright_thresh = self._apply_gray_blur_and_thresh(bright_res)
        inbetween_thresh = self._apply_gray_blur_and_thresh(inbetween_res)
        dark_thresh = self._apply_gray_blur_and_thresh(dark_res)

        #self.cv2ShowImage(bright_thresh)
        #self.cv2ShowImage(inbetween_thresh)
        #self.cv2ShowImage(dark_thresh)
        
        data = []
        data.extend(self._get_locations_contours(bright_thresh, True, image))
        data.extend(self._get_locations_contours(inbetween_thresh, True, image))
        data.extend(self._get_locations_contours(dark_thresh, True, image))

        #self.cv2ShowImage(image)

        return data

    
    def _apply_gray_blur_and_thresh(self, res):
        # Grayscale result
        imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

        # Blur Grayed image
        imgrayblur = cv2.GaussianBlur(imgray, (1, 1), 0)

        # Thresh the image
        ret, thresh = cv2.threshold(imgrayblur, 50, 255, 3)

        return thresh

    def _apply_color_mask(self, hsv, lower_color, upper_color):
        mask = cv2.inRange(hsv, lower_color, upper_color)

        res = cv2.bitwise_and(hsv, hsv, mask=mask)

        return res
    
    def _get_locations_contours(self, thresh, drawContours=True, or_image=None):
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        data = []

        for cni in range(len(contours)):
            cnt = contours[cni]

            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter < (2*self.camera_height + 2*self.camera_width)*0.025:
                continue
            ff = ((4 * math.pi) * area) / (perimeter**2)

            #if (ff < 0.2):
            #    continue
            
            if drawContours and or_image.any():
                cv2.drawContours(or_image, [cnt], -1, (255, 255, 0), thickness=1)

            x, y, w, h = cv2.boundingRect(cnt)
            data.append([x,y,w,h])
        
        return data

    def pos_bright_side(self, decoded_image):
        # Convert Image to HSV
        hsv = cv2.cvtColor(decoded_image, cv2.COLOR_RGB2HSV)

        # Only look for determined colors (leaves only mineral and surface)
        mask = cv2.inRange(hsv, self.bright_lower_color, self.bright_upper_color)
        res = cv2.bitwise_and(decoded_image, decoded_image, mask=mask)

        # Grayscale result
        imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

        # Blur Grayed image
        imgrayblur = cv2.GaussianBlur(imgray, (5, 5), 0)

        # Thresh the image
        ret, thresh = cv2.threshold(imgrayblur, 50, 255, 3)
        
        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        data = []

        for cni in range(len(contours)):
            cnt = contours[cni]

            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter < (2*self.camera_height + 2*self.camera_width)*0.025:
                continue
            ff = ((4 * math.pi) * area) / (perimeter**2)

            #if (ff < 0.2):
            #    continue
            
            cv2.drawContours(decoded_image, [cnt], -1, (255, 255, 0), thickness=1)

            x, y, w, h = cv2.boundingRect(cnt)
            data.append([x,y,w,h])
        
        return data
    
    def pos_dark_side(self, decoded_image):
        # Convert Image to HSV
        hsv = cv2.cvtColor(decoded_image, cv2.COLOR_RGB2HSV)

        # Only look for determined colors (leaves only mineral and surface)
        mask = cv2.inRange(hsv, self.dark_lower_color, self.dark_upper_color)
        res = cv2.bitwise_and(decoded_image, decoded_image, mask=mask)

        # Grayscale result
        imgray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

        # Blur Grayed image
        imgrayblur = cv2.GaussianBlur(imgray, (5, 5), 0)

        # Sharpen Image for better edge definement
        sharpened = self.sharpen_image(imgrayblur, amount=5)

        # Thresh the image
        ret, thresh = cv2.threshold(sharpened, 50, 255, 3)
        sharpened = self.sharpen_image(thresh, amount=5)
        #self.cv2ShowImage(thresh)
        
        contours, hierarchy = cv2.findContours(
            sharpened, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        data = []

        for cni in range(len(contours)):
            cnt = contours[cni]

            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter < (2*self.camera_height + 2*self.camera_width)*0.005:
                continue
            ff = ((4 * math.pi) * area) / (perimeter**2)

            #if (ff < 0.2):
            #    continue
            
            cv2.drawContours(decoded_image, [cnt], -1, (255, 255, 0), thickness=1)

            x, y, w, h = cv2.boundingRect(cnt)
            data.append([x,y,w,h])
        
        return data
    
    def getDecodedImage(self):
        return self.decoded_img
    
    def decodeImage(self, image):
        return np.frombuffer(image, np.uint8).reshape((self.camera_height, self.camera_width, 4))