from re import S
from pymunk_tools import PymunkToolManager
from langchain_openai import ChatOpenAI
from config import EXECTUTOR_BASE_URL, EXECTUTOR_MODEL, EXECTUTOR_API_KEY, EXECTUTOR_TEMPERATURE, EXECTUTOR_SYSTEM_PROMPT, PLANNER_BASE_URL, PLANNER_MODEL, PLANNER_API_KEY, PLANNER_TEMPERATURE, PLANNER_SYSTEM_PROMPT
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from json.decoder import JSONDecodeError
from openai import InternalServerError
import json
import time
from typing import Union


class PymunkAgent:
    def __init__(self):
        self.tool_manager = PymunkToolManager()
        self.tools = self.tool_manager.get_tools()
        self.tools_description = self.tool_manager.get_tools_description()
        self.executor_llm = ChatOpenAI(base_url=EXECTUTOR_BASE_URL, model=EXECTUTOR_MODEL, api_key=EXECTUTOR_API_KEY, temperature=EXECTUTOR_TEMPERATURE)
        self.planner_llm = ChatOpenAI(base_url=PLANNER_BASE_URL, model=PLANNER_MODEL, api_key=PLANNER_API_KEY, temperature=PLANNER_TEMPERATURE)
        self.executor_system_prompt_template = SystemMessagePromptTemplate.from_template(template=EXECTUTOR_SYSTEM_PROMPT)
        self.planner_system_prompt_template = SystemMessagePromptTemplate.from_template(template=PLANNER_SYSTEM_PROMPT)
        self.executor_system_prompt = self.executor_system_prompt_template.format(tools_description=self.tools_description)
        self.planner_system_prompt = self.planner_system_prompt_template.format(tools_description=self.tools_description)
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

    # 清除消息历史记录
    def clear_history(self,agent_type: str):
        if agent_type == "executor":
            self.executor_history = [self.executor_system_prompt]
        elif agent_type == "planner":
            self.planner_history = [self.planner_system_prompt]

    def run_two_agents(self, user_instruction: str):
        chat_trun_limit = 10
        self.planner_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令制定计划列表"))
        self.executor_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令完成任务"))
        planner_response = self.planner_execute()
        print(planner_response)
        self.planner_history.append(AIMessage(content=planner_response))
        self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
        while True:
            executor_response = self.executor_execute()
            print(executor_response)
            self.executor_history.append(AIMessage(content=executor_response))
            self.planner_history.append(HumanMessage(content=f"这是执行结果:{executor_response},如果指令没有完成请更新计划列表,如果指令已经完成请输出<TASK_DONE>"))
            planner_response = self.planner_execute()
            print(planner_response)
            if "<TASK_DONE>" in planner_response:
                break
            else:
                self.planner_history.append(AIMessage(content=planner_response))
                # 只有当planner_response不包含<TASK_DONE>时才传递给executor
                if "<TASK_DONE>" not in planner_response:
                    self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
                chat_trun_limit -= 1
                if chat_trun_limit <= 0:
                    break

    def run(self, user_instruction: str):
        self.planner_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令制定计划列表"))
        self.executor_history.append(HumanMessage(content=f"用户指令: {user_instruction},请你根据用户指令完成任务"))
        planner_response = self.planner_execute()
        print(planner_response)
        self.executor_history.append(HumanMessage(content=f"这是当前可供参考的计划列表:{planner_response}"))
        while True:
            executor_response = self.executor_execute()
            print(executor_response)
            self.executor_history.append(HumanMessage(content=f"这是执行结果:{executor_response}"))
            if "<TASK_DONE>" in executor_response:
                break
