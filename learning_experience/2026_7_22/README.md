# tool装饰器的多种用法

## 1. 直接使用
直接使用`@tool`, 声明一个函数是工具, 可以直接调用
无法实现很多复杂的功能

## 2. 使用args_schema
对于工具的输入参数有具体要求, 而docstring无法满足所有需求, 可以使用args_schema参数处理
使用pydantic可以对每个参数做出具体的限制和描述, 能够让agent更好的使用该工具

## 3. 使用return_direct
在有些情况下, 工具的输出结果就是我想要的结果, 不需要模型进行总结了, 可以通过设置return_direct, 在执行该工具后立刻结束, 将工具内容作为最终输出

Agent 会跳过后续的模型思考步骤, 直接返回工具结果, 这在节省 Token 和降低时延方面非常有价值, 但也意味着模型不会对工具结果做任何二次加工

>注意：如果一个 Agent 同时挂载了多个工具，其中既有 return_direct=True 的工具，也有普通工具，那么只要模型在这一轮调用中触发了任意一个 return_direct 工具，Agent 循环就会立即结束——即使同一轮还并行调用了其他普通工具，它们的结果也不会再被模型加工总结。设计包含多个工具的 Agent 时要留意这一点，避免"该总结的内容被跳过"。

## 4. 获取工具调用ID
有时工具需要知道"是谁调用了它"——InjectedToolCallId 可以在工具函数中注入当前的 tool_call_id

虽然在参数中写了, 但agent在调用时不会生成id, 而是自动注入的方式处理

## 5. 工具异常处理
工具执行过程中可能会出错, 使用 ToolException 抛出明确的工具异常, 让 Agent 知道出了问题

虽然agent知道了发生错误, 但是agent不能自己处理, 所以最后还是会抛出异常(不是调用工具时抛出异常, 而是在对话时抛出异常, 如invoke等)

> 现在使用的tool装饰器是`langchain_core.tools.tool`, 但在最初有`langchain.tools.tool`这个装饰器(基本弃用), 其中在异常处理部分是有一个参数"handle_tool_error"的, 它能够将工具的异常信息转化成字符串发送给agent, 但在现在的tool装饰器中不适用, 如果需要, 可以直接使用`try...except`语句return错误信息, 或者使用更底层的创建工具的方式`StructuredTool.from_function`, 这个底层工具具有更多功能