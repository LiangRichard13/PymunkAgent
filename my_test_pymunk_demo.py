import pymunk
import pymunk.pygame_util
import pygame
import sys

# 初始化pygame和pymunk
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, 900)  # 设置重力方向向下

# 创建绘图选项
draw_options = pymunk.pygame_util.DrawOptions(screen)

# 创建地面（平面）
def create_ground():
    ground = pymunk.Segment(space.static_body, (0, 400), (800, 500), 5)
    ground.friction = 5.0  # 设置地面摩擦力
    space.add(ground)
    return ground

# 创建小车
def create_car():
    # 创建车体（矩形）
    car_body = pymunk.Body(100, pymunk.moment_for_box(100, (150, 50)))
    car_body.position = 100, 300
    car_shape = pymunk.Poly.create_box(car_body, (150, 50))
    car_shape.friction = 0.7
    
    # 创建前轮（圆形）
    wheel1 = pymunk.Body(20, pymunk.moment_for_circle(20, 0, 30))
    wheel1.position = car_body.position[0] - 50, car_body.position[1] + 60
    wheel_shape1 = pymunk.Circle(wheel1, 30)
    wheel_shape1.friction = 1.0
    
    # 创建后轮（圆形）
    wheel2 = pymunk.Body(20, pymunk.moment_for_circle(20, 0, 30))
    wheel2.position = car_body.position[0] + 50, car_body.position[1] + 60
    wheel_shape2 = pymunk.Circle(wheel2, 30)
    wheel_shape2.friction = 1.0
    
    # 将形状添加到空间
    space.add(car_body, car_shape)
    space.add(wheel1, wheel_shape1)
    space.add(wheel2, wheel_shape2)
    
    # 创建悬挂关节（将轮子连接到车体）
    spring1 = pymunk.PinJoint(car_body, wheel1, (-50, -25), (0, 0))
    spring2 = pymunk.PinJoint(car_body, wheel2, (50, -25), (0, 0))
    spring3 = pymunk.PinJoint(car_body, wheel1, (50, -25), (0, 0))
    spring4 = pymunk.PinJoint(car_body, wheel2, (-50, -25), (0, 0))

    space.add(spring1, spring2, spring3, spring4)
    
    return car_body, wheel1, wheel2

# 创建场景
ground = create_ground()
car_body, wheel1, wheel2 = create_car()

# 施加向右的冲量
# car_body.apply_force_at_local_point((10000, 0))  # 在车体中心施加向右的冲量

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 清屏
    screen.fill((255, 255, 255))
    
    # 更新物理引擎
    space.step(1/60.0)
    
    # 绘制场景
    space.debug_draw(draw_options)
    
    # 显示一些信息
    font = pygame.font.Font(None, 30)
    text = font.render("小车受到向右的冲量", True, (0, 0, 0))
    screen.blit(text, (20, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()