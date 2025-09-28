## util.py
import pygame as pg
import sys
from pymunk.pygame_util import DrawOptions

background = (255, 255, 255) # white
fps = 60

def init_pygame_display(width=1000, height=600):
    """初始化Pygame显示"""
    screen = pg.display.set_mode((width, height))
    draw_options = DrawOptions(screen)
    clock = pg.time.Clock()
    return screen, draw_options, clock

def run(space, func=None, width=1000, height=600):
    """运行Pygame显示循环"""
    # 初始化Pygame显示
    screen, draw_options, clock = init_pygame_display(width, height)
    
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
