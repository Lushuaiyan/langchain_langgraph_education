import json
import os
import math
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# 环境变量导入
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL")

# 定义参数模型
class SearchParams(BaseModel):
    keyword: str = Field(description="搜索关键词")
    category: Optional[str] = Field(default=None, description="分类筛选")
    max_results: int = Field(default=5, description="最大结果数量")

# 定义工具

# 输入参数为参数模型的工具
@tool
def advanced_search(params: SearchParams)->str:
    """
    高级搜索功能
    支持关键词搜索, 分类筛选, 结果数量限制

    Args:
        params: 搜索参数对象
    """
    result = f"搜索 '{params.keyword}\n'"
    if params.category:
        result += f"在分类 '{params.category}' 中\n"
    result += f"返回前 {params.max_results} 条结果"
    return result

# 输出结果为参数模型(json)的工具
@tool
def get_product_info(product_id: str)->str:
    """
    获取产品的详细信息

    Args:
        product_id: 产品的ID
    Returns:
        JSON 格式的产品信息
    """
    # 模拟产品信息
    products = {
        "P001": {
            "name": "iPhone 15",
            "price": 5999,
            "stock": 100,
            "rating": 4.8
        },
        "P002": {
            "name": "MacBook Pro",
            "price": 12999,
            "stock": 50,
            "rating": 4.9
        },
    }
    product = products.get(product_id, {"error": "产品不存在"})
    return json.dumps(product, ensure_ascii=False)

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
    tools=[advanced_search, get_product_info],
    system_prompt="""
...
""",
    # debug=True
)