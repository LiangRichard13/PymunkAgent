"""
Pymunk物理引擎的LangChain工具注册
将PhysicsSandbox的方法封装为LangChain工具，供AI Agent调用
"""

from langchain.tools import Tool
from typing import Dict, Any, List
import json
from physics_sandbox import PhysicsSandbox


class PymunkToolManager:
    """Pymunk工具管理器，管理物理沙盒实例和工具注册"""
    
    def __init__(self):
        self.sandbox = PhysicsSandbox()
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[Tool]:
        """创建所有Pymunk工具"""
        return [
            self._create_circle_tool(),
            self._create_box_tool(),
            self._create_spring_joint_tool(),
            self._create_impulse_tool(),
            self._create_force_tool(),
            self._create_set_position_tool(),
            self._create_get_position_tool(),
            self._create_remove_body_tool(),
            self._create_set_gravity_tool(),
            self._create_step_tool(),
            self._create_get_all_bodies_tool(),
            self._create_clear_all_tool(),
        ]
    
    def _create_circle_tool(self) -> Tool:
        """创建圆形工具"""
        def create_circle_wrapper(input_str: str) -> str:
            try:
                print(f"创建圆形工具输入: {input_str}")
                params = json.loads(input_str)
                self.sandbox.create_circle(
                    name=params["name"],
                    position=tuple(params["position"]),
                    radius=params["radius"],
                    mass=params.get("mass", 1.0),
                    is_static=params.get("is_static", False)
                )
                return f"创建圆形成功！名称：{params['name']}，位置：{params['position']}，半径：{params['radius']}，质量：{params.get('mass', 1.0)}，是否静态：{params.get('is_static', False)}"
            except Exception as e:
                return f"创建圆形时出错: {str(e)}"
        
        return Tool(
            name="create_circle",
            description="创建一个圆形物理物体。需要提供name(名称)、position(位置)、radius(半径)参数，可选mass(质量)和is_static(是否静态)参数。请输出JSON格式，示例：{\"name\": \"ball1\", \"position\": [100, 200], \"radius\": 25, \"mass\": 2.0, \"is_static\": false}",
            func=create_circle_wrapper
        )
    
    def _create_box_tool(self) -> Tool:
        """创建矩形工具"""
        def create_box_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.create_box(
                    name=params["name"],
                    position=tuple(params["position"]),
                    size=tuple(params["size"]),
                    mass=params.get("mass", 1.0),
                    is_static=params.get("is_static", False)
                )
            except Exception as e:
                return f"创建矩形时出错: {str(e)}"
        
        return Tool(
            name="create_box",
            description="创建一个矩形物理物体。需要提供name(名称)、position(位置)、size(尺寸)参数，可选mass(质量)和is_static(是否静态)参数。请输出JSON格式，示例：{\"name\": \"box1\", \"position\": [150, 300], \"size\": [50, 30], \"mass\": 1.5, \"is_static\": false}",
            func=create_box_wrapper
        )
    
    def _create_spring_joint_tool(self) -> Tool:
        """创建弹簧关节工具"""
        def create_spring_joint_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.add_spring_joint(
                    body1_name=params["body1_name"],
                    body2_name=params["body2_name"],
                    anchor1=tuple(params["anchor1"]),
                    anchor2=tuple(params["anchor2"]),
                    stiffness=params["stiffness"],
                    damping=params["damping"]
                )
            except Exception as e:
                return f"创建弹簧关节时出错: {str(e)}"
        
        return Tool(
            name="add_spring_joint",
            description="在两个物体之间添加弹簧关节连接。需要提供body1_name、body2_name、anchor1、anchor2、stiffness、damping参数。请输出JSON格式，示例：{\"body1_name\": \"ball1\", \"body2_name\": \"ball2\", \"anchor1\": [0, 0], \"anchor2\": [0, 0], \"stiffness\": 1000, \"damping\": 10}",
            func=create_spring_joint_wrapper
        )
    
    def _create_impulse_tool(self) -> Tool:
        """创建冲量工具"""
        def apply_impulse_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.apply_impulse(
                    body_name=params["body_name"],
                    impulse=tuple(params["impulse"])
                )
            except Exception as e:
                return f"施加冲量时出错: {str(e)}"
        
        return Tool(
            name="apply_impulse",
            description="对指定物体施加冲量（瞬间力）。需要提供body_name和impulse参数。请输出JSON格式，示例：{\"body_name\": \"ball1\", \"impulse\": [100, -50]}",
            func=apply_impulse_wrapper
        )
    
    def _create_force_tool(self) -> Tool:
        """创建力工具"""
        def apply_force_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.apply_force(
                    body_name=params["body_name"],
                    force=tuple(params["force"])
                )
            except Exception as e:
                return f"施加力时出错: {str(e)}"
        
        return Tool(
            name="apply_force",
            description="对指定物体施加持续的力。需要提供body_name和force参数。请输出JSON格式，示例：{\"body_name\": \"ball1\", \"force\": [0, -100]}",
            func=apply_force_wrapper
        )
    
    def _create_set_position_tool(self) -> Tool:
        """创建设置位置工具"""
        def set_position_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.set_position(
                    body_name=params["body_name"],
                    position=tuple(params["position"])
                )
            except Exception as e:
                return f"设置位置时出错: {str(e)}"
        
        return Tool(
            name="set_position",
            description="设置指定物体的位置。需要提供body_name和position参数。请输出JSON格式，示例：{\"body_name\": \"ball1\", \"position\": [200, 150]}",
            func=set_position_wrapper
        )
    
    def _create_get_position_tool(self) -> Tool:
        """创建获取位置工具"""
        def get_position_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.get_position(params["body_name"])
            except Exception as e:
                return f"获取位置时出错: {str(e)}"
        
        return Tool(
            name="get_position",
            description="获取指定物体的当前位置。需要提供body_name参数。请输出JSON格式，示例：{\"body_name\": \"ball1\"}",
            func=get_position_wrapper
        )
    
    def _create_remove_body_tool(self) -> Tool:
        """创建删除物体工具"""
        def remove_body_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.remove_body(params["body_name"])
            except Exception as e:
                return f"删除物体时出错: {str(e)}"
        
        return Tool(
            name="remove_body",
            description="删除指定的物理物体。需要提供body_name参数。请输出JSON格式，示例：{\"body_name\": \"ball1\"}",
            func=remove_body_wrapper
        )
    
    def _create_set_gravity_tool(self) -> Tool:
        """创建设置重力工具"""
        def set_gravity_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                return self.sandbox.set_gravity(tuple(params["gravity"]))
            except Exception as e:
                return f"设置重力时出错: {str(e)}"
        
        return Tool(
            name="set_gravity",
            description="设置物理世界的重力。需要提供gravity参数。请输出JSON格式，示例：{\"gravity\": [0, -981]}",
            func=set_gravity_wrapper
        )
    
    def _create_step_tool(self) -> Tool:
        """创建物理步进工具"""
        def step_wrapper(input_str: str) -> str:
            try:
                params = json.loads(input_str)
                dt = params.get("dt", 1/60.0)
                return self.sandbox.step(dt)
            except Exception as e:
                return f"执行物理步进时出错: {str(e)}"
        
        return Tool(
            name="step_physics",
            description="执行一步物理模拟计算。可选提供dt参数。请输出JSON格式，示例：{\"dt\": 0.016} 或 {}",
            func=step_wrapper
        )
    
    def _create_get_all_bodies_tool(self) -> Tool:
        """创建获取所有物体工具"""
        def get_all_bodies_wrapper(input_str: str) -> str:
            try:
                return self.sandbox.get_all_bodies()
            except Exception as e:
                return f"获取物体列表时出错: {str(e)}"
        
        return Tool(
            name="get_all_bodies",
            description="获取当前物理世界中所有物体的信息。无需参数。",
            func=get_all_bodies_wrapper
        )
    
    def _create_clear_all_tool(self) -> Tool:
        """创建清空所有物体工具"""
        def clear_all_wrapper(input_str: str) -> str:
            try:
                return self.sandbox.clear_all()
            except Exception as e:
                return f"清空物体时出错: {str(e)}"
        
        return Tool(
            name="clear_all_bodies",
            description="清空物理世界中的所有物体。无需参数。",
            func=clear_all_wrapper
        )
    
    def get_tools(self) -> List[Tool]:
        """获取所有工具列表"""
        return self.tools
    
    def get_sandbox(self) -> PhysicsSandbox:
        """获取物理沙盒实例"""
        return self.sandbox


