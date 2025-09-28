import pymunk
import math
from typing import Dict, Tuple, Optional
import pymunk.pygame_util


class PhysicsSandbox:
    """
    物理沙盒类，封装Pymunk的功能，用于agent的工具调用
    
    注意：Pymunk使用y轴向下为正的坐标系统
    - x轴：向右为正
    - y轴：向下为正
    - 原点(0,0)位于左上角
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

    def add_pin_joint(self, body1_name: str, body2_name: str, 
                     anchor1: Tuple[float, float], anchor2: Tuple[float, float]) -> str:
        """
        在两个物体之间添加刚性连接（PinJoint）
        
        Args:
            body1_name: 第一个物体名称
            body2_name: 第二个物体名称
            anchor1: 第一个物体的锚点
            anchor2: 第二个物体的锚点
            
        Returns:
            操作结果信息
        """
        if body1_name not in self.bodies:
            return f"错误：名为'{body1_name}'的物体不存在。"
        if body2_name not in self.bodies:
            return f"错误：名为'{body2_name}'的物体不存在。"
            
        body1 = self.bodies[body1_name]
        body2 = self.bodies[body2_name]
        
        # 创建PinJoint刚性连接
        pin_joint = pymunk.PinJoint(body1, body2, anchor1, anchor2)
        
        # 添加到空间
        self.space.add(pin_joint)
        
        return f"成功在'{body1_name}'和'{body2_name}'之间添加了刚性连接。"
    
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

    def set_body_properties(self, body_name: str, **properties) -> str:
        """
        设置物体的物理属性
        
        Args:
            body_name: 物体名称
            **properties: 要设置的属性，包括：
                - mass: 质量
                - friction: 摩擦系数
                - elasticity: 弹性系数
                - velocity: 速度 (x, y)
                - angular_velocity: 角速度
                
        Returns:
            操作结果信息
        """
        if body_name not in self.bodies:
            return f"错误：名为'{body_name}'的物体不存在。"
            
        body = self.bodies[body_name]
        shape = self.shapes[body_name]
        
        result_messages = []
        
        # 设置质量
        if "mass" in properties:
            new_mass = properties["mass"]
            if body.body_type != pymunk.Body.STATIC:
                # 重新计算转动惯量
                if isinstance(shape, pymunk.Circle):
                    moment = pymunk.moment_for_circle(new_mass, 0, shape.radius)
                elif isinstance(shape, pymunk.Poly):
                    moment = pymunk.moment_for_box(new_mass, shape.get_vertices())
                else:
                    moment = pymunk.moment_for_circle(new_mass, 0, 10)  # 默认值
                
                body.mass = new_mass
                body.moment = moment
                result_messages.append(f"质量设置为{new_mass}")
        
        # 设置摩擦系数
        if "friction" in properties:
            shape.friction = properties["friction"]
            result_messages.append(f"摩擦系数设置为{properties['friction']}")
        
        # 设置弹性系数
        if "elasticity" in properties:
            shape.elasticity = properties["elasticity"]
            result_messages.append(f"弹性系数设置为{properties['elasticity']}")
        
        # 设置速度
        if "velocity" in properties:
            body.velocity = properties["velocity"]
            result_messages.append(f"速度设置为{properties['velocity']}")
        
        # 设置角速度
        if "angular_velocity" in properties:
            body.angular_velocity = properties["angular_velocity"]
            result_messages.append(f"角速度设置为{properties['angular_velocity']}")
        
        if result_messages:
            return f"已更新'{body_name}'的属性：{', '.join(result_messages)}。"
        else:
            return f"没有提供有效的属性来更新'{body_name}'。"

    def create_ground(self, name: str, start_point: Tuple[float, float], 
                     end_point: Tuple[float, float], friction: float = 0.7, 
                     elasticity: float = 0.3) -> str:
        """
        创建地面（静态线段）
        
        Args:
            name: 地面名称
            start_point: 起始点 (x, y)
            end_point: 结束点 (x, y)
            friction: 摩擦系数
            elasticity: 弹性系数
            
        Returns:
            操作结果信息
        """
        if name in self.bodies:
            return f"错误：名为'{name}'的物体已存在。"
        
        # 创建静态身体
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        # 创建线段形状
        shape = pymunk.Segment(body, start_point, end_point, 5)  # 5是线段的厚度
        shape.friction = friction
        shape.elasticity = elasticity
        
        # 添加到空间
        self.space.add(body, shape)
        
        # 存储引用
        self.bodies[name] = body
        self.shapes[name] = shape
        
        return f"成功创建名为'{name}'的地面，从({start_point[0]:.1f}, {start_point[1]:.1f})到({end_point[0]:.1f}, {end_point[1]:.1f})。"
    
    def duplicate_body(self, original_name: str, count: int, offset: Tuple[float, float] = (50, 0)) -> str:
        """
        复制指定物体成多个副本
        
        Args:
            original_name: 原始物体名称
            count: 复制数量
            offset: 每个副本之间的偏移量 (x, y)
            
        Returns:
            操作结果信息
        """
        if original_name not in self.bodies:
            return f"错误：名为'{original_name}'的物体不存在。"
        
        if count <= 0:
            return f"错误：复制数量必须大于0。"
        
        original_body = self.bodies[original_name]
        original_shape = self.shapes[original_name]
        
        created_names = []
        
        for i in range(1, count + 1):
            # 生成新名称
            new_name = f"{original_name}_copy_{i}"
            
            # 检查名称是否已存在
            if new_name in self.bodies:
                return f"错误：名为'{new_name}'的物体已存在。"
            
            # 计算新位置
            new_position = (
                original_body.position.x + offset[0] * i,
                original_body.position.y + offset[1] * i
            )
            
            # 根据原始形状类型创建新物体
            if isinstance(original_shape, pymunk.Circle):
                # 复制圆形
                if original_body.body_type == pymunk.Body.STATIC:
                    new_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                else:
                    moment = pymunk.moment_for_circle(original_body.mass, 0, original_shape.radius)
                    new_body = pymunk.Body(original_body.mass, moment)
                
                new_body.position = new_position
                new_body.angle = original_body.angle
                new_body.velocity = original_body.velocity
                new_body.angular_velocity = original_body.angular_velocity
                
                # 创建新形状
                new_shape = pymunk.Circle(new_body, original_shape.radius)
                new_shape.friction = original_shape.friction
                new_shape.elasticity = original_shape.elasticity
                
            elif isinstance(original_shape, pymunk.Poly):
                # 复制多边形（矩形）
                if original_body.body_type == pymunk.Body.STATIC:
                    new_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                else:
                    vertices = original_shape.get_vertices()
                    moment = pymunk.moment_for_poly(original_body.mass, vertices)
                    new_body = pymunk.Body(original_body.mass, moment)
                
                new_body.position = new_position
                new_body.angle = original_body.angle
                new_body.velocity = original_body.velocity
                new_body.angular_velocity = original_body.angular_velocity
                
                # 创建新形状
                vertices = original_shape.get_vertices()
                new_shape = pymunk.Poly(new_body, vertices)
                new_shape.friction = original_shape.friction
                new_shape.elasticity = original_shape.elasticity
                
            elif isinstance(original_shape, pymunk.Segment):
                # 复制线段（地面/斜面）
                new_body = pymunk.Body(body_type=pymunk.Body.STATIC)
                new_body.position = new_position
                
                # 获取原始线段的端点
                start_point = original_shape.a
                end_point = original_shape.b
                
                # 创建新形状
                new_shape = pymunk.Segment(new_body, start_point, end_point, original_shape.radius)
                new_shape.friction = original_shape.friction
                new_shape.elasticity = original_shape.elasticity
                
            else:
                return f"错误：不支持的形状类型 '{type(original_shape).__name__}'。"
            
            # 添加到空间
            self.space.add(new_body, new_shape)
            
            # 存储引用
            self.bodies[new_name] = new_body
            self.shapes[new_name] = new_shape
            
            created_names.append(new_name)
        
        return f"成功复制'{original_name}' {count}次，创建了：{', '.join(created_names)}。"
    
    def create_car(self, name: str, position: Tuple[float, float], 
                   chassis_size: Tuple[float, float] = (50, 20), 
                   wheel_radius: float = 10, chassis_mass: float = 10, 
                   wheel_mass: float = 2) -> str:
        """
        创建一个小车，包含车身和两个轮子
        
        Args:
            name: 小车名称
            position: 车身中心位置 (x, y)
            chassis_size: 车身尺寸 (width, height)
            wheel_radius: 轮子半径
            chassis_mass: 车身质量
            wheel_mass: 轮子质量
            
        Returns:
            操作结果信息
        """
        if name in self.bodies:
            return f"错误：名为'{name}'的物体已存在。"
        
        x, y = position
        
        # 创建车身
        chassis_moment = pymunk.moment_for_box(chassis_mass, chassis_size)
        chassis_body = pymunk.Body(chassis_mass, chassis_moment, body_type=pymunk.Body.DYNAMIC)
        chassis_body.position = (x, y)
        chassis_shape = pymunk.Poly.create_box(chassis_body, chassis_size)
        chassis_shape.friction = 0.7
        chassis_shape.elasticity = 0.1
        chassis_shape.filter = pymunk.ShapeFilter(group=1)
        
        # 创建轮子
        wheel_moment = pymunk.moment_for_circle(wheel_mass, 0, wheel_radius)
        
        # 计算轮子位置（在车身下方）
        wheel_offset_y = chassis_size[1] / 2 + wheel_radius
        wheel_offset_x = chassis_size[0] / 2 - 10  # 轮子距离车身边缘10像素
        
        # 左轮
        wheel1_body = pymunk.Body(wheel_mass, wheel_moment, body_type=pymunk.Body.DYNAMIC)
        wheel1_body.position = (x - wheel_offset_x, y + wheel_offset_y)
        wheel1_shape = pymunk.Circle(wheel1_body, wheel_radius)
        wheel1_shape.friction = 1.0
        wheel1_shape.elasticity = 0.2
        wheel1_shape.filter = pymunk.ShapeFilter(group=1)
        
        # 右轮
        wheel2_body = pymunk.Body(wheel_mass, wheel_moment, body_type=pymunk.Body.DYNAMIC)
        wheel2_body.position = (x + wheel_offset_x, y + wheel_offset_y)
        wheel2_shape = pymunk.Circle(wheel2_body, wheel_radius)
        wheel2_shape.friction = 1.0
        wheel2_shape.elasticity = 0.2
        wheel2_shape.filter = pymunk.ShapeFilter(group=1)
        
        # 创建关节连接车身和轮子
        joint1 = pymunk.PivotJoint(chassis_body, wheel1_body, (-wheel_offset_x, wheel_offset_y), (0, 0))
        joint2 = pymunk.PivotJoint(chassis_body, wheel2_body, (wheel_offset_x, wheel_offset_y), (0, 0))
        
        # 添加到空间
        self.space.add(chassis_body, chassis_shape, wheel1_body, wheel1_shape, wheel2_body, wheel2_shape)
        self.space.add(joint1, joint2)
        
        # 存储引用（只存储车身，轮子作为车身的组成部分）
        self.bodies[name] = chassis_body
        self.shapes[name] = chassis_shape
        
        # 存储轮子信息（用于后续操作）
        self.bodies[f"{name}_wheel1"] = wheel1_body
        self.shapes[f"{name}_wheel1"] = wheel1_shape
        self.bodies[f"{name}_wheel2"] = wheel2_body
        self.shapes[f"{name}_wheel2"] = wheel2_shape
        
        return f"成功创建名为'{name}'的小车，车身位置({x:.1f}, {y:.1f})，尺寸{chassis_size}，轮子半径{wheel_radius}。"

    def add_pivot_joint(self, body1_name: str, body2_name: str, 
                       anchor1: Tuple[float, float], anchor2: Tuple[float, float]) -> str:
        """
        在两个物体之间添加枢轴关节（PivotJoint）
        
        Args:
            body1_name: 第一个物体名称
            body2_name: 第二个物体名称
            anchor1: 第一个物体上的锚点 (相对于物体中心)
            anchor2: 第二个物体上的锚点 (相对于物体中心)
            
        Returns:
            操作结果信息
        """
        if body1_name not in self.bodies:
            return f"错误：名为'{body1_name}'的物体不存在。"
        if body2_name not in self.bodies:
            return f"错误：名为'{body2_name}'的物体不存在。"
            
        body1 = self.bodies[body1_name]
        body2 = self.bodies[body2_name]
        
        # 创建PivotJoint
        pivot_joint = pymunk.PivotJoint(body1, body2, anchor1, anchor2)
        
        # 添加到空间
        self.space.add(pivot_joint)
        
        return f"成功在'{body1_name}'和'{body2_name}'之间添加了枢轴关节。"

    def create_slope(self, name: str, start_point: Tuple[float, float], 
                    end_point: Tuple[float, float], friction: float = 0.7, 
                    elasticity: float = 0.3) -> str:
        """
        创建斜面（静态线段）
        
        Args:
            name: 斜面名称
            start_point: 起始点 (x, y)
            end_point: 结束点 (x, y)
            friction: 摩擦系数
            elasticity: 弹性系数
            
        Returns:
            操作结果信息
        """
        # 斜面本质上也是地面，只是角度不同
        return self.create_ground(name, start_point, end_point, friction, elasticity)

    def get_space_status(self) -> dict:
        """
        获取 Pymunk 空间的状态信息。

        Returns:
            一个包含空间、所有物体、形状和约束详细信息的字典。
        """
        status_info = {
            "summary": {
                "body_count": len(self.space.bodies),
                "shape_count": len(self.space.shapes),
                "constraint_count": len(self.space.constraints),
                "gravity": tuple(self.space.gravity),
                "iterations": self.space.iterations,
                "current_time_step": self.space.current_time_step
            },
            "bodies": [],
            "shapes": [],
            "constraints": []
        }

        # 1. 收集所有物体的信息
        for body in self.space.bodies:
            # 查找对应的名称
            body_name = None
            for name, stored_body in self.bodies.items():
                if stored_body == body:
                    body_name = name
                    break
            
            body_data = {
                "name": body_name,
                "type": "STATIC" if body.body_type == pymunk.Body.STATIC else "DYNAMIC",
                "position": tuple(body.position),
                "angle_radians": body.angle,
                "angle_degrees": math.degrees(body.angle),
                "velocity": tuple(body.velocity),
                "angular_velocity": body.angular_velocity,
                "mass": body.mass,
                "moment": body.moment,
                "center_of_gravity": tuple(body.center_of_gravity),
                "force": tuple(body.force),
                "torque": body.torque
            }
            status_info["bodies"].append(body_data)

        # 2. 收集所有形状的信息
        for shape in self.space.shapes:
            # 查找对应的名称
            shape_name = None
            for name, stored_shape in self.shapes.items():
                if stored_shape == shape:
                    shape_name = name
                    break
            
            # 根据形状类型获取特定信息
            shape_details = {
                "name": shape_name,
                "type": shape.__class__.__name__,
                "friction": shape.friction,
                "elasticity": shape.elasticity,
                "mass": shape.mass,
                "sensor": shape.sensor,
                "collision_type": shape.collision_type,
                "body_hash": hash(shape.body)
            }
            
            # 添加特定形状的详细信息
            if isinstance(shape, pymunk.Circle):
                shape_details["radius"] = shape.radius
                shape_details["offset"] = tuple(shape.offset)
            elif isinstance(shape, pymunk.Poly):
                shape_details["vertices"] = [tuple(v) for v in shape.get_vertices()]
                shape_details["radius"] = shape.radius
            elif isinstance(shape, pymunk.Segment):
                shape_details["a"] = tuple(shape.a)
                shape_details["b"] = tuple(shape.b)
                shape_details["radius"] = shape.radius
            
            status_info["shapes"].append(shape_details)
        
        # 3. 收集所有约束的信息
        for constraint in self.space.constraints:
            constraint_data = {
                "type": constraint.__class__.__name__,
                "max_force": constraint.max_force,
                "error_bias": constraint.error_bias,
                "max_bias": constraint.max_bias,
                "collide_bodies": constraint.collide_bodies
            }
            
            # 添加特定约束的详细信息
            if isinstance(constraint, pymunk.PivotJoint):
                constraint_data["anchor_a"] = tuple(constraint.anchor_a)
                constraint_data["anchor_b"] = tuple(constraint.anchor_b)
            elif isinstance(constraint, pymunk.PinJoint):
                constraint_data["anchor_a"] = tuple(constraint.anchor_a)
                constraint_data["anchor_b"] = tuple(constraint.anchor_b)
                constraint_data["dist"] = constraint.dist
            elif isinstance(constraint, pymunk.DampedSpring):
                constraint_data["anchor_a"] = tuple(constraint.anchor_a)
                constraint_data["anchor_b"] = tuple(constraint.anchor_b)
                constraint_data["rest_length"] = constraint.rest_length
                constraint_data["stiffness"] = constraint.stiffness
                constraint_data["damping"] = constraint.damping
            
            # 查找连接的物体名称
            body_a_name = None
            body_b_name = None
            for name, stored_body in self.bodies.items():
                if stored_body == constraint.a:
                    body_a_name = name
                if stored_body == constraint.b:
                    body_b_name = name
            
            constraint_data["body_a"] = body_a_name
            constraint_data["body_b"] = body_b_name
            
            status_info["constraints"].append(constraint_data)
            
        return status_info

    def get_simulation_sequence(self, max_steps: int = 1000, dt: float = 1.0/60.0, 
                              velocity_threshold: float = 0.1, angular_threshold: float = 0.01,
                              max_sequence_length: int = 10) -> dict:
        """
        获取一段时间内的空间状态序列信息，直到系统达到稳定状态或达到最大步数
        
        Args:
            max_steps: 最大模拟步数
            dt: 时间步长（秒）
            velocity_threshold: 速度阈值，用于判断是否稳定
            angular_threshold: 角速度阈值，用于判断是否稳定
            
        Returns:
            包含序列信息的字典，包括：
            - metadata: 模拟元信息
            - sequence: 状态序列列表
            - final_state: 最终状态
            - convergence_info: 收敛信息
        """
        import copy
        
        # 保存初始状态
        initial_status = self.get_space_status()
        full_sequence = []
        convergence_info = {
            "converged": False,
            "convergence_step": None,
            "reason": "",
            "final_velocity_sum": 0.0,
            "final_angular_velocity_sum": 0.0
        }
        
        # 记录初始速度和角速度
        initial_velocity_sum = sum(
            abs(body["velocity"][0]) + abs(body["velocity"][1]) + abs(body["angular_velocity"])
            for body in initial_status["bodies"]
            if body["type"] == "DYNAMIC"
        )
        
        previous_status = None
        previous_velocity_sum = initial_velocity_sum
        
        # 开始模拟序列
        for step in range(max_steps):
            # 执行物理步进
            self.space.step(dt)
            
            # 获取当前状态
            current_status = self.get_space_status()
            current_status["time_step"] = step
            current_status["simulation_time"] = step * dt
            full_sequence.append(current_status)
            
            # 计算当前速度和角速度总和
            current_velocity_sum = sum(
                abs(body["velocity"][0]) + abs(body["velocity"][1]) + abs(body["angular_velocity"])
                for body in current_status["bodies"]
                if body["type"] == "DYNAMIC"
            )
            
            # 检查是否收敛（速度和角速度都很小）
            if current_velocity_sum < velocity_threshold and current_velocity_sum < angular_threshold:
                convergence_info["converged"] = True
                convergence_info["convergence_step"] = step
                convergence_info["reason"] = "系统达到速度和角速度阈值，趋于稳定"
                convergence_info["final_velocity_sum"] = current_velocity_sum
                convergence_info["final_angular_velocity_sum"] = sum(
                    abs(body["angular_velocity"]) for body in current_status["bodies"]
                    if body["type"] == "DYNAMIC"
                )
                break
            
            # 检查是否振荡收敛（速度变化很小）
            if previous_status is not None:
                velocity_change = abs(current_velocity_sum - previous_velocity_sum)
                if velocity_change < 0.001:  # 速度变化极小
                    # 检查几个连续步骤的速度变化
                    if step > 10:  # 至少运行10步后才检查
                        recent_changes = [
                            abs(full_sequence[i]["bodies"][0]["velocity"][0] - full_sequence[i-1]["bodies"][0]["velocity"][0])
                            for i in range(max(1, len(full_sequence)-5), len(full_sequence))
                        ]
                        if all(change < 0.1 for change in recent_changes if len(full_sequence) > 1):
                            convergence_info["converged"] = True
                            convergence_info["convergence_step"] = step
                            convergence_info["reason"] = "系统趋于稳定，速度变化极小"
                            convergence_info["final_velocity_sum"] = current_velocity_sum
                            break
            
            previous_status = current_status
            previous_velocity_sum = current_velocity_sum
            
            # 如果达到最大步数
            if step == max_steps - 1:
                convergence_info["reason"] = f"达到最大步数 {max_steps}"
                convergence_info["final_velocity_sum"] = current_velocity_sum
        
        # 控制序列长度：保留初始和末尾状态，中间按顺序间隔抽取
        sequence = []
        
        if len(full_sequence) == 0:
            # 如果没有序列数据，返回空序列
            pass
        elif len(full_sequence) == 1 or max_sequence_length == 1:
            # 如果只有一个状态或只要求一个状态，只返回初始状态
            sequence.append(full_sequence[0])
        elif max_sequence_length == 2:
            # 特殊情况：只保留初始和最终状态
            sequence.append(full_sequence[0])
            if len(full_sequence) > 1:
                sequence.append(full_sequence[-1])
        elif len(full_sequence) <= max_sequence_length:
            # 如果序列长度小于等于最大长度，直接使用完整序列
            sequence = full_sequence.copy()
        else:
            # 需要抽样以控制长度
            # 添加初始状态
            sequence.append(full_sequence[0])
            
            # 计算需要抽取的中间状态数量
            middle_count = max_sequence_length - 2
            if middle_count > 0 and len(full_sequence) > 2:
                # 计算间隔
                interval = (len(full_sequence) - 2) / (middle_count + 1)
                # 按顺序间隔抽取中间状态
                for i in range(middle_count):
                    index = int(1 + (i + 1) * interval)
                    if 1 <= index < len(full_sequence) - 1:
                        sequence.append(full_sequence[index])
            
            # 添加最终状态
            if len(full_sequence) > 1:
                sequence.append(full_sequence[-1])
        
        # 确保序列长度不超过限制
        if len(sequence) > max_sequence_length:
            sequence = sequence[:max_sequence_length]
        
        return {
            "metadata": {
                "max_steps": max_steps,
                "dt": dt,
                "velocity_threshold": velocity_threshold,
                "angular_threshold": angular_threshold,
                "total_steps": len(full_sequence),
                "max_sequence_length": max_sequence_length
            },
            "sequence": sequence,
            "final_state": full_sequence[-1] if full_sequence else initial_status,
            "convergence_info": convergence_info,
            "initial_state": initial_status
        }

# if __name__ == "__main__":
#     sandbox = PhysicsSandbox()
#     sandbox.create_circle("ball1", (100, 200), 25)
#     sandbox.create_circle("ball2", (150, 200), 25)
#     sandbox.add_spring_joint("ball1", "ball2", (0, 0), (0, 0), 100, 10)
#     print(sandbox.get_space_status())
