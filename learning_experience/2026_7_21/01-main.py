import os
import math
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv

# 环境变量导入
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL")


# 定义工具
@tool       # 这个装饰器就是定义工具的核心流程, 以此区分函数和工具
def get_weather(city:str)->str:
    """
    获取指定城市的天气情况
    Args:
        city: 城市名称, 如 北京, 上海等
    Returns:
        查询结果
    Examples:
        get_weather("北京") 返回 "北京天气晴, 温度25度"
    """
    # 上面这段关于工具的描述是必要的, 因为在agent选择工具调用时, 这段的内容会被传输给LLM, LLM根据这段描述选择使用的工具
    weather_db = {
        "北京": "北京天气晴, 温度25度",
        "上海": "上海天气阴, 温度13度",
        "西安": "西安天气暴雨, 温度6度",
        "成都": "成都天气大风, 温度10度",
        "哈尔滨": "哈尔滨天气大雪, 温度-4度"
    }
    if weather_db.get(city):
        return weather_db[city]
    else:
        return f"{city}天气多云, 温度20度"
    
@tool
def calculator(expression: str)->str:
    """
    计算数学表达式
    Args:
        expression: 数学表达式, 如 "2 * 3 + 4"
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return result
    except Exception as e:
        return f"计算错误: {e}"

# 创建agent
model = init_chat_model(
    model="Qwen/Qwen3-8B",
    model_provider="openai",
    base_url=QWEN_URL,
    api_key=QWEN_API_KEY,
    # streaming=True
)

agent = create_agent(
    model=model,
    tools=[get_weather, calculator],
    system_prompt="""
你是一名智能助手, 能够帮助我查询天气和数学计算

当用户需要查询天气时, 调用 get_weather 工具
当用户需要数学计算时, 调用 calculator 工具

请始终使用中文回答
""",
    # debug=True
)

# 测试
# print("="*60)
# question1 = "告诉我北京和上海谁更热?"

# answer1 = agent.invoke(input={"messages": [{"role": "user", "content": question1}]})
# print(answer1["messages"][-1].content)

# for chunk in agent.stream(input={"messages": [{"role": "user", "content": question1}]}):
#     print(chunk)
#     print("-"*100)

# for chunk, metadata in agent.stream(
#     input={"messages": [{"role": "user", "content": question1}]},
#     stream_mode="messages"
#     ):
#     if hasattr(chunk, 'content') and chunk.content:
#         print(chunk.content, end="", flush=True)


# print("="*60)


# 多轮对话
print("多轮对话, 输入quit退出")
# 定义messages
messages = []
while True:
    user_input = input("你: ").strip()
    if user_input.lower() == "quit":
        print("退出成功")
        break
    # 将用户的提示词添加到messages中
    messages.append({"role": "user", "content": user_input})
    # 调用agent
    resp = agent.invoke({"messages": messages})
    # 更新历史信息
    messages = resp["messages"]
    # 获取最后一条信息, 作为AI的回复
    last_message = messages[-1]
    if last_message.type == "ai":
        print(f"AI: {last_message.content}\n")