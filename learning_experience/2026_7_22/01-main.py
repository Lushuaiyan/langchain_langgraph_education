import os
from typing import Annotated
from dotenv import load_dotenv
from langchain_core.tools import handle_tool_error, InjectedToolCallId, ToolException, tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

# 环境变量导入
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL")

# 直接使用@tool
@tool
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
    # 上面这段关于工具的描述(docstring)是必要的, 因为在agent选择工具调用时, 这段的内容会被传输给LLM, LLM根据这段描述选择使用的工具
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


# 使用args_schema

# 定义参数模型
class CourseSearchInput(BaseModel):
    """
    搜索课程参数
    """
    keyword: str = Field(
        description="搜索关键词, 支持模糊匹配",
        min_length=1,
        max_length=50,
    )
    category: str = Field(
        default="all",
        description="课程类别: all(全部), frontend(前端), backend(后端), data(数据科学)",
        pattern=r"^(all|frontend|backend|data)$",   # 限定可选值
    )
    page: int = Field(
        default=1,
        description="页码, 从1开始",
        ge=1,
        le=100
    )

# 定义工具
@tool(args_schema=CourseSearchInput)
def search_course(keyword: str, category: str, page: int)->str:     # 注意, 这里参数部分可以直接改成input: CourseSearchInput, 这样子装饰器可以不指定参数模型
    """在xxx平台搜索课程"""
    return f"搜索 '{keyword}' (分类: {category}, 第 {page} 页)：共找到 15 条结果"

# 直接返回工具
@tool(return_direct=True)
def get_weather_direct(city:str)->str:
    """
    获取指定城市的天气情况

    当用户只需要搜索结果, 不需要额外分析时使用该工具
    Args:
        city: 城市名称, 如 北京, 上海等
    Returns:
        查询结果
    Examples:
        get_weather("北京") 返回 "北京天气晴, 温度25度"
    """
    # 上面这段关于工具的描述(docstring)是必要的, 因为在agent选择工具调用时, 这段的内容会被传输给LLM, LLM根据这段描述选择使用的工具
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
    
# 工具调用ID
@tool
def log_user_action(
    action: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
)->str:
    """
    记录用户的操作到日志系统中
    Args:
        action: 用户的操作描述
        tool_call_id: 系统自动注入的工具调用ID
    """
    # 这里将数据发送到日志服务
    # 注意, 这个工具本身没有任何业务, 在实际使用中, 应该是在业务工具中补充这个日志功能
    return f"操作已记录, (调用ID: {tool_call_id}): {action}"

# 工具异常
@tool
def get_user_info(user_id: int)->str:
    """
    根据用户的ID查询用户信息
    Args:
        user_id: 用户ID, 必须是正整数
    """
    # 数据校验
    if user_id<=0:
        # 抛出ToolException, 而不是普通的Exception
        raise ToolException(f"用户ID必须是正整数, 收到了{user_id}")
    # 模拟数据库查询
    users = {
        1: "张三(VIP 会员，注册于 2024-01-15)",
        2: "李四(普通用户，注册于 2024-03-20)",
    }
    # 未查询到异常
    if user_id not in users:
        raise ToolException(f"未找到ID为{user_id}的用户")
    return users[user_id]




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
    tools=[get_weather, search_course, get_weather_direct, log_user_action, get_user_info],
    system_prompt="""
...
""",
    # debug=True
)