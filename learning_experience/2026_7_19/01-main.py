import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


# 导入环境变量
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_URL = os.getenv("QWEN_URL")

# 定义智能翻译类
class SmartTranslator():
    def __init__(self):
        self.model = init_chat_model(
            model="Qwen/Qwen3-8B",
            model_provider="openai",
            base_url=QWEN_URL,
            api_key=QWEN_API_KEY,
            temperature=0.3
        )

    def translate(self, text: str, target: str = "中文", style: str = "正式"):
        """
        将文本翻译成指定的语言, 并可以规定翻译的风格
        Args:
            text:需要翻译的文本
            target:翻译的目标语言
            style:翻译的风格
        """
        system_prompt = f"""
# 人设
你是一个专业的翻译助手
# 任务
1. 自动检测输入文本的语言
2. 将该文本翻译成{target}
3. 使用{style}风格
4. 如果有专有名词, 在翻译后标注原文和解释
# 输出格式
<原文>: xxx
<翻译>: xxx
<术语解释>: xxx(如果有)
"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=text)
        ]
        resp = self.model.invoke(messages)
        return resp.content
    

def main():
    # 初始化翻译模型
    translator = SmartTranslator()

    # 单次调用
    # print("智能翻译助手")
    # print("="*30)
    # text = "I always hear about my friends' plaining, they say their ine is such low that they can't not make ends meet. At first, I would pity for them, but in the long run, I find their work is so easy, they just sit in the office from 9 am to 5 pm, they even don't need to go out for business. While I see another friend, he works so hard, his working hour is very unstable, sometimes he even works until 9 pm. The fact is that he earns the most between my friends. It is true that no pain, no gain, if people want more, they need to pay out more. Comparing to be envy about other people's great ine, we'd better to work hard to realize what we want. There is not short-cut for people to get successful, working hard is the only way."
    # translated_text = translator.translate(text)

    # print(f"翻译结果:\n{translated_text}")

    # 交互模式
    print("进入交互模式(输入 'quit' 退出)")
    while True:
        text = input("请输入您需要翻译的文本:\n").strip()
        if text.lower() == "quit":
            print("退出成功, 欢迎下次使用")
            break
        elif text is None:
            print("输入文本不能为空, 请重新输入")
            continue
        else:
            target = input("请输入翻译的目标语言(默认中文):\n").strip() or "中文"
            style = input("请输入翻译的风格(正式, 口语, 文学等, 默认正式):\n").strip() or "正式"
            print("翻译中...")
            translated_text = translator.translate(text, target, style)
            print("="*30)
            print(f"翻译结果: \n{translated_text}")
            print("="*30)

if __name__ == "__main__":
    main()