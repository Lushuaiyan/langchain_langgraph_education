import os
import json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from datetime import datetime
from typing import Optional

load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL")

# ========================= 数据管理 ==========================
class CustomerDatabase:
    """客户数据库(模拟)"""
    def __init__(self):
        # 这里记录用户的数据, 实际项目中这些数据应该是从数据库中存取
        self.customers = {
            "user001": {
                "name": "张三",
                "level": "VIP",
                "phone": "123****1234",
                "email": "zhangsan@example.com"
            },
            "user002": {
                "name": "李四",
                "level": "普通会员",
                "phone": "128****1834",
                "email": "lisi@example.com"
            }
        }
        self.orders = {
            "user001": [
                {"order_id": "ORD001", "product": "iPhone 15", "status": "已发货", "date": "2025-7-14"},
                {"order_id": "ORD002", "product": "AirPods Pro", "status": "已送达", "date": "2025-9-4"},
            ],
            "user002": [
                            {"order_id": "ORD003", "product": "MacBook Pro", "status": "已发货", "date": "2026-3-14"},
                        ]
        }

    def get_customer(self, user_id: str)->Optional[dict]:
        """获取客户信息"""
        return self.customers.get(user_id)

    def get_orders(self, user_id: str)->list:
        """获取客户订单"""
        return self.orders.get(user_id, [])

class ConversationStorage:
    """对话储存"""
    def __init__(self, storage_file: str = "customer_service_history.json"):
        self.storage_file = storage_file

    def save(self, user_id: str, session_id: str, messages: list, metadata: dict = None):
        """保存对话"""
        data = self._load()

        if user_id not in data:
            data[user_id] = {}

        serialized = []
        for msg in messages:
            serialized.append(
                {
                    "type": msg.type,
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                }
            )

        data[user_id][session_id] = {
            "messages": serialized,
            "metadata": metadata or {},
            "update_at": datetime.now().isoformat()
        }

        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # 这里模拟逻辑是直接存文件, 而且写入时是将所有数据全部写入, 这是浪费很多时间的
        # 实际项目中必须使用数据库存储, 将不同用户的对话信息分开保存
        return

    def load(self, user_id: str, session_id: str)->str:
        data = self._load()
        if user_id not in data or session_id not in data[user_id]:
            return []
        messages = []
        for msg_data in data[user_id][session_id]["messages"]:
            if msg_data["type"]=="human":
                messages.append(HumanMessage(content=msg_data["content"]))
            if msg_data["type"]=="ai":
                messages.append(AIMessage(content=msg_data["content"]))
            if msg_data["type"]=="system":
                messages.append(SystemMessage(content=msg_data["content"]))

        return messages

    def list_sessions(self, user_id: str)->list:
        data = self._load()
        if user_id not in data:
            return []
        return list(data[user_id].keys())

    def _load(self)->dict:
        if not os.path.exists(self.storage_file):
            return {}
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

# ============================== 工具定义 ========================
db = CustomerDatabase()

@tool
def get_customer_info(user_id: str)->str:
    """
    获取客户信息

    Args:
        user_id: 客户ID, 如 user001等
    """
    customer = db.get_customer(user_id)
    if not customer:
        return f"未找到客户 {user_id} 的信息"
    return f"""
客户信息:
    姓名: {customer['name']}
    会员等级: {customer['level']}
    电话: {customer['phone']}
    邮箱: { customer['email']}
"""


@tool
def query_orders(user_id: str)->str:
    """
    查询客户订单

    Args:
        user_id: 客户ID, 如 user001等
    """
    orders = db.get_orders(user_id)
    if not orders:
        return f"客户 {user_id} 暂无订单记录"
    result = f"客户 {user_id} 的订单记录: \n\n"
    for order in orders:
        result += f"订单号: {order['order_id']}\n"
        result += f"商品: {order['product']}\n"
        result += f"状态: {order['status']}\n"
        result += f"下单时间: {order['date']}\n"
        result =+ '-'*40 + '\n'

    return result

@tool
def get_order_status(order_id: str)->str:
    """
    查询订单状态

    Args:
        order_id: 订单号, 如 ORD001等
    """
    for user_id, orders in db.orders.items():
        for order in orders:
            if order['order_id'] == order_id:
                return f"""
订单 {order_id} 状态:
    商品: {order['product']}
    状态: {order['status']}
    下单时间: {order['date']}
    {'预计明天到达' if order['status'] == '已发货' else ''}
"""

    return f"未找到订单 {order_id}"

@tool
def create_ticket(user_id: str, problem: str)->str:
    """
    创建客服工单
    
    当客户问题无法立即解决时, 创建工单记录

    Args:
        user_id: 客户ID
        problem: 问题描述
    """
    ticket_id = f"TICKET_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 模拟创建工单
    return f"""
已为您创建工单:
    工单号: {ticket_id}
    问题: {problem}
    状态: 待处理

我们工作人员会在 24 小时内联系您, 感谢您的耐心等待!
"""

