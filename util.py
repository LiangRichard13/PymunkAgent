## util.py
import pygame as pg
import sys
from pymunk.pygame_util import DrawOptions

background = (255, 255, 255) # white
fps = 60

screen = pg.display.set_mode((1000, 600))
draw_options = DrawOptions(screen)

clock = pg.time.Clock()

def run(space, func=None):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        if func:
            s = str(func())
        else:
            s = "FPS: {}".format(clock.get_fps())

        pg.display.set_caption(s)
        screen.fill(background)
        
        space.debug_draw(draw_options)
        space.step(1 / fps)

        pg.display.flip()
        clock.tick(fps)