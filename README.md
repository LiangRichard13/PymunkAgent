# Pymunk物理引擎LangChain工具

这个项目将Pymunk物理引擎封装为LangChain工具，让AI Agent能够控制和操作物理模拟。

## 功能特性

- 🎯 **12个专业工具**: 创建物体、施加力、管理物理世界
- 🤖 **AI Agent集成**: 完美支持LangChain Agent调用
- 📝 **详细文档**: 每个工具都有完整的参数格式说明
- 🎮 **可视化支持**: 集成Pygame可视化物理模拟
- 🔧 **错误处理**: 完善的错误检查和友好的错误信息

## 安装依赖

```bash
pip install -r requirements.txt
```

## 核心文件

- `physics_sandbox.py` - 物理沙盒核心类
- `pymunk_tools.py` - LangChain工具注册
- `test_pymunk_tools.py` - 工具功能测试
- `agent_example.py` - AI Agent使用示例
- `util.py` - Pygame可视化工具

## 工具列表

### 创建物体
- `create_circle` - 创建圆形物体
- `create_box` - 创建矩形物体

### 物理操作
- `apply_impulse` - 施加冲量
- `apply_force` - 施加持续力
- `set_position` - 设置物体位置
- `get_position` - 获取物体位置

### 连接和约束
- `add_spring_joint` - 添加弹簧关节

### 世界管理
- `set_gravity` - 设置重力
- `step_physics` - 执行物理步进
- `get_all_bodies` - 获取所有物体信息
- `remove_body` - 删除指定物体
- `clear_all_bodies` - 清空所有物体

## 快速开始

### 1. 基本使用

```python
from pymunk_tools import create_pymunk_tools
import json

# 创建工具管理器
tool_manager = create_pymunk_tools()
tools = tool_manager.get_tools()

# 使用工具
circle_tool = next(t for t in tools if t.name == "create_circle")
result = circle_tool.func(json.dumps({
    "name": "ball1",
    "position": [100, 200],
    "radius": 25,
    "mass": 2.0
}))
print(result)
```

### 2. AI Agent集成

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from pymunk_tools import create_pymunk_tools

# 创建工具
tool_manager = create_pymunk_tools()
tools = tool_manager.get_tools()

# 创建Agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 使用Agent
response = agent.run("创建一个名为ball的圆形，位置在(100,200)，半径30")
print(response)
```

### 3. 可视化演示

```python
import util
from pymunk_tools import create_pymunk_tools

tool_manager = create_pymunk_tools()
# ... 创建一些物体 ...
util.run(tool_manager.get_sandbox().space)
```

## 工具参数格式

所有工具都使用JSON格式的参数：

### 创建圆形
```json
{
    "name": "物体名称",
    "position": [x坐标, y坐标],
    "radius": 半径,
    "mass": 质量,
    "is_static": 是否静态
}
```

### 施加冲量
```json
{
    "body_name": "物体名称",
    "impulse": [x方向冲量, y方向冲量]
}
```

### 弹簧关节
```json
{
    "body1_name": "第一个物体",
    "body2_name": "第二个物体",
    "anchor1": [x偏移, y偏移],
    "anchor2": [x偏移, y偏移],
    "stiffness": 弹簧刚度,
    "damping": 阻尼系数
}
```

## 运行示例

```bash
# 测试工具功能
python test_pymunk_tools.py

# 运行Agent示例 (需要设置OPENAI_API_KEY)
python agent_example.py

# 运行基本演示
python physics_sandbox_demo.py
```

## Agent指令示例

- "创建一个名为ball1的圆形，位置在(100,200)，半径25"
- "给ball1施加向上的冲量(0,-300)"
- "设置重力为(0,500)"
- "在ball1和ball2之间添加弹簧连接"
- "获取所有物体的位置信息"

## 环境变量

使用AI Agent功能时需要设置：
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

## 注意事项

1. **坐标系统**: 使用标准屏幕坐标，原点在左上角，Y轴向下
2. **重力**: 默认重力为(0, 981)，表示向下980像素/秒²
3. **质量**: 质量为0的物体为静态物体
4. **弹簧参数**: 刚度推荐100-10000，阻尼推荐10-1000

## 扩展功能

可以轻松扩展更多工具：
- 添加更多形状类型
- 实现碰撞检测
- 添加约束类型
- 实现材质属性

## 许可证

MIT License
