# 文档处理
使用rag时需要将文本处理好后在存入向量数据库中

处理流程有两步:
加载->切分

## 1. 加载
langchain要将不同文件转化成统一的格式: `Document`

`Document`格式:
- page_content: str
    > 核心内容, 存储文档的实际文本内容
- metadata: dict
    > 元数据, 存储与文档相关的辅助信息
- id: str
    > 唯一标识符, 文档的可选唯一id

常见的加载器有:
1. TextLoader: 纯文本加载器, 通常是整个文本在page_content中
2. PyPDFLoader: pdf加载器, 自动分页, 每页单独作为一个Document
3. CSVLoader: 表格加载器, 每行作为一个Document
4. Docx2txtLoader: Word加载器, 整个文本在page_content中


## 2. 切分
langchain中将文件切分的方式通常是`RecursiveCharacterTextSplitter`
传入一个列表， 就可以递归切分其中的所有文档

在该切分器的逻辑中, 会优先将文本根据"\n\n"切分, 如果长度都满足, 就返回, 否则将超出范围的拎出来使用下一级切分, 直到全部满足要求

重叠部分的逻辑是滑动窗口, 不是拼接, 所以每块的增量最多是`chunk_size`-`chunk_overlap`
> 注意: 因为英文和中文的字符不同， 所以通常中文文档和英文文档要用两种切分器


## 3. 向量化
直接使用langchain自带的向量化框架虽然可以, 但是还需要自己定义计算相似度的方法
所以推荐直接和Chroma一起使用, 该库有做和langchain的兼容, 可以使用Document数据