from pymunk_agent import PymunkAgent

if __name__ == "__main__":
    agent = PymunkAgent()
    agent.run("创建一个比较长的斜面，在斜面的末尾连接一个平面，平面的末尾放一个较轻的圆形，再做一个小车，矩形为车体，两个圆为轮子，将小车平稳放在该斜面上，让其自然受重力滑下，最后撞飞圆形")
    space = agent.tool_manager.sandbox.space
    import util
    util.run(space)