class VisionDisplay:
    NAME_OF_DISPLAY = 'vision_display'

    def __init__(self, display, camera, display_color):
        self.display = display
        self.camera = camera
        self.display_color = display_color
    
    def refresh(self, image_arr):
        imageRef = self.display.imageNew(image_arr, self.display_color, self.camera.getWidth(), self.camera.getHeight())
        self.display.imagePaste(imageRef, 0, 0)

    def setColor(self, color):
        self.display.setColor(color)

    def setThickness(self, thickness):
        self.display.setFont(self, 0, thickness, 0)

    def drawRectangle(self, x, y, w, h):
        self.display.drawRectangle(x, y, w, h)
    
    def drawText(self, text, x, y):
        self.display.drawText(text, x, y)