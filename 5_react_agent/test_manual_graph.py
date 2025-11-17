from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from react_graph_manual import app

load_dotenv()

# 그래프 구조 출력
print("=== 그래프 구조 ===\n")
print(app.get_graph().draw_mermaid())

# Messages 기반으로 실행
query = "How many days ago was the latest SpaceX launch?"
messages = [HumanMessage(content=query)]

print("\n=== ReAct Agent 실행 (수동 구현) ===\n")

# 스트리밍으로 상세 과정 보기
for step in app.stream({"messages": messages}):
    for node, data in step.items():
        print(f"\n[{node}]")
        if "messages" in data:
            for msg in data["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        print(f"  도구 사용: {tool_call['name']}")
                        print(f"  입력: {tool_call['args']}")
                elif hasattr(msg, "name") and msg.name:
                    print(f"  도구 결과: {msg.content[:200]}...")
                elif msg.content and not hasattr(msg, "tool_calls"):
                    print(f"  최종 답변: {msg.content}")

# 최종 결과 출력
result = app.invoke({"messages": messages})
print("\n=== 최종 결과 ===")
print(result["messages"][-1].content)
