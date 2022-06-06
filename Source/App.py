from settings import *
import pygame as pg
import sys
from Robot import Robot
from camera import Camera
import threading

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(DISPLAY_SIZE)
        pg.display.set_caption(TITLE)
        self.icon = pg.image.load('icon.png')
        pg.display.set_icon(self.icon)
        self.clock = pg.time.Clock()

        self.fonts_initiated = False

        self.deltaTime = 0
        self.getTicksLastFrame = 0

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
        
        self.user_text = ''

        create_fonts = threading.Thread(target=self.initialize_fonts())
        create_fonts.start()

    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            t = pg.time.get_ticks()
            # deltaTime in seconds.
            self.deltaTime = (t - self.getTicksLastFrame) / 1000.0
            self.getTicksLastFrame = t

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
            speed = self.font.render('Speed: ' + str(round(self.robot.real_world_speed, 3)) + ' m/s', True, GRAY)
            self.screen.blit(speed, (20, 40))
            distance_droven = self.font.render("Distance driven: " + str(round(self.robot.distance_droven, 1)) + " m", True, GRAY)
            self.screen.blit(distance_droven, (20, 60))
            resistance = self.font.render('Motor resistance: ' + str(self.robot.get_motor_stall(MOTOR_NUMERIC_PORT)), True, GRAY)
            self.screen.blit(resistance, (20, 80))
            sensor_angle = self.font.render('Sensor angle: ' + str(self.robot.servo_sensor_angle), True, GRAY)
            self.screen.blit(sensor_angle, (20, 100))
            user_console = self.font.render(self.user_text, True, WHITE)
            self.screen.blit(user_console, (20, 700))
            
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
                if event.key == pg.K_0:
                    self.robot.scanned_points = [self.robot.dummy_scan]
                    self.camera.x = -self.robot.pos.x + INITIAL_CAMERA_POS_X
                    self.camera.y = -self.robot.pos.y + INITIAL_CAMERA_POS_Y


    def show_start_screen(self):
        pass

    def initialize_fonts(self):
        self.font = pg.font.SysFont(None, TEXT_SIZE)
        self.fonts_initiated = True


app = App()