@tool
def search_knowledge_base(keyword: str)->str:
    """
    搜索知识库

    Args:
        keyword: 搜索关键词
    """
    # 模拟知识库
    knowledge = {
        "退货": "退货政策: \n1. 7天无理由退货\n2. 商品需保持完整\n3. 提供订单号和退货原因",
        "发票": "发票申请: \n1. 登录账号\n2. 进入订单详情\n3. 点击申请发票并填写信息",
        "配送": "配送说明: \n1. 全国包邮(偏远山区除外)\n2. 一般3-5个工作日内送达"
    }

    for key, value in knowledge.items():
        if keyword in key:
            return value

    return f"未找到关于 {keyword} 的相关信息, 请联系人工客服"


# ==================================客服机器人 ==================================

class CustomerServiceBot:
    """
    智能客服机器人
    """
    def __init__(self):
        # 初始化模型
        self.model = init_chat_model(
        model="Qwen/Qwen3-8B",
        model_provider="openai",
        base_url=QWEN_URL,
        api_key=QWEN_API_KEY,
        # streaming=True
        )
        # 工具列表
        self.tools = [
            get_customer_info,
            query_orders,
            get_order_status,
            create_ticket,
            search_knowledge_base
        ]
        # 系统提示词
        system_prompt = """
# 人设
你是一个专业的客服助手

# 任务
1. 礼貌友好地回答客户问题
2. 使用工具查询订单, 客户信息
3. 解答常见问题(退货, 发票, 配送等)
4. 无法解决问题时创建工单

# 工作流程
1. 首先确认客户身份(询问客户ID或订单号)
2. 了解客户问题
3. 使用合适的工具查询信息或解决问题
4. 使用通俗易懂的语言回复客户
5. 如果无法解决, 创建工单

# 注意事项:
1. 始终保持专业和礼貌
2. 回答要准确, 不要编造信息
3. 如果不确定, 建议联系人工客服
4. 记住对话历史中的客户信息

请始终使用中文
"""

        # 创建agent
        self.agent=create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=system_prompt
        )

        # 存储
        self.storage = ConversationStorage()

        # 当前会话
        self.current_user = None
        self.current_session = None
        self.messages = []

    def start_session(self, user_id: str, sessiong_id: str = None):
        """开始会话"""
        self.current_user = user_id
        self.current_session = sessiong_id or f"session {datetime.now().strftime('%Y%m%d%H%M%S')}"

        # 加载历史对话
        self.messages = self.storage.load(user_id, self.current_session)

        if not self.messages:
            # 新会话
            welcome = f"您好, 我是智能客服助手, 请问有什么可以帮助您的?"
            self.messages.append(AIMessage(content=welcome))

        return

    def chat(self, user_input: str)->str:
        """对话"""
        # 添加用户消息
        self.messages.append(HumanMessage(content=user_input))

        # 调用agent
        resp = self.agent.invoke({"messages": self.messages})
        self.messages = resp['messages']

        # 自动保存
        self.storage.save(self.current_user, self.current_session, self.messages)

        # 返回AI回复
        for msg in reversed(self.messages):
            if msg.type == 'ai' and msg.content:
                return msg.content
        return "抱歉, 我暂时无法处理您的请求"

    def end_session(self):
        """结束会话"""
        self.storage.save(
            self.current_user,
            self.current_session,
            self.messages,
            metadata={"ended_at": datetime.now().isoformat()}
        )



# ===================== 主程序 ========================

def main():
    bot = CustomerServiceBot()

    print('='*60)
    print("智能客服机器人")
    print('='*60)

    # 用户身份
    print("\n请输入您的客户ID(测试账号:user001 或 user002)")
    user_id = input("客户ID: ").strip() or "user001"

    # 检查历史会话
    sessions = bot.storage.list_sessions(user_id)
    if sessions:
        print(f"您有 {len(sessions)} 个历史会话")
        print("会话列表: ", ", ".join(sessions[-3:]))
        choice = input("\n继续上次会话?(y/n): ").strip().lower()
        if choice == 'y':
            session_id = sessions[-1]
            print(f"继续会话: {session_id}")

        else:
            session_id = None
            print("开启新会话")
    else:
        session_id = None
        print(f"\n欢迎新客户: {user_id}")

    # 开始会话
    bot.start_session(user_id, session_id)

    # 显示欢迎消息
    if bot.messages:
        print(f"\nAI: {bot.messages[-1].content}\n")

    print("输入 quit 结束会话\n")

    # 会话循环
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == 'quit':
            bot.end_session()
            print(f"\n对话已保存")
            break

        if not user_input:
            continue
        resp = bot.chat(user_input)
        print(f"\nAI: {resp}")

if __name__ == "__main__":
    main()