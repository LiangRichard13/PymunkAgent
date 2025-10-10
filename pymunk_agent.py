from re import S
from pymunk_tools import PymunkToolManager
from langchain_openai import ChatOpenAI
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from json.decoder import JSONDecodeError
from config import *
from openai import InternalServerError
from typing import Union
import json
import time
import os


class PymunkAgent:
    def __init__(self):
        # 工具配置
        self.tool_manager = PymunkToolManager()
        self.tools = self.tool_manager.get_tools()
        self.tools_description = self.tool_manager.get_tools_description()
        # 大模型API配置
        self.executor_llm = ChatOpenAI(base_url=EXECTUTOR_BASE_URL, model=EXECTUTOR_MODEL, api_key=EXECTUTOR_API_KEY, temperature=EXECTUTOR_TEMPERATURE)
        self.planner_llm = ChatOpenAI(base_url=PLANNER_BASE_URL, model=PLANNER_MODEL, api_key=PLANNER_API_KEY, temperature=PLANNER_TEMPERATURE)
        # 系统提示词配置
        self.executor_system_prompt_template = SystemMessagePromptTemplate.from_template(template=EXECTUTOR_SYSTEM_PROMPT)
        self.planner_system_prompt_template = SystemMessagePromptTemplate.from_template(template=PLANNER_SYSTEM_PROMPT)
        self.executor_system_prompt = self.executor_system_prompt_template.format(tools_description=self.tools_description)
        self.planner_system_prompt = self.planner_system_prompt_template.format(tools_description=self.tools_description)
        # 历史消息配置
        self.executor_history = [self.executor_system_prompt]
        self.planner_history = [self.planner_system_prompt]
        
    # Executor工具调用    
    def executor_tool_call(self, tool_name: str, tool_input: dict)->str:
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if tool:
            try:
                if tool_input == "":
                    tool_execute_result =  tool.func()
                else:
                    tool_execute_result =  tool.func(tool_input)
                space_current_status = self.tool_manager.get_sandbox_status()
                aggregated_status = f"工具 {tool_name} 执行成功，执行结果: {tool_execute_result}，物理沙盒状态: {space_current_status}"
                return aggregated_status
            except Exception as e:
                aggregated_status = f"工具 {tool_name} 执行失败: {str(e)}"
                return aggregated_status
        else:
            aggregated_status = f"工具 {tool_name} 不存在"
            return aggregated_status
    
    # Executor执行
    def executor_execute(self)->Union[str,dict]:
        executor_response = self.executor_llm.invoke(self.executor_history)
        while True:
            try:
                executor_response = json.loads(executor_response.content)
                if executor_response.get("tool_name") == "no_tool":
                    return executor_response
                elif executor_response.get("tool_name") == "task_done":
                    return "<TASK_DONE>"
                else:
                    tool_name = executor_response.get("tool_name")
                    tool_input = executor_response.get("tool_input")
                    tool_call_result = self.executor_tool_call(tool_name, tool_input)
                    executor_response["tool_call_result"] = tool_call_result
                    return executor_response
            except JSONDecodeError:
                print("Executor执行失败: JSONDecodeError")
                executor_response = self.executor_llm.invoke(self.executor_history)
            except InternalServerError:
                print("Executor执行失败: InternalServerError")
                time.sleep(5) # 等待5秒后重试
                executor_response = self.executor_llm.invoke(self.executor_history)
            except Exception as e:
                print(f"Executor执行失败: {str(e)}")
                raise Exception(f"Executor执行失败: {str(e)}")

    # Planner执行
    def planner_execute(self)->str:
        while True:
            try:
                planner_response = self.planner_llm.invoke(self.planner_history)
                return planner_response.content
            except InternalServerError:
                print("Planner执行失败: InternalServerError")
                time.sleep(5) # 等待5秒后重试
                planner_response = self.planner_llm.invoke(self.planner_history)
            except Exception as e:
                print(f"Planner执行失败: {str(e)}")
                raise Exception(f"Planner执行失败: {str(e)}")
    # Judge初始化
    def judge_init(self,sequence_data,user_instruction):
        self.judge_llm = ChatOpenAI(base_url=JUDGE_BASE_URL,model=JUDGE_MODEL,api_key=JUDGE_API_KEY,temperature=JUDGE_TEMPERATURE)
        self.judge_system_prompt_template = SystemMessagePromptTemplate.from_template(template=JUDGE_SYSTEM_PROMPT)
        self.judge_system_prompt = self.judge_system_prompt_template.format(sequence_data=sequence_data,user_instruction=user_instruction)
        self.judge_history = [self.judge_system_prompt]

    # Judge执行
    def judge_execute(self)->dict:
        judge_response = self.judge_llm.invoke(self.judge_history)
        while True:
            try:
                judge_response = json.loads(judge_response.content)
                return judge_response
            except JSONDecodeError:
                print("Judge执行失败: JSONDecodeError")
                judge_response = self.judge_llm.invoke(self.judge_history)
            except InternalServerError:
                print("Judge执行失败: InternalServerError")
                time.sleep(5) # 等待5秒后重试
                judge_response = self.judge_llm.invoke(self.judge_history)
            except Exception as e:
                print(f"Judge执行失败: {str(e)}")
                raise Exception(f"Judge执行失败: {str(e)}")

    # Summary初始化
    def summary_init(self, action_sequence, user_instruction):
        self.summary_llm = ChatOpenAI(base_url=SUMMARY_BASE_URL, model=SUMMARY_MODEL, api_key=SUMMARY_API_KEY, temperature=SUMMARY_TEMPERATURE)
        self.summary_system_prompt_template = SystemMessagePromptTemplate.from_template(template=SUMMARY_SYSTEM_PROMPT)
        self.summary_system_prompt = self.summary_system_prompt_template.format(action_sequence=action_sequence, user_instruction=user_instruction)
        self.summary_history = [self.summary_system_prompt]

    # Summary执行
    def summary_execute(self)->dict:
        while True:
            try:
                summary_response = self.summary_llm.invoke(self.summary_history)
                summary_response = json.loads(summary_response.content)
                return summary_response
            except InternalServerError:
                print("Summary执行失败: InternalServerError")
                time.sleep(5) # 等待5秒后重试
                summary_response = self.summary_llm.invoke(self.summary_history)
            except Exception as e:
                print(f"Summary执行失败: {str(e)}")
                raise Exception(f"Summary执行失败: {str(e)}")

    # 保存成功案例到JSON文件
    def save_success_case(self, user_instruction, summary_response):
        # 创建success_cases目录
        os.makedirs("success_cases", exist_ok=True)
        
        # 准备保存的数据
        success_data = {
            "user_instruction": user_instruction,
            "summary": summary_response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 统一保存的文件名
        filename = "success_cases/success_cases.json"
        
        # 读取现有的成功案例数据（如果文件存在）
        all_success_cases = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    all_success_cases = json.load(f)
            except (json.JSONDecodeError, Exception):
                # 如果文件损坏或为空，重新初始化
                all_success_cases = []
        
        # 添加新的成功案例
        all_success_cases.append(success_data)
        
        # 保存到统一的JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_success_cases, f, ensure_ascii=False, indent=2)
        
        print(f"成功案例已保存到: {filename}")
        return filename

    # 清除消息历史记录
    def clear_history(self,agent_type: str):
        if agent_type == "executor":
            self.executor_history = [self.executor_system_prompt]
        elif agent_type == "planner":
            self.planner_history = [self.planner_system_prompt]

    # def run_two_agents(self, user_instruction: str):
    #     chat_trun_limit = 10
    #     self.planner_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令制定计划列表"))
    #     self.executor_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令完成任务"))
    #     planner_response = self.planner_execute()
    #     print(planner_response)
    #     self.planner_history.append(AIMessage(content=planner_response))
    #     self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
    #     while True:
    #         executor_response = self.executor_execute()
    #         print(executor_response)
    #         self.executor_history.append(AIMessage(content=executor_response))
    #         self.planner_history.append(HumanMessage(content=f"这是执行结果:{executor_response},如果指令没有完成请更新计划列表,如果指令已经完成请输出<TASK_DONE>"))
    #         planner_response = self.planner_execute()
    #         print(planner_response)
    #         if "<TASK_DONE>" in planner_response:
    #             break
    #         else:
    #             self.planner_history.append(AIMessage(content=planner_response))
    #             # 只有当planner_response不包含<TASK_DONE>时才传递给executor
    #             if "<TASK_DONE>" not in planner_response:
    #                 self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
    #             chat_trun_limit -= 1
    #             if chat_trun_limit <= 0:
    #                 break

    # def run(self, user_instruction: str):
    #     self.planner_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令制定计划列表"))
    #     self.executor_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令完成任务"))
    #     planner_response = self.planner_execute()
    #     print(planner_response)
    #     self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
    #     while True:
    #         executor_response = self.executor_execute()
    #         print(executor_response)
    #         self.executor_history.append(HumanMessage(content=f"这是执行结果:{executor_response}"))
    #         if "<TASK_DONE>" in executor_response:
    #             break
