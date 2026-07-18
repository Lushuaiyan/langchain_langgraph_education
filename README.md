# 引言
**langchain**和**langgraph**都是一种AI agent框架, 他们的使用方式不同, 适合的场景也不同

但是, 因为**langchain**比**langgraph**更早诞生, 后者常常包含许多前者的内容, 因此学习时也最好先学习这部分

这个项目的目的就是按照日期, 一步一步的学习并融汇贯通其中的内容

# langchain
安装langchain包非常简单
```bash
uv add langchain
```
注意, 在安装langchain时, 默认也会安装langgraph

如果还有其它定制化需求, 还可以安装`langchian-openai`, `langchain-community`
他们分别是不同模型, 社区提供的定制服务

所有的包都是基于最基础的`langchian-core`包实现的, 它是langchian实现的核心抽象层