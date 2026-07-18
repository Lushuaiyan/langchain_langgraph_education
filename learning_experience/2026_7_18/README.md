# 使用模型

1. 安装
安装了三个包
```bash
uv add langchain langchain-openai dotenv
```
这三个包的作用是:
- langchain: 框架的基础内容
- langchain-openai: 框架本身不提供模型的服务, 国内大多数模型都兼容openai的集成
- dotenv: 注入环境变量

2. 创建模型
```python
from langchain.chat_models import init_chat_model
model= init_chat_model(
    model: str,                             # 这里推荐使用模型提供商+模型的形式, 如: openai: gpt-4o
    *,
    model_provider: str | None = None,      # 如果模型没有写提供商, 可以在这里写
    configurable_fields: None = None,       # 定义参数白名单, 可以在对话中修改这些参数的数值
    config_prefix: str | None = None,       # 命名空间前缀, 方便扩展命名空间
    **kwargs: Any                           # 根据不同模型输入不同的参数
)
```
**注意**: 这里创建模型中没有url和apikey, 这些内容写在`**kwargs`中, 如果没有, 默认根据模型提供商读取环境变量中的apikey(只有国外的模型可以使用)

3. 调用模型
调用模型获取回答由三种形式, 且都有一个异步版本:
- invoke/ainvoke: 单次同步调用, 等待完整结果
- stream/astream: 流式处理, 逐个产生结果片段
- batch/abatch: 批量处理, 并行指定多个调用
```python
resp = model.invoke(
    input: LanguageModelInput,              # 这里输入给模型的提示词
    config: RunnableConfig | None = None,   # 这里写需要修改的参数的数值
    **kwargs: Any                           # 根据不同模型输入不同的参数
)
```
**注意**: 关于其中的input, 有三种输入方式:
- **纯文本格式**: 相当于直接问模型问题
- **json格式**: 使用json输入系统提示词和用户提示词
- **Message对象格式**: 这是兼容旧框架的格式, 基本使用json格式平替

4. 解析响应
得到的响应数据主要是模型回复的内容和其它额外的参数
重点是回复内容, 在`resp.content`中, 其它参数在`resp.additional_kwargs`中
如果使用的是流式输出, 参考下列方式
```python
for chunk in model.stream(question):
    print(chunk.content, end="", flush=True)
```