# 便捷函数：创建工具管理器实例
# def create_pymunk_tools() -> PymunkToolManager:
#     """创建Pymunk工具管理器实例"""
#     return PymunkToolManager()


# 示例：如何注册到LangChain Agent
def register_tools_to_agent():
    """演示如何将工具注册到LangChain Agent"""
    from langchain.agents import initialize_agent, AgentType
    from langchain_openai import ChatOpenAI
    from llm_config import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY

    # 创建工具管理器
    tool_manager = PymunkToolManager()
    tools = tool_manager.get_tools()
    
    # 创建LLM (需要设置OPENAI_API_KEY)
    llm = ChatOpenAI(base_url=LLM_BASE_URL, model=LLM_MODEL, api_key=LLM_API_KEY)
    
    # 创建Agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        early_stopping_method="generate"
    )
    
    return agent, tool_manager


if __name__ == "__main__":
    # 测试工具创建
    # tool_manager = create_pymunk_tools()
    # tools = tool_manager.get_tools()
    
    # print(f"成功创建了 {len(tools)} 个Pymunk工具:")
    # for tool in tools:
    #     print(f"- {tool.name}: {tool.description[:50]}...")

    # agent, tool_manager = register_tools_to_agent()
    tool_manager = PymunkToolManager()
    tools = tool_manager.get_tools()
    
    # 先测试工具是否正常工作
    print("=== 测试工具功能 ===")
    tools = tool_manager.get_tools()
    print(f"可用工具数量: {len(tools)}")
    print(tools)
    
    response={
        "tool_name": "create_circle",
        "tool_input": '{"name": "ball1", "position": [100, 200], "radius": 25, "mass": 2.0, "is_static": false}'
    }
    find_tool = next((tool for tool in tools if tool.name == response["tool_name"]), None)
    if find_tool:
        result = find_tool.func(response["tool_input"])
        print(result)
    else:
        print(f"未找到工具: {response["tool_name"]}")

    # 测试Agent
    # print("\n=== 测试Agent ===")
    # try:
    #     result = agent.invoke({"input": "创建一个名为ball1的圆形，位置在(100,200)，半径25，静态"})
    #     print("Agent执行结果:", result)
    # except Exception as e:
    #     print(f"Agent执行失败: {e}")

    # from physics_sandbox import PhysicsSandbox
    # sanbox = PhysicsSandbox()
    # sanbox.create_circle("ball1", (100, 200), 25)
    # space = sanbox.space
    space = tool_manager.get_sandbox().space
    
    import util
    util.run(space) 