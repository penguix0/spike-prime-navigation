from settings import *
import pygame as pg
import sys
from Robot import Robot

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
    
    def draw_points(self):
        for point in self.robot.scanned_points:
            pass

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass


app = App()
