import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings

# 加载环境变量
load_dotenv()
EMBEDDING_API_KEY = os.getenv("QWEN_API_KEY")
EMBEDDING_URL = os.getenv("QWEN_URL")

# 将文本转化成向量
embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    api_key=EMBEDDING_API_KEY,
    base_url=EMBEDDING_URL
)

text = "这是一段测试文本"
vector = embeddings.embed_query(text)

print(f"文本:{text}")
print(f"向量维度:{len(vector)}")
print(f"向量的前五个值:{vector[:5]}")

# 使用这个模型, 计算向量的维度是1024