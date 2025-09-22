import pymunk
import pymunk.pygame_util
from typing import Dict, Tuple, Optional


class PhysicsSandbox:
    """
    物理沙盒类，封装Pymunk的功能，用于agent的工具调用
    """
    
    def __init__(self, gravity: Tuple[float, float] = (0, 981)):
        """
        初始化物理沙盒
        
        Args:
            gravity: 重力向量，默认为(0, 981)表示向下980像素/秒²
        """
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.bodies: Dict[str, pymunk.Body] = {}  # 用字典来管理人机交互中的物体
        self.shapes: Dict[str, pymunk.Shape] = {}  # 存储形状信息
        
    def create_circle(self, name: str, position: Tuple[float, float], radius: float, 
                     mass: float = 1.0, is_static: bool = False) -> str:
        """
        创建圆形物体
        
        Args:
            name: 物体名称
            position: 位置坐标 (x, y)
            radius: 半径
            mass: 质量
            is_static: 是否为静态物体
            
        Returns:
            操作结果信息
        """
        if name in self.bodies:
            return f"错误：名为'{name}'的物体已存在。"
            
        # 创建身体
        if is_static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            moment = pymunk.moment_for_circle(mass, 0, radius)
            body = pymunk.Body(mass, moment)
            
        body.position = position
        
        # 创建形状
        shape = pymunk.Circle(body, radius)
        shape.friction = 0.7
        shape.elasticity = 0.3
        
        # 添加到空间
        self.space.add(body, shape)
        
        # 存储引用
        self.bodies[name] = body
        self.shapes[name] = shape
        
        return f"成功创建名为'{name}'的圆形，位置({position[0]:.1f}, {position[1]:.1f})，半径{radius}。"
    
    def create_box(self, name: str, position: Tuple[float, float], size: Tuple[float, float], 
                  mass: float = 1.0, is_static: bool = False) -> str:
        """
        创建矩形物体
        
        Args:
            name: 物体名称
            position: 位置坐标 (x, y)
            size: 尺寸 (width, height)
            mass: 质量
            is_static: 是否为静态物体
            
        Returns:
            操作结果信息
        """
        if name in self.bodies:
            return f"错误：名为'{name}'的物体已存在。"
            
        # 创建身体
        if is_static:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            moment = pymunk.moment_for_box(mass, size)
            body = pymunk.Body(mass, moment)
            
        body.position = position
        
        # 创建形状
        shape = pymunk.Poly.create_box(body, size)
        shape.friction = 0.7
        shape.elasticity = 0.3
        
        # 添加到空间
        self.space.add(body, shape)
        
        # 存储引用
        self.bodies[name] = body
        self.shapes[name] = shape
        
        return f"成功创建名为'{name}'的矩形，位置({position[0]:.1f}, {position[1]:.1f})，尺寸{size}。"
    
    def add_spring_joint(self, body1_name: str, body2_name: str, 
                        anchor1: Tuple[float, float], anchor2: Tuple[float, float],
                        stiffness: float, damping: float) -> str:
        """
        在两个物体之间添加弹簧关节
        
        Args:
            body1_name: 第一个物体名称
            body2_name: 第二个物体名称
            anchor1: 第一个物体的锚点
            anchor2: 第二个物体的锚点
            stiffness: 弹簧刚度
            damping: 阻尼系数
            
        Returns:
            操作结果信息
        """
        if body1_name not in self.bodies:
            return f"错误：名为'{body1_name}'的物体不存在。"
        if body2_name not in self.bodies:
            return f"错误：名为'{body2_name}'的物体不存在。"
            
        body1 = self.bodies[body1_name]
        body2 = self.bodies[body2_name]
        
        # 创建弹簧关节
        spring = pymunk.DampedSpring(body1, body2, anchor1, anchor2, 
                                   rest_length=50, stiffness=stiffness, damping=damping)
        
        # 添加到空间
        self.space.add(spring)
        
        return f"成功在'{body1_name}'和'{body2_name}'之间添加了弹簧关节。"
    
    def apply_impulse(self, body_name: str, impulse: Tuple[float, float]) -> str:
        """
        对指定物体施加冲量
        
        Args:
            body_name: 物体名称
            impulse: 冲量向量 (x, y)
            
        Returns:
            操作结果信息
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        body.apply_impulse_at_local_point(impulse)
        
        return f"已对'{body_name}'施加冲量({impulse[0]:.1f}, {impulse[1]:.1f})。"
    
    def apply_force(self, body_name: str, force: Tuple[float, float]) -> str:
        """
        对指定物体施加力
        
        Args:
            body_name: 物体名称
            force: 力向量 (x, y)
            
        Returns:
            操作结果信息
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        body.apply_force_at_local_point(force)
        
        return f"已对'{body_name}'施加力({force[0]:.1f}, {force[1]:.1f})。"
    
    def set_position(self, body_name: str, position: Tuple[float, float]) -> str:
        """
        设置物体位置
        
        Args:
            body_name: 物体名称
            position: 新位置 (x, y)
            
        Returns:
            操作结果信息
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        body.position = position
        
        return f"已将'{body_name}'移动到位置({position[0]:.1f}, {position[1]:.1f})。"
    
    def get_position(self, body_name: str) -> str:
        """
        获取物体位置
        
        Args:
            body_name: 物体名称
            
        Returns:
            位置信息字符串
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        pos = body.position
        
        return f"'{body_name}'的当前位置：({pos.x:.1f}, {pos.y:.1f})"
    
    def remove_body(self, body_name: str) -> str:
        """
        删除指定物体
        
        Args:
            body_name: 物体名称
            
        Returns:
            操作结果信息
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        shape = self.shapes[body_name]
        
        # 从空间中移除
        self.space.remove(body, shape)
        
        # 从字典中删除
        del self.bodies[body_name]
        del self.shapes[body_name]
        
        return f"已删除名为'{body_name}'的物体。"
    
    def set_gravity(self, gravity: Tuple[float, float]) -> str:
        """
        设置重力
        
        Args:
            gravity: 重力向量 (x, y)
            
        Returns:
            操作结果信息
        """
        self.space.gravity = gravity
        return f"重力已设置为({gravity[0]:.1f}, {gravity[1]:.1f})。"
    
    def step(self, dt: float = 1/60.0) -> str:
        """
        执行一步物理模拟
        
        Args:
            dt: 时间步长
            
        Returns:
            操作结果信息
        """
        self.space.step(dt)
        return f"执行了物理模拟步骤，时间步长：{dt:.4f}秒。"
    
    def get_all_bodies(self) -> str:
        """
        获取所有物体信息
        
        Returns:
            所有物体的信息字符串
        """
        if not self.bodies:
            return "当前没有物体。"
            
        info = "当前物体列表：\n"
        for name, body in self.bodies.items():
            pos = body.position
            info += f"- {name}: 位置({pos.x:.1f}, {pos.y:.1f})\n"
            
        return info.strip()
    
    def clear_all(self) -> str:
        """
        清空所有物体
        
        Returns:
            操作结果信息
        """
        # 从空间中移除所有物体
        for body, shape in zip(self.bodies.values(), self.shapes.values()):
            self.space.remove(body, shape)
            
        # 清空字典
        self.bodies.clear()
        self.shapes.clear()
        
        return "已清空所有物体。"