import pymunk

space = pymunk.Space() # 创建一个pymunk物理空间

body = pymunk.Body(body_type=pymunk.Body.STATIC) # 创建一个静态的“身体”
body.position = (100, 100) # 设置身体的位置

shape = pymunk.Circle(body, 20) # 创建一个半径为20像素的圆形的形状，并绑定其“身体”
shape.mass = 1 # 设置圆形的质量为1

space.add(body, shape) # 将身体和形状加入pymunk空间

if __name__ == "__main__":
    import util
    util.run(space) # 这里调用了util.py用于显示pymunk的运行结果