from langchain_community.document_loaders import (
    PyPDFLoader,        # PDF
    Docx2txtLoader,     # Word
    TextLoader,         # 纯文本
    DirectoryLoader     # 目录批量加载
)

from langchain_core.documents import Document

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter, # 递归分块
    CharacterTextSplitter, # 字符分块
    TokenTextSplitter # Token分块
)
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# 加载环境变量
load_dotenv()
EMBEDDING_API_KEY = os.getenv("QWEN_API_KEY")
EMBEDDING_URL = os.getenv("QWEN_URL")


embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    api_key=EMBEDDING_API_KEY,
    base_url=EMBEDDING_URL
)


# 加载PDF
pdf_loader = PyPDFLoader('路径')
pdf_docs = pdf_loader.load()

print(f"加载了 {len(pdf_docs)} 页 PDF")
print(f"第一页内容预览: {pdf_docs[0].page_content[:100]}...")

# 加载Word
docx_loader = Docx2txtLoader('路径')
docx_docs = docx_loader.load()

# 加载文本文件
text_loader = TextLoader('路径')
text_docs = text_loader.load()

# 批量加载
dir_loader = DirectoryLoader(
    '文件夹路径',
    glob='',        # 具体匹配的文件, 可以指定文件格式, 默认全选
    loader_cls=TextLoader,      # 使用哪个文档加载器
    loader_kwargs={"encoding": "utf-8"}     # 该加载器的具体参数配置
)

all_docs = dir_loader.load()
# 这是一个列表, 每个元素是对应文件加载后的结果

# Document数据格式
doc = Document(
    page_content="文档内容",
    metadata={
        "source": "文档来源",
        "page": 1, # 页码, 通常是pdf有
        "author": "张三",
        "date": "2026-7-28"
    },
    id=f"source-page"   # 唯一标识符
)


# ======================================分块========================================

# 递归分块
splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,       # 每块的字符数
    chunk_overlap = 50,     # 重合的字符数
    separators=["\n\n", "\n", "。", "！", "？", " ", ""]    # 分割的优先级
)


# 文本
# chunks = splitter.split_text(text="具体的文本内容")


# Document
# doc_chunks = splitter.split_documents(documents=["Document的列表"])

