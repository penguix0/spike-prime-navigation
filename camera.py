class Camera():
    def __init__(self, startPosX:float, startPosY:float, zoom:float):
        self.x = startPosX
        self.y = startPosY
        self.zoom = zoom

    def smoothZoom(self, originalZoom:float, newZoom:float, speed:int):
        pass
