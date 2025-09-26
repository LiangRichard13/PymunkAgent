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
            self._create_pin_joint_tool(),
            self._create_impulse_tool(),
            self._create_force_tool(),
            self._create_set_position_tool(),
            self._create_get_position_tool(),
            self._create_remove_body_tool(),
            self._create_set_gravity_tool(),
            self._create_clear_all_tool(),
            self._create_set_properties_tool(),
            self._create_ground_tool(),
            self._create_slope_tool(),
            self._create_duplicate_body_tool(),
            self._create_car_tool(),
        ]
    
    def _create_circle_tool(self) -> Tool:
        """创建圆形工具"""
        def create_circle_wrapper(input_str: dict) -> str:
            try:
                print(f"创建圆形工具输入: {input_str}")
                params = input_str
                self.sandbox.create_circle(
                    name=params["name"],
                    position=tuple(params["position"]),
                    radius=params["radius"],
                    mass=params.get("mass", 1.0),
                    is_static=params.get("is_static", False)
                )
                return f"创建圆形成功！名称：{params['name']}，位置：{params['position']}，半径：{params['radius']}，质量：{params.get('mass', 1.0)}，是否静态：{params.get('is_static', False)}"
            except Exception as e:
                raise Exception(f"创建圆形时出错: {str(e)}")
        
        return Tool(
            name="create_circle",
            description="""创建一个圆形物理物体。
必需参数：
- name (string): 物体的唯一名称，用于后续引用
- position (array): 物体中心位置坐标 [x, y]，注意Pymunk使用y轴向下为正的坐标系统
- radius (number): 圆形半径，单位为像素

可选参数：
- mass (number): 物体质量，默认为1.0，单位为千克
- is_static (boolean): 是否为静态物体，默认为false。静态物体不会受重力影响，不能移动

注意事项：
- 当放置在斜面或平台上时，不要将物体放在边缘点上，这会导致物体直接掉落
- 示例：如果斜面从(100,300)到(500,400)，球应该放在(120,280)而不是(100,300)

JSON格式示例：{"name": "ball1", "position": [100, 200], "radius": 25, "mass": 2.0, "is_static": false}""",
            func=create_circle_wrapper
        )
    
    def _create_box_tool(self) -> Tool:
        """创建矩形工具"""
        def create_box_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.create_box(
                    name=params["name"],
                    position=tuple(params["position"]),
                    size=tuple(params["size"]),
                    mass=params.get("mass", 1.0),
                    is_static=params.get("is_static", False)
                )
            except Exception as e:
                raise Exception(f"创建矩形时出错: {str(e)}")
        
        return Tool(
            name="create_box",
            description="""创建一个矩形物理物体。
必需参数：
- name (string): 物体的唯一名称，用于后续引用
- position (array): 物体中心位置坐标 [x, y]，注意Pymunk使用y轴向下为正的坐标系统
- size (array): 矩形尺寸 [width, height]，单位为像素

可选参数：
- mass (number): 物体质量，默认为1.0，单位为千克
- is_static (boolean): 是否为静态物体，默认为false。静态物体不会受重力影响，不能移动

注意事项：
- 当放置在斜面或平台上时，不要将物体放在边缘点上，这会导致物体直接掉落
- 矩形会以position为中心点创建

JSON格式示例：{"name": "box1", "position": [150, 300], "size": [50, 30], "mass": 1.5, "is_static": false}""",
            func=create_box_wrapper
        )
    
    def _create_spring_joint_tool(self) -> Tool:
        """创建弹簧关节工具"""
        def create_spring_joint_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.add_spring_joint(
                    body1_name=params["body1_name"],
                    body2_name=params["body2_name"],
                    anchor1=tuple(params["anchor1"]),
                    anchor2=tuple(params["anchor2"]),
                    stiffness=params["stiffness"],
                    damping=params["damping"]
                )
            except Exception as e:
                raise Exception(f"创建弹簧关节时出错: {str(e)}")
        
        return Tool(
            name="add_spring_joint",
            description="""在两个物体之间添加弹簧关节连接，模拟弹簧的弹性行为。
必需参数：
- body1_name (string): 第一个物体的名称
- body2_name (string): 第二个物体的名称
- anchor1 (array): 第一个物体上的连接点 [x, y]，相对于物体中心
- anchor2 (array): 第二个物体上的连接点 [x, y]，相对于物体中心
- stiffness (number): 弹簧刚度，数值越大弹簧越硬，单位为N/m
- damping (number): 阻尼系数，数值越大阻尼越强，用于减少振荡

注意事项：
- 弹簧会尝试保持rest_length（默认50像素）的长度
- 刚度值建议范围：100-10000
- 阻尼值建议范围：1-100

JSON格式示例：{"body1_name": "ball1", "body2_name": "ball2", "anchor1": [0, 0], "anchor2": [0, 0], "stiffness": 1000, "damping": 10}""",
            func=create_spring_joint_wrapper
        )
    
    def _create_pin_joint_tool(self) -> Tool:
        """创建刚性连接工具"""
        def create_pin_joint_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.add_pin_joint(
                    body1_name=params["body1_name"],
                    body2_name=params["body2_name"],
                    anchor1=tuple(params["anchor1"]),
                    anchor2=tuple(params["anchor2"])
                )
            except Exception as e:
                raise Exception(f"创建刚性连接时出错: {str(e)}")
        
        return Tool(
            name="add_pin_joint",
            description="""在两个物体之间添加刚性连接（PinJoint），将两个物体在指定锚点处刚性固定。
必需参数：
- body1_name (string): 第一个物体的名称
- body2_name (string): 第二个物体的名称
- anchor1 (array): 第一个物体上的连接点 [x, y]，相对于物体中心
- anchor2 (array): 第二个物体上的连接点 [x, y]，相对于物体中心

注意事项：
- 这种连接就像用钉子将两个物体钉在一起，它们会保持相对位置不变
- 两个物体会一起移动和旋转，但连接点之间的距离和角度保持不变
- 适用于创建复合物体或刚性结构

JSON格式示例：{"body1_name": "ball1", "body2_name": "ball2", "anchor1": [0, 0], "anchor2": [0, 0]}""",
            func=create_pin_joint_wrapper
        )
    
    def _create_impulse_tool(self) -> Tool:
        """创建冲量工具"""
        def apply_impulse_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.apply_impulse(
                    body_name=params["body_name"],
                    impulse=tuple(params["impulse"])
                )
            except Exception as e:
                raise Exception(f"施加冲量时出错: {str(e)}")
        
        return Tool(
            name="apply_impulse",
            description="""对指定物体施加冲量（瞬间力），会立即改变物体的速度。
必需参数：
- body_name (string): 目标物体的名称
- impulse (array): 冲量向量 [x, y]，单位为kg⋅m/s

注意事项：
- 冲量是瞬间施加的力，会立即改变物体的速度
- x分量：正值向右，负值向左
- y分量：正值向下，负值向上
- 冲量大小影响速度变化的程度
- 适用于模拟碰撞、爆炸、弹射等瞬间力效果

JSON格式示例：{"body_name": "ball1", "impulse": [100, -50]}""",
            func=apply_impulse_wrapper
        )
    
    def _create_force_tool(self) -> Tool:
        """创建力工具"""
        def apply_force_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.apply_force(
                    body_name=params["body_name"],
                    force=tuple(params["force"])
                )
            except Exception as e:
                raise Exception(f"施加力时出错: {str(e)}")
        
        return Tool(
            name="apply_force",
            description="""对指定物体施加持续的力，会在每个物理步进中持续作用。
必需参数：
- body_name (string): 目标物体的名称
- force (array): 力向量 [x, y]，单位为牛顿(N)

注意事项：
- 力会持续作用，直到被其他力抵消或物体被移除
- x分量：正值向右，负值向左
- y分量：正值向下，负值向上
- 适用于模拟推力、风力、磁力等持续力
- 力的大小影响加速度的大小（F=ma）

JSON格式示例：{"body_name": "ball1", "force": [0, -100]}""",
            func=apply_force_wrapper
        )
    
    def _create_set_position_tool(self) -> Tool:
        """创建设置位置工具"""
        def set_position_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.set_position(
                    body_name=params["body_name"],
                    position=tuple(params["position"])
                )
            except Exception as e:
                raise Exception(f"设置位置时出错: {str(e)}")
        
        return Tool(
            name="set_position",
            description="""设置指定物体的位置，会立即将物体移动到新位置。
必需参数：
- body_name (string): 目标物体的名称
- position (array): 新位置坐标 [x, y]，注意Pymunk使用y轴向下为正的坐标系统

注意事项：
- 这会立即改变物体的位置，不会影响物体的速度
- 如果物体与其他物体有碰撞，可能会产生碰撞反应
- 适用于重置物体位置或精确放置

JSON格式示例：{"body_name": "ball1", "position": [200, 150]}""",
            func=set_position_wrapper
        )
    
    def _create_get_position_tool(self) -> Tool:
        """创建获取位置工具"""
        def get_position_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.get_position(params["body_name"])
            except Exception as e:
                raise Exception(f"获取位置时出错: {str(e)}")
        
        return Tool(
            name="get_position",
            description="""获取指定物体的当前位置坐标。
必需参数：
- body_name (string): 目标物体的名称

返回值：
- 返回物体当前的中心位置坐标 [x, y]
- 坐标系统：Pymunk使用y轴向下为正的坐标系统

注意事项：
- 只能获取动态物体的位置
- 静态物体的位置通常为(0,0)

JSON格式示例：{"body_name": "ball1"}""",
            func=get_position_wrapper
        )
    
    def _create_remove_body_tool(self) -> Tool:
        """创建删除物体工具"""
        def remove_body_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.remove_body(params["body_name"])
            except Exception as e:
                raise Exception(f"删除物体时出错: {str(e)}")
        
        return Tool(
            name="remove_body",
            description="""删除指定的物理物体，将其从物理世界中完全移除。
必需参数：
- body_name (string): 要删除的物体名称

注意事项：
- 删除后物体将不再参与物理模拟
- 与该物体相关的所有关节和约束也会被移除
- 无法撤销此操作
- 适用于清理不需要的物体

JSON格式示例：{"body_name": "ball1"}""",
            func=remove_body_wrapper
        )
    
    def _create_set_gravity_tool(self) -> Tool:
        """创建设置重力工具"""
        def set_gravity_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.set_gravity(tuple(params["gravity"]))
            except Exception as e:
                raise Exception(f"设置重力时出错: {str(e)}")
        
        return Tool(
            name="set_gravity",
            description="""设置物理世界的重力向量，影响所有动态物体。
必需参数：
- gravity (array): 重力向量 [x, y]，单位为像素/秒²

注意事项：
- x分量：正值向右，负值向左
- y分量：正值向下，负值向上
- 标准地球重力约为(0, 981)像素/秒²
- 设置为(0, 0)可以创建无重力环境
- 重力会影响所有动态物体，静态物体不受影响

JSON格式示例：{"gravity": [0, 981]}""",
            func=set_gravity_wrapper
        )
    
    def _create_clear_all_tool(self) -> Tool:
        """创建清空所有物体工具"""
        def clear_all_wrapper() -> str:
            try:
                return self.sandbox.clear_all()
            except Exception as e:
                raise Exception(f"清空物体时出错: {str(e)}")
        
        return Tool(
            name="clear_all_bodies",
            description="""清空物理世界中的所有物体，重置物理环境。
参数：无需参数

注意事项：
- 会删除所有动态和静态物体
- 会移除所有关节和约束
- 重力设置会保持不变
- 无法撤销此操作
- 适用于开始新的物理实验或清理场景

调用方式：直接调用，无需JSON参数""",
            func=clear_all_wrapper
        )
    
    def _create_set_properties_tool(self) -> Tool:
        """创建设置物体属性工具"""
        def set_properties_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                body_name = params["body_name"]
                properties = {k: v for k, v in params.items() if k != "body_name"}
                return self.sandbox.set_body_properties(body_name, **properties)
            except Exception as e:
                raise Exception(f"设置物体属性时出错: {str(e)}")
        
        return Tool(
            name="set_body_properties",
            description="""设置物体的物理属性，包括质量、摩擦系数、弹性系数、速度等。
必需参数：
- body_name (string): 目标物体的名称

可选属性参数：
- mass (number): 物体质量，必须为正数，单位为千克
- friction (number): 摩擦系数，0-1之间，0表示无摩擦，1表示完全摩擦
- elasticity (number): 弹性系数，0-1之间，0表示完全非弹性，1表示完全弹性
- velocity (array): 速度向量 [x, y]，单位为像素/秒
- angular_velocity (number): 角速度，单位为弧度/秒

注意事项：
- 可以同时设置多个属性
- 质量改变会重新计算转动惯量
- 速度设置会立即生效

JSON格式示例：{"body_name": "ball1", "mass": 2.0, "friction": 0.8, "elasticity": 0.5, "velocity": [10, 0], "angular_velocity": 1.0}""",
            func=set_properties_wrapper
        )
    
    def _create_ground_tool(self) -> Tool:
        """创建地面工具"""
        def create_ground_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.create_ground(
                    name=params["name"],
                    start_point=tuple(params["start_point"]),
                    end_point=tuple(params["end_point"]),
                    friction=params.get("friction", 0.7),
                    elasticity=params.get("elasticity", 0.3)
                )
            except Exception as e:
                raise Exception(f"创建地面时出错: {str(e)}")
        
        return Tool(
            name="create_ground",
            description="""创建地面（静态线段），作为物理世界的边界或平台。
必需参数：
- name (string): 地面的唯一名称
- start_point (array): 起始点坐标 [x, y]
- end_point (array): 结束点坐标 [x, y]

可选参数：
- friction (number): 摩擦系数，默认为0.7，0-1之间
- elasticity (number): 弹性系数，默认为0.3，0-1之间

注意事项：
- 地面是静态的，不会移动或受重力影响
- 可以创建水平、垂直或倾斜的地面
- 物体与地面碰撞时会受到摩擦和弹性影响
- 适用于创建边界、平台、墙壁等

JSON格式示例：{"name": "ground1", "start_point": [0, 400], "end_point": [800, 400], "friction": 0.7, "elasticity": 0.3}""",
            func=create_ground_wrapper
        )
    
    def _create_slope_tool(self) -> Tool:
        """创建斜面工具"""
        def create_slope_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.create_slope(
                    name=params["name"],
                    start_point=tuple(params["start_point"]),
                    end_point=tuple(params["end_point"]),
                    friction=params.get("friction", 0.7),
                    elasticity=params.get("elasticity", 0.3)
                )
            except Exception as e:
                raise Exception(f"创建斜面时出错: {str(e)}")
        
        return Tool(
            name="create_slope",
            description="""创建斜面（静态线段），用于模拟斜坡、滑道等倾斜表面。
必需参数：
- name (string): 斜面的唯一名称
- start_point (array): 起始点坐标 [x, y]，通常是较高的一端
- end_point (array): 结束点坐标 [x, y]，通常是较低的一端

可选参数：
- friction (number): 摩擦系数，默认为0.7，0-1之间
- elasticity (number): 弹性系数，默认为0.3，0-1之间

注意事项：
- 斜面是静态的，不会移动或受重力影响
- 物体在斜面上会受到重力分量影响而滑动
- 摩擦系数影响滑动速度，弹性系数影响碰撞反弹
- 当在斜面上放置物体时，不要放在边缘点上
- 适用于创建滑道、斜坡、坡道等

JSON格式示例：{"name": "slope1", "start_point": [100, 300], "end_point": [500, 400], "friction": 0.5, "elasticity": 0.2}""",
            func=create_slope_wrapper
        )
    
    def _create_duplicate_body_tool(self) -> Tool:
        """创建复制物体工具"""
        def duplicate_body_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.duplicate_body(
                    original_name=params["original_name"],
                    count=params["count"],
                    offset=tuple(params.get("offset", [50, 0]))
                )
            except Exception as e:
                raise Exception(f"复制物体时出错: {str(e)}")
        
        return Tool(
            name="duplicate_body",
            description="""复制指定物体成多个副本，自动命名为原名_copy_1、原名_copy_2等。
必需参数：
- original_name (string): 要复制的原始物体名称
- count (number): 复制数量，必须大于0

可选参数：
- offset (array): 每个副本之间的偏移量 [x, y]，默认为[50, 0]

注意事项：
- 复制会保持原始物体的所有属性（质量、摩擦系数、弹性系数、速度等）
- 副本会按照偏移量依次排列
- 支持复制圆形、矩形、地面、斜面等所有类型的物体
- 副本名称格式：原名_copy_1、原名_copy_2、原名_copy_3...
- 如果副本名称已存在，操作会失败

JSON格式示例：{"original_name": "ball1", "count": 3, "offset": [60, 0]}""",
            func=duplicate_body_wrapper
        )
    
    def _create_car_tool(self) -> Tool:
        """创建小车工具"""
        def create_car_wrapper(input_str: dict) -> str:
            try:
                params = input_str
                return self.sandbox.create_car(
                    name=params["name"],
                    position=tuple(params["position"]),
                    chassis_size=tuple(params.get("chassis_size", [50, 20])),
                    wheel_radius=params.get("wheel_radius", 10),
                    chassis_mass=params.get("chassis_mass", 10),
                    wheel_mass=params.get("wheel_mass", 2)
                )
            except Exception as e:
                raise Exception(f"创建小车时出错: {str(e)}")
        
        return Tool(
            name="create_car",
            description="""创建一个小车，包含车身和两个轮子，通过关节连接。
必需参数：
- name (string): 小车的唯一名称
- position (array): 车身中心位置 [x, y]，注意Pymunk使用y轴向下为正的坐标系统

可选参数：
- chassis_size (array): 车身尺寸 [width, height]，默认为[50, 20]
- wheel_radius (number): 轮子半径，默认为10
- chassis_mass (number): 车身质量，默认为10
- wheel_mass (number): 轮子质量，默认为2

注意事项：
- 小车由车身和两个轮子组成，通过PivotJoint关节连接
- 轮子会自动放置在车身下方，距离车身边缘10像素
- 轮子具有高摩擦系数(1.0)，适合在平面上行驶
- 车身具有中等摩擦系数(0.7)和低弹性系数(0.1)
- 在设置小车位置时，需要为车身下的轮子留出足够空间
- 建议小车位置y坐标至少比地面高30-50像素，确保轮子不嵌入地面
- 小车创建后，轮子会自动命名为：小车名_wheel1、小车名_wheel2

JSON格式示例：{"name": "car1", "position": [200, 100], "chassis_size": [60, 25], "wheel_radius": 12, "chassis_mass": 15, "wheel_mass": 3}""",
            func=create_car_wrapper
        )
    
    def get_tools_description(self) -> List[str]:
        """获取所有工具描述列表"""
        return [f"tool_name: {tool.name}, tool_description: {tool.description}" for tool in self.tools]

    def get_tools(self) -> List[Tool]:
        """获取所有工具列表 (工具对象列表) """
        return self.tools
    
    def get_sandbox_status(self) -> PhysicsSandbox:
        """获取物理沙盒状态"""
        return self.sandbox.get_space_status()