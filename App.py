from comm.HubClient import ConnectionState
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
        self.camera = Camera(startPosX=INITIAL_CAMERA_POS_X, 
                             startPosY=INITIAL_CAMERA_POS_Y,
                             zoom=INITIAL_ZOOM)

        self.robot = Robot(self, WHITE, ROBOT_WIDTH, ROBOT_HEIGHT)

    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            if self.robot.client.state == ConnectionState.DISCONNECTED:
                self.running = False

    def quit(self):
        pg.quit()
        sys.exit()
    
    def update(self):
        self.all_sprites.update()
        self.camera.update()
    
    def draw_points(self):
        for point in self.robot.scanned_points:
            '''
                First create a vector with only the length
                then rotate that vector to the correct angle
                then scale that point
            '''
            length = pg.math.Vector2(0, point["length"]*self.camera.get_zoom())
            robot_position = pg.math.Vector2(point["robot_position"])
            rotated_point = length.rotate(-point["angle"]) + robot_position
            camera_pos = pg.math.Vector2(self.camera.get_position()[0], self.camera.get_position()[1])
            pg.draw.circle(self.screen, 
                           RED, 
                           (rotated_point + camera_pos - pg.math.Vector2(INITIAL_CAMERA_POS_X, INITIAL_CAMERA_POS_Y)),
                           DOT_SIZE)


    def draw(self):
        self.screen.fill(BGCOLOR)
        ## Draw the scanned_points first so that they go under the robot
        self.draw_points()
        self.all_sprites.draw(self.screen)
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
                    self.robot.pos = pg.math.Vector2(0, 0)
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
                    self.camera.set_zoom(self.camera.get_zoom() - 0.05)
                if event.key == pg.K_e:
                    self.camera.set_zoom(self.camera.get_zoom() + 0.05)


    def show_start_screen(self):
        pass


app = App()
