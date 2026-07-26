import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

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

# 创建Chroma向量数据库(本地文件)
vector_store = Chroma(
    collection_name="test_store",
    embedding_function=embeddings,
    persist_directory="./chroma_db", # 持久化目录
)
# 类比SQL
# 这里的持久化目录相当于数据库
# 名字相当于数据表
# 每次操作时都是在对指定的数据表操作(增删改查)
# 多个脚本的向量数据可以在同一个目录下, 只要名字不同, 就互不干扰(相同就是同一个表了)



# 添加文档
texts = [
    "张三最喜欢的水果是哈密瓜",
    "李四曾经杀过人，被判了 20 年",
    "王五有一个幸福的家庭，有一个爱他的妻子和3个孩子"
]

# 删除集合中所有数据
vector_store.delete(ids=vector_store.get()['ids'])

# add_texts 自动将文本转化成向量并存储
vector_store.add_texts(texts)

# 注意: 
# 如果多次运行这个脚本, 相同的文本会多次重复添加到向量库中
# 因为向量库是根据主键id去重的, 这里没有指定id, 所以每次都会当作新的文本添加到数据库中
# 真实使用中需要基于文本内容生成md5或基于业务字段使用uuid等方式控制ids, 避免重复添加
# 或者结合元数据, 将ids设置为 文档来源+页码 

# 语义检索
results = vector_store.similarity_search(
    query="王五有几个孩子",
    k=2, # 返回两个最相似的结果
)

# # 检索器
# retriever = vector_store.as_retriever(
#     search_type="similarity", # 相似度搜索
#     search_kwargs={"k": 3}, # 返回前3个结果
# )

# # 使用检索器
# docs = retriever.invoke("王五有几个孩子")

# 使用检索器的方式可以提前设置好基础配置, 使用时只需输入文本即可


print("搜索结果: ")
for i, doc in enumerate(results):
    print(f"\n结果{i+1}:")
    print(f"内容: {doc.page_content}")
    print(f"元数据: {doc.metadata}")