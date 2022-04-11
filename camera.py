class Camera():
    def __init__(self, startPosX:float, startPosY:float, zoom:float):
        self.x = startPosX
        self.y = startPosY
        self.zoom = zoom

    def smoothZoom(self, originalZoom:float, newZoom:float, speed:int):
        pass

    def get_position(self):
        return (self.x, self.y)

    def get_zoom(self):
        return self.zoom
    
    def set_zoom(self, newZoom:float):
        self.zoom = newZoom

    def update(self):
        pass
