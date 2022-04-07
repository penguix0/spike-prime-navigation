from settings import *
import pygame as pg
import sys
from Robot import Robot
from camera import Camera

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(DISPLAY_SIZE)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
        self.new()
        self.run()

    def load_data(self):
        pass

    def new(self):
        self.load_data()
        # initialize all sprites
        self.all_sprites = pg.sprite.Group()
        
        ## Center the camera
        self.camera_offset = pg.math.Vector2(DISPLAY_SIZE[0] / 2, DISPLAY_SIZE[1] / 2)
        self.camera = Camera(startPosX=self.camera_offset.x, 
                             startPosY=self.camera_offset.y,
                             zoom=1)

        self.robot = Robot(self, WHITE, ROBOT_WIDTH, ROBOT_HEIGHT)

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()
    
    def update(self):
        self.all_sprites.update()
        self.camera.update()
    
    def draw_points(self):
        for point in self.robot.scanned_points:
            length_added_point = pg.math.Vector2()
            length_added_point.x = 0
            length_added_point.y += point["length"] * 4
            robot_position = pg.math.Vector2(point["robot_position"])
            rotated_point = length_added_point.rotate(-point["angle"]) + robot_position
            camera_pos = pg.math.Vector2(self.camera.position()[0], self.camera.position()[1])
            pg.draw.circle(self.screen, RED, 
                           (rotated_point + camera_pos - self.camera_offset),
                            5 * self.camera.zoom)


    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_points()
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_r:
                    self.robot.scanned_points = [self.robot.dummy_scan]
                ## Move the camera
                if event.key == pg.K_a:
                    self.camera.x -= 10
                if event.key == pg.K_d:
                    self.camera.x += 10
                if event.key == pg.K_w:
                    self.camera.y -= 10
                if event.key == pg.K_s:
                    self.camera.y += 10
                ## Zoom the camera
                if event.key == pg.K_q:
                    self.camera.zoom -= 0.1
                if event.key == pg.K_e:
                    self.camera.zoom += 0.1


    def show_start_screen(self):
        pass


app = App()
