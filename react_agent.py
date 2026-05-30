from openai import OpenAI
from tools import explore_path, solve_input
import os

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

system_prompt = """
你是一个逆向分析Agent。

目标：
找到能够输出

Success! Flag is found.

的输入。

避免进入：

trapped
dead loop

相关路径。

可用工具：

1. explore_path
2. solve_input
3. finish

规则：

如果 Observation 中出现：

SUCCESS_STATE_FOUND=True

则下一步必须调用：

Action: solve_input

如果 Observation 中出现：

INPUT_FOUND=

则下一步必须调用：

Action: finish

输出格式必须严格遵守：

Thought: 你的思考
Action: explore_path

或者

Thought: 你的思考
Action: solve_input

或者

Thought: 你的思考
Action: finish
"""

messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": """
开始分析目标程序。
"""
    }
]

simgr = None

for round_id in range(10):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0
    )

    reply = response.choices[0].message.content.strip()

    print("\n====================")
    print(f"Round {round_id + 1}")
    print("====================")
    print(reply)

    messages.append({
        "role": "assistant",
        "content": reply
    })

    if "Action: explore_path" in reply:

        simgr = explore_path("./crackme")

        obs = f"""
SUCCESS_STATE_FOUND={len(simgr.found) > 0}
FOUND_STATES={len(simgr.found)}
"""

    elif "Action: solve_input" in reply:

        result = solve_input(simgr)

        if result is None:
            obs = "ERROR=NO_FOUND_STATE"
        else:
            clean = result.decode(errors="ignore").strip()

            obs = f"""
INPUT_FOUND={clean}
"""

    elif "Action: finish" in reply:

        print("\nTask Finished")
        break

    else:

        obs = """
ERROR=INVALID_ACTION
"""

    print("\nObservation:")
    print(obs)

    messages.append({
        "role": "user",
        "content": obs
    })
