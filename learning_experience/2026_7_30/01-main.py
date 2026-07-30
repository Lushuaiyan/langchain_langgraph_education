import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List
from langchain_core.documents import Document
import json
from datetime import datetime

load_dotenv()
# os.getenv("QWEN_API_KEY")  QWen和embedding的api_key和url
# os.getenv("QWEN_URL")

class KnowledeBase:
    """企业知识库系统"""
    def __init__(
            self,
            docs_directory: str = "./resource/rag_test",
            embedding_model: str = "BAAI/bge-m3",
            chat_model: str = "Qwen/Qwen3-8B"
    ):
        self.docs_directory = docs_directory


        # 初始化 Embedding
        print("正在加载模型...")
        self.embedding_model = OpenAIEmbeddings(
            base_url=os.getenv("QWEN_URL"),
            api_key=os.getenv("QWEN_API_KEY"),
            model=embedding_model
        )
        print("模型加载完成")

        # 文本分块器
        headers_to_split_on = [
            ("#", "Header1"),
            ("##", "Header2"),
            ("###", "Header3"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

        # 向量数据库
        print("\n正在创建数据库...")
        try:
            self.vectorstore = Chroma(
                collection_name="company_konwledge_store",
                embedding_function=self.embedding_model,
                persist_directory="./chroma_db"
            )
        except Exception as e:
            print(f"\t创建数据库失败: {e}")
            return False

        # LLM
        self.model = init_chat_model(
            chat_model,
            model_provider="openai",
            base_url=os.getenv("QWEN_URL"),
            api_key=os.getenv("QWEN_API_KEY"),
            temperature=0.0
        )

        # 查询历史
        self.query_log = []

    def build_store(self):
        print("\n开始构建知识库索引...")

        # 1. 加载文档
        print("\t正在加载文档...")
        loader = DirectoryLoader(
            self.docs_directory,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True
        )
        docs = loader.load()
        print(f"\t成功加载 {len(docs)} 个文档")

        if not docs:
            print("\t没有找到文档")
            return False

        # 2. 文本分块（保留元数据）
        print("\n正在分块...")
        all_chunks = []

        # 二级分割器（控制块大小）
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
        )

        for doc in docs:
            # 原始元数据（包含 source）
            original_metadata = doc.metadata.copy()

            # 按 Markdown 标题切分
            header_chunks = self.markdown_splitter.split_text(doc.page_content)

            # 为每个标题块补上原始元数据
            for chunk in header_chunks:
                chunk.metadata.update(original_metadata)

            # 二次切分（避免块过大）
            sub_chunks = recursive_splitter.split_documents(header_chunks)
            all_chunks.extend(sub_chunks)

        print(f"\t分块完成，共 {len(all_chunks)} 个文本块")

        # 3. 向量化并存入数据库
        print("\n正在向量化文档并存入数据库...")
        self.vectorstore.add_documents(all_chunks)
        print("向量化完成，文档已存入数据库中")
        return True

    def query(self, question: str, k: int = 3)->dict:
        """查询知识库"""
        if not self.vectorstore:
            return {"error": "知识库未初始化"}

        # 1. 检索相关文档
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=retriever,
            llm=self.model
        )
        docs = retriever_from_llm.invoke(question)

        # 2. 构建提示词
        prompt = ChatPromptTemplate.from_template("""
# 角色
你是企业知识库问答助手

# 任务
基于文档片段回答问题

# 文档片段
{context}

# 用户问题
{question}

# 回答要求
1. 仅基于提供的文档内容回答
2. 如果文档没有相关信息, 请明确告知用户
3. 回答要准确, 完整, 易懂
4. 如果答案来自多个文档片段, 请综合回答
""")

        # 3. 格式化文档
        def format_docs(docs:list[Document]):
            return "\n\n---\n\n".join([
                f"**文档 {i+1}**\n来源: {doc.metadata.get('source', '未知')}\n内容: {doc.page_content}"
                for i, doc in enumerate(docs)
            ])

        # 4. 构建 RAG Chain
        rag_chain = (
            {"context": lambda x: format_docs(docs), "question": RunnablePassthrough()}
            | prompt
            | self.model
            | StrOutputParser()
        )

        # 5. 生成答案
        answer = rag_chain.invoke(question)

        # 6. 记录查询
        self.query_log.append({
            "question": question,
            "answer": answer,
            "sources": [doc.metadata.get("source", "未知") for doc in docs],
            "timestamp": datetime.now().isoformat()
        })

        return {
            "question": question,
            "answer": answer,
            "sources": docs,
            "source_count": len(docs)
        }

    def export_logs(self, filename: str = "query_log.json"):
        """导出查询日志"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.query_log, f, ensure_ascii=False, indent=2)

        print("查询日志已导出到 {filename}")

def run_example():
    kb = KnowledeBase()

    # 构建数据库
    if kb.build_store():
        print("="*60)
        print("查询示例")
        test_question = [
            "公司制定规章制度的基本原则是什么",
            "员工离职的具体流程是怎样",
            "薪酬的具体组成是怎样, 什么时候发放",
            "公司有哪些奖励"
        ]
        for question in test_question:
            print(f"\n问题: {question}")
            resp = kb.query(question)
            print(f"回答: {resp["answer"]}")
            print(f"参考文档: {', '.join([doc.metadata['source'] for doc in resp['sources']])}")
        print("="*60)
        kb.vectorstore.delete(ids=kb.vectorstore.get()['ids'])
        # 结束后删除数据库的数据, 否则每次运行该程序都会加入重复内容
    else:
        print("数据库构建失败")


    return

if __name__=="__main__":
    run_example()
