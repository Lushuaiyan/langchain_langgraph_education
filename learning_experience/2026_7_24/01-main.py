from datetime import datetime
import json
import os
import math
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
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



# 长期记忆

# 记忆管理器
class MemoryManager:
    """
    记忆管理器
    """
    def __init__(self, storage_file: str = "conversation_memory.json"):
        self.storage_file = storage_file

    def save_conversation(self, session_id: str, messages: list):
        # 读取现有数据
        data = self._load_data()

        # 将消息转化成可序列化格式
        serialized_messages = []
        for msg in messages:
            serialized_messages.append(
                {
                    "type": msg.type,
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                }
            )

        # 保存
        data[session_id] = {
            "messages": serialized_messages,
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return

    def load_conversation(self, session_id: str)->list:
        data = self._load_data()

        if session_id not in data:
            return []

        # 转化为消息对象
        messages = []
        for msg_data in data[session_id]["messages"]:
            if msg_data["type"] == "human":
                messages.append(HumanMessage(content=msg_data["content"]))
            if msg_data["type"] == "ai":
                messages.append(AIMessage(content=msg_data["content"]))

        return messages

    def _load_data(self)->dict:
        if not os.path.exists(self.storage_file):
            return {}
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                return json.load(f)

        except:
            return {}

    def list_sessions(self)->list:
        data = self._load_data()
        return list(data.keys())

    def trim_messages(messages: list, max_messages: int = 20)->list:
        """
        上下文窗口, 保留最近的N条信息
        Args:
            messages: 完整的消息列表
            max_messages: 保留的最大消息数
        """
        if len(messages) <= max_messages:
            return messages

        # 始终保留系统消息
        system_messages = [msg for msg in messages if msg.type == "system"]
        other_messages = [msg for msg in messages if msg.type != "system"]

        # 保留最近的消息
        recent_messages = other_messages[-max_messages:]

        return system_messages + recent_messages

    def summarize_old_messages(model, messages: list)->str:
        """
        将旧消息总结成摘要
        ps: 这里之所以要传一个模型是因为通常这里使用更便宜的模型
        """
        # 提取旧对话
        old_conversation = "\n".join([
            f"{'你: ' if msg.type == 'human' else 'AI: '} {msg.content}"
            for msg in messages
        ])

        # 生成摘要
        summary_prompt = f"""
请总结以下对话的关键信息:
{old_conversation}
总结(包括用户信息, 重要事实, 待办事项):
"""
        summary = model.invoke(summary_prompt).content
        return summary


memory = MemoryManager()

print("持久化记忆助手")
print("="*60)

# 选择或创建会话
sessions = memory.list_sessions()
if sessions:
    print(f"\n现有会话: {', '.join(sessions)}")
    session_id = input("输入会话ID(或输入新ID创建会话): ").strip()
else:
    session_id = input("输入ID创建会话: ").strip()

# 加载历史会话
messages = memory.load_conversation(session_id)

if messages:
    print(f"\n 已加载 {len(messages)} 条历史消息")
    for msg in messages[-4:]:
        role = "你: " if msg.type == "human" else "AI: "
        print(f"{role} {msg.content[:50]}...")

else:
    print(f"\n 创建新会话: {session_id}")

print("\n输入 'quit' 退出\n")

# 对话循环
while True:
    user_input = input("你: ").strip()

    if user_input.lower() == 'quit':
        print("退出成功!")
        break
    messages.append(HumanMessage(content=user_input))
    resp = agent.invoke(input={"messages": messages})
    # 更新历史信息
    messages = resp["messages"]
    # 获取最后一条信息, 作为AI的回复
    last_message = messages[-1]
    if last_message.type == "ai":
        print(f"AI: {last_message.content}\n")

    # 保存
    memory.save_conversation(session_id, messages)