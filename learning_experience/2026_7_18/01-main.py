from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

# 导入环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = os.getenv("DEEPSEEK_URL")

# 创建模型
model = init_chat_model(
    model="deepseek-v4-pro",
    model_provider="openai",
    configurable_fields=["streaming"],
    config_prefix="my",
    base_url=DEEPSEEK_URL,
    api_key=DEEPSEEK_API_KEY,
    streaming=False,
    #timeout=...,           超时时间
    #max_retries=...,       最大重试次数
    #temperature=...,       温度参数
)

# 调用
resp = model.invoke(
    input="你好",
    # config={
    #     "configurable":{
    #         "my_stream": True
    #     }
    # }
)

# 解析响应
print(resp.content)