from pymunk_agent import PymunkAgent

if __name__ == "__main__":
    agent = PymunkAgent()
    agent.run("创建一个名为ball的圆形，位置固定，半径30")
    space = agent.tool_manager.sandbox.space
    import util
    util.run(space)