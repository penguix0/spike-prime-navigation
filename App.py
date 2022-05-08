from sqlite3 import connect
from settings import *
import pygame as pg
import sys
from Robot import Robot
from camera import Camera
import threading
import random

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(DISPLAY_SIZE)
        pg.display.set_caption(TITLE)
        self.icon = pg.image.load('icon.png')
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()

        self.fonts_initiated = False

        self.modes = { 
            "1": ["Ziek", False],
            "2": ["Normaal", False],
            "3": ["Auto", False]
        }
        self.mode_text = "Druk een getal in om een modus te selecteren."

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
        
        create_fonts = threading.Thread(target=self.initialize_fonts())
        create_fonts.start()

    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        self.robot.client.connection.close()
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
            rotated_point = length.rotate(-point["angle"])
            pg.draw.circle(self.screen, 
                           RED, 
                           (rotated_point + robot_position),
                           DOT_SIZE)
    
    def draw_text(self):
        if self.fonts_initiated and self.robot.setup_complete:
            position = self.font.render('Position: ' + str(self.robot.pos), True, GRAY)
            self.screen.blit(position, (20, 20))
            speed = self.font.render('Speed: ' + str(round(self.robot.speed, 1)), True, GRAY)
            self.screen.blit(speed, (20, 40))
            mode = self.font.render('Mode: ' + self.mode_text, True, GRAY)
            self.screen.blit(mode, (20, 60))
            if self.robot.activity != None:
                activity = self.font.render('Activiteit: ' + str(self.robot.activity_text), True, GRAY)
            else:
                activity = self.font.render('Activiteit: -', True, GRAY)
            self.screen.blit(activity, (20, 80))
            if type(self.robot.tracker_state) == str:
                nek = self.font.render('Nek: ' + self.robot.tracker_state, True, GRAY)
            elif self.robot.tracker_state == True:
                nek = self.font.render('Nek: omlaag', True, GRAY)
            elif self.robot.tracker_state == False:
                nek = self.font.render('Nek: omhoog', True, GRAY)
            self.screen.blit(nek, (20, 100))
        elif self.fonts_initiated:
            text = "Starting"
            if not self.robot.setup_complete:
                text = 'Preparing robot...'
            else:
                text = "Connecting..."
            connecting = self.font.render(text, True, GRAY)
            self.screen.blit(connecting, (INITIAL_CAMERA_POS_X-(connecting.get_width()/2), INITIAL_CAMERA_POS_Y))


    def draw(self):
        self.screen.fill(BGCOLOR)
        ## Draw the scanned_points first so that they go under the robot
        self.draw_points()
        self.all_sprites.draw(self.screen)
        self.draw_text()
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_q:
                    self.quit()
                if event.key == pg.K_r:
                    self.robot.scanned_points = [self.robot.dummy_scan]
                    self.camera.x = -self.robot.pos.x + INITIAL_CAMERA_POS_X
                    self.camera.y = -self.robot.pos.y + INITIAL_CAMERA_POS_Y
                ## Move the camera
                if event.key == pg.K_a:
                    if not self.mode_text == self.modes["3"][0]:
                        self.camera.x -= 10
                    else:
                        self.robot.turn_left(STEERING_PORT, STEERING_SPEED)
                if event.key == pg.K_d:
                    if not self.mode_text == self.modes["3"][0]:
                        self.camera.x += 10
                    else:
                        self.robot.turn_right(STEERING_PORT, STEERING_SPEED)
                if event.key == pg.K_w:
                    if not self.mode_text == self.modes["3"][0]:
                        self.camera.y -= 10
                    else:
                        self.robot.turn_center(STEERING_PORT, STEERING_SPEED)
                if event.key == pg.K_s:
                    if not self.mode_text == self.modes["3"][0]:
                        self.camera.y += 10

                ## Switch modes
                if event.key == pg.K_1:
                    self.mode_text = self.modes["1"][0]
                if event.key == pg.K_2:
                    self.mode_text = self.modes["2"][0]
                if event.key == pg.K_3:
                    self.mode_text = self.modes["3"][0]
                    self.robot.speed = -100
                
                ## Change "nek"
                if event.key == pg.K_9 and self.robot.tracker_calibrated and self.mode_text == self.modes["3"][0]:
                    self.robot.tracker_state = False
                    self.robot.tracker_moved = False
                if event.key == pg.K_0 and self.robot.tracker_calibrated and self.mode_text == self.modes["3"][0]:
                    self.robot.tracker_state = True
                    self.robot.tracker_moved = False
                
            if event.type == self.robot.CHOOSE_ACTIVITY:
                self.robot.choose_event()

    def show_start_screen(self):
        pass

    def initialize_fonts(self):
        self.font = pg.font.SysFont(None, TEXT_SIZE)
        self.fonts_initiated = True


app = App()
