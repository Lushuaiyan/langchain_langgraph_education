# agent的定义与使用

## 1. 定义工具
绝大多数的agent的工具都是`function calling`
根据ReAct架构, 思考->执行->观察->思考 的循环
在执行阶段, 如果需要使用工具, 本质上不是模型自己运行了这个工具
而是根据之前传给模型的工具信息, 生成对应的参数
而后电脑根据参数执行代码, 最后将返回传递给模型, 作为这一次执行后的结果

在langchain中, 定义工具需要使用`langchain_core.tools`中的tool装饰器定义
且工具下的文档必须详细描述该工具的作用, 参数, 返回, 示例(最好有)
给文档会和提示词一起发送给LLM, LLM根据这些文档选择使用的工具

使用tool装饰器有许多好处:
- 自动上传工具文档
- 自动返回工具执行结果作为模型的执行结果

## 2. 定义agent

```python
agent = create_agent(
    model=...,                  # 这里的模型必须是使用init_chat_model创建出来的模型
    tools=...,                  # 这是关于工具的列表, 所有工具必须使用`@tool`装饰器包裹, 这里会将所有工具的文档作为提示词一起发送给LLM
    *,
    system_prompt=...,          # 这里可以传入agent的提示词
    interrupt_before=...,       # 传入工具列表, 告诉LLM在使用哪些工具前需要暂停
    interrupt_after=...,        # 传入工具列表, 告诉LLM在使用哪些工具后需要暂停
    debug=...                   # 调试模式, 查看详细信息
)
```
> 关于系统提示词部分, 其实在模型部分也有, 是在使用invoke等交互是作为信息的一部分传递的
> 这里就体现了agent和普通的LLM的不同, 一个agent的系统提示词通常是持久化的, 不变的
> 因此在交互之前就设定好了系统提示词, 而不是像LLM一样, 每次对话都要设置系统提示词

## 3. 使用agent
agent和model差不多, 都是使用invoke, stream等方法交互
但是有一个不同之处是其中的input参数
原model可以有三种处理方式: 纯文本, 消息对象列表, 字典列表
但是在agent中, 必须传入字典, 格式如下
```python
input = {"messages": [消息对象列表或字典列表]}
```
> 这里就体现了model和agent的不同之处, model是执行者, agent是管理者
> 因为一个问题在agent中常常不是一次问答就可以解决的, 所以agent必须维护上下文的状态
> "messages"这个key就是管理对话的方式(后续有记忆的内容就可以append到里面)

且agent的返回结果也和model有很大的不同
`resp["messages"][-1].content`, 能体现响应的结构, 可以从中获取更多详细内容

如果是流式输出也有很多不同之处
```python
for chunk in agent.stream(input={"messages": [{"role": "user", "content": question1}]}):
    print(chunk)
    print("-"*100)
```
如果直接运行上面的代码, 会发现实际上在agent中, chunk的划分不是按照token划分的(一个字一个字的生成), 而是每个步骤分为一个chunk(工具调用, 最终回答等)
所以, 想要真正做到流式输出需要使用以下方式:
`steam_mode`: 通过设置流式输出的模式, 使得流式输出回到正常(按照token划分), 划分的内容是你选择的目标内容
```python
for chunk, metadata in agent.stream(
    input={"messages": [{"role": "user", "content": question1}]},
    stream_mode="messages"
    ):
    if hasattr(chunk, 'content') and chunk.content:
        print(chunk.content, end="", flush=True)
```
其中会有关于工具的响应的内容, 如果不需要, 使用metadata将它们过滤掉就可以了
```python
if metadata.get('langgraph_node') == 'tools':   # 这是使用langgraph的内容
    continue
if hasattr(chunk, 'tool_calls') and chunk.tool_calls:   # 这是agent中有tool响应的内容
    continue
```
这样得到的就是响应的流式输出了