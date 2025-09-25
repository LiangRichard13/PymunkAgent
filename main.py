from pymunk_agent import PymunkAgent

if __name__ == "__main__":
    agent = PymunkAgent()
    # agent.run("创建一个斜面，角度不要太大，但够长，让一个非常有弹性的圆形自然放置在斜面的顶部(高的那一端)，并滑下来，然后落到一个平面上弹起")
    agent.run("创建一个平面，再做一个小车，矩形为车体，两个圆为轮子，将小车平稳放在该平面上")
    space = agent.tool_manager.sandbox.space
    import util
    util.run(space)