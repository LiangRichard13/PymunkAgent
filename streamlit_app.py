import streamlit as st
import pygame as pg
import sys
import io
import time
from PIL import Image
from pymunk_agent import PymunkAgent
from pymunk.pygame_util import DrawOptions
import util
import imageio
import numpy as np
import os

# 设置页面配置
st.set_page_config(
    page_title="Pymunk Agent 物理模拟器",
    page_icon="🔬",
    layout="wide"
)

# 初始化session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'ready_to_simulate' not in st.session_state:
    st.session_state.ready_to_simulate = False
if 'video_path' not in st.session_state:
    st.session_state.video_path = None

"""视频模式：不进行实时线程模拟"""

def initialize_agent():
    """初始化Agent"""
    if st.session_state.agent is None:
        with st.spinner("正在初始化Pymunk Agent..."):
            st.session_state.agent = PymunkAgent()
        st.success("Agent初始化完成！")

def add_log(message, log_type="info"):
    """添加日志到session state"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append({
        "timestamp": timestamp,
        "message": message,
        "type": log_type
    })

def clear_logs():
    """清空日志"""
    st.session_state.logs = []

# 删除实时模拟线程逻辑

def render_video_frames(agent, duration_seconds=10, fps=60, width=800, height=600, tmp_dir=".cache_frames"):
    """离线渲染固定时长到帧序列并编码为mp4，返回视频路径"""
    if agent is None:
        raise RuntimeError("Agent未初始化")
    
    space = agent.tool_manager.sandbox.space
    
    # 离线渲染：使用pygame的Surface在内存中绘制
    pg.init()
    surface = pg.Surface((width, height))
    draw_options = DrawOptions(surface)
    background = (255, 255, 255)
    total_frames = int(duration_seconds * fps)
    dt = 1.0 / fps
    
    os.makedirs(tmp_dir, exist_ok=True)
    frames = []
    
    for _ in range(total_frames):
        surface.fill(background)
        space.debug_draw(draw_options)
        space.step(dt)
        # 转为RGB ndarray
        img_str = pg.image.tostring(surface, 'RGB')
        frame = np.frombuffer(img_str, dtype=np.uint8)
        frame = frame.reshape((height, width, 3))
        frames.append(frame)
    
    # 编码为mp4
    video_path = os.path.join(tmp_dir, f"simulation_{int(time.time())}.mp4")
    imageio.mimwrite(video_path, frames, fps=fps, quality=7)
    pg.quit()
    return video_path

def execute_instruction_step_by_step(instruction, log_placeholder):
    """分步执行用户指令，实现实时日志显示"""
    if st.session_state.agent is None:
        initialize_agent()
    
    add_log(f"用户指令: {instruction}", "user")
    update_log_display(log_placeholder)
    
    # 清空之前的物理世界
    st.session_state.agent.tool_manager.sandbox.clear_all()
    add_log("已清空物理世界", "system")
    update_log_display(log_placeholder)
    st.session_state.ready_to_simulate = False
    st.session_state.simulation_image = None
    
    # 执行指令
    try:
        # 重写run方法以捕获输出
        agent = st.session_state.agent
        agent.planner_history.append(agent.planner_history[0])  # 添加系统提示
        agent.executor_history.append(agent.executor_history[0])  # 添加系统提示
        
        # 添加用户指令
        from langchain_core.messages import HumanMessage
        agent.planner_history.append(HumanMessage(content=f"用户指令: {instruction},请你根据用户指令制定计划列表"))
        agent.executor_history.append(HumanMessage(content=f"用户指令: {instruction},请你根据用户指令完成任务"))
        
        add_log("正在执行Planner...", "system")
        update_log_display(log_placeholder)
        
        # Planner执行
        planner_response = agent.planner_execute()
        add_log(f"计划📋   {planner_response}", "planner")
        update_log_display(log_placeholder)
        
        from langchain_core.messages import AIMessage
        agent.planner_history.append(AIMessage(content=planner_response))
        agent.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
        
        add_log("开始执行Executor...", "system")
        update_log_display(log_placeholder)
        
        # Executor执行循环
        step_count = 0
        while True:
            step_count += 1
            add_log(f"执行步骤 {step_count}...", "system")
            update_log_display(log_placeholder)
            
            executor_response = agent.executor_execute()
            if isinstance(executor_response, dict):
                add_log(f"观察👀   {executor_response["observation"]}", "executor")
                add_log(f"思考💡   {executor_response["thinking"]}", "executor")
                add_log(f"动作🔧   {executor_response["tool_name"]}", "executor")
                add_log(f"输入✏️   {executor_response["tool_input"]}", "executor")
                update_log_display(log_placeholder)
            else:            
                if "<TASK_DONE>" in executor_response:
                    add_log("任务执行完成！", "success")
                    update_log_display(log_placeholder)
                    break
            
            agent.executor_history.append(HumanMessage(content=f"这是执行结果:{executor_response}"))
        
        # 任务完成后，提供开始模拟按钮
        st.session_state.ready_to_simulate = True
        add_log("任务已完成。可点击'开始模拟'按钮启动模拟。", "system")
        update_log_display(log_placeholder)
        
    except Exception as e:
        add_log(f"执行出错: {str(e)}", "error")
        update_log_display(log_placeholder)
        st.error(f"执行出错: {str(e)}")

def update_log_display(log_placeholder):
    """更新日志显示"""
    with log_placeholder.container():
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-50:]):  # 只显示最近50条日志
                timestamp = log["timestamp"]
                message = log["message"]
                log_type = log["type"]
                
                # 根据日志类型设置不同的样式
                if log_type == "user":
                    st.info(f"🕐 {timestamp} | 👤 用户: {message}")
                elif log_type == "planner":
                    st.success(f"🕐 {timestamp} | 🧠 Planner: {message}")
                elif log_type == "executor":
                    st.warning(f"🕐 {timestamp} | ⚙️ Executor: {message}")
                elif log_type == "system":
                    st.info(f"🕐 {timestamp} | 🔧 系统: {message}")
                elif log_type == "success":
                    st.success(f"🕐 {timestamp} | ✅ 成功: {message}")
                elif log_type == "error":
                    st.error(f"🕐 {timestamp} | ❌ 错误: {message}")
                else:
                    st.write(f"🕐 {timestamp} | {message}")
        else:
            st.info("暂无日志记录")

# 主界面
st.title("🔬 Pymunk Agent 物理模拟器")
st.markdown("---")

# 侧边栏 - 控制面板
with st.sidebar:
    st.header("🎛️ 控制面板")
    
    # 清空日志按钮
    if st.button("🗑️ 清空日志"):
        clear_logs()
    
    st.markdown("---")

# 主内容区域
col1, col2 = st.columns([1, 1])

# 左列 - 指令输入和日志
with col1:
    st.subheader("📝 指令输入")
    
    # 指令输入框
    instruction = st.text_area(
        "请输入您的指令:",
        height=100,
        placeholder="例如：创建一个圆形，位置在(100, 100)，半径为20",
        key="instruction_input"
    )
    
    # 执行按钮
    if st.button("▶️ 执行指令", type="primary"):
        if instruction.strip():
            # 创建日志占位符
            log_placeholder = st.empty()
            # 使用分步执行函数实现实时日志显示
            execute_instruction_step_by_step(instruction.strip(), log_placeholder)
        else:
            st.warning("请输入指令")
    
    st.markdown("---")
    
    # 日志显示
    st.subheader("📋 执行日志")
    
    # 创建日志容器用于实时更新
    log_container = st.empty()
    
    with log_container.container():
        if st.session_state.logs:
            for log in reversed(st.session_state.logs[-50:]):  # 只显示最近50条日志
                timestamp = log["timestamp"]
                message = log["message"]
                log_type = log["type"]
                
                # 根据日志类型设置不同的样式
                if log_type == "user":
                    st.info(f"🕐 {timestamp} | 👤 用户: {message}")
                elif log_type == "planner":
                    st.success(f"🕐 {timestamp} | 🧠 Planner: {message}")
                elif log_type == "executor":
                    st.warning(f"🕐 {timestamp} | ⚙️ Executor: {message}")
                elif log_type == "system":
                    st.info(f"🕐 {timestamp} | 🔧 系统: {message}")
                elif log_type == "success":
                    st.success(f"🕐 {timestamp} | ✅ 成功: {message}")
                elif log_type == "error":
                    st.error(f"🕐 {timestamp} | ❌ 错误: {message}")
                else:
                    st.write(f"🕐 {timestamp} | {message}")
        else:
            st.info("暂无日志记录")

# 右列 - 视频生成
with col2:
    st.subheader("🎬 模拟视频生成")
    
    if st.session_state.ready_to_simulate:
        with st.expander("📹 生成并预览视频", expanded=True):
            duration = st.slider("视频时长 (秒)", 1, 30, 10, 1)
            fps = st.slider("帧率 (fps)", 15, 120, 60, 5)
            if st.button("🎬 生成视频", key="gen_video"):
                try:
                    with st.spinner("正在渲染视频..."):
                        st.session_state.video_path = render_video_frames(st.session_state.agent, duration_seconds=duration, fps=fps)
                    st.success("视频生成完成！")
                except Exception as e:
                    st.error(f"视频生成失败: {e}")
            
            if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                st.video(st.session_state.video_path)
    else:
        st.info("请先执行指令以生成场景，然后在此生成视频")

# 底部状态栏
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.agent is not None:
        st.success("✅ Agent已初始化")
    else:
        st.warning("⚠️ Agent未初始化")

with col2:
    st.info("🎥 视频模式：不进行实时模拟")

with col3:
    st.info(f"📊 日志数量: {len(st.session_state.logs)}")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🔬 Pymunk Agent 物理模拟器 | 基于 Pymunk 和 LangChain 构建
    </div>
    """,
    unsafe_allow_html=True
)